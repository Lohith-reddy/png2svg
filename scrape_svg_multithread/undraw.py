import os
import threading
from multiprocessing import Queue
import importlib

from utils import get_soup, download_img

import re
from json import loads
from dotenv import load_dotenv
import yaml

load_dotenv()
yaml_data = yaml.safe_load(open("config.yaml", 'r'))


class UnDraw(threading.Thread):

    def __init__(self):
        super(UnDraw, self).__init__()
        self.page_ext = yaml_data["ENVIRONMENT_VARIABLES"]["PAGE_EXT"]

    def get_svg(self, pagecount=0):
        svg = []
        names = []
        download_dict = {}
        url = yaml_data["ENVIRONMENT_VARIABLES"]["WEBSITE_URL"]
        if pagecount == 0:
            url = url
            for link_1 in get_soup(url).find_all('div', yaml_data["ENVIRONMENT_VARIABLES"]["CLASS_NAME_SVG"]):
                link_1 = str(link_1)
                svg.append(re.search(r'data-src="([^"]*)', link_1).group(1))
            for link_2 in get_soup(url).find_all('div', yaml_data["ENVIRONMENT_VARIABLES"]["CLASS_NAME_TITLE"]):
                link_2 = str(link_2)
                names.append(link_2.split(">")[1].split("<")[0])
        else:
            url = yaml_data["ENVIRONMENT_VARIABLES"]["SECOND_URL"]
            url = url + self.page_ext + str(pagecount)
            link = get_soup(url)
            link = str(link)
            link = loads(link)
            for obj in range(len(link["illos"])):
                svg.append(link["illos"][obj]["image"])
                names.append(link["illos"][obj]["title"])

        for i in range(len(svg)):
            download_dict[names[i]] = svg[i]

        print(f"page {pagecount} yielded ", len(set(download_dict)), " images \n")
        return download_dict


class DownloadScheduler(threading.Thread):
    def __init__(self, input_queue, **kwargs):
        super(DownloadScheduler, self).__init__()
        self.queue = input_queue
        self.start()

    def run(self):
        print("Starting Download")
        while True:
            val = self.queue.get()
            if val == "DONE":
                break

            title = download_img(val)


class ScrapeScheduler(threading.Thread):
    def __init__(self, input_queue, **kwargs):
        super(ScrapeScheduler, self).__init__()
        self.queue = input_queue
        self.pagecount = int(kwargs["pagecount"])
        self.download_q = kwargs["output_q"]
        self.thread_count = yaml_data["WORKERS"]["DOWNLOAD_WORKER"]["THREAD_COUNT"]
        self.start()

    def run(self):
        print("Starting Scrape of page: ", self.pagecount, "\n")
        und = getattr(importlib.import_module(yaml_data["CLASSES"]["LOCATION"],
                                              yaml_data["CLASSES"]["NAME"]))
        download_schedulers_list = []
        while True:
            val = self.queue.get()
            if val == "DONE":
                # when the scraper q gets empty it will send "DONE" signals to the download_q,
                # and we join all the download threads
                for i in range(len(download_schedulers_list)):
                    self.download_q.put("DONE")

                for i in range(len(download_schedulers_list)):
                    download_schedulers_list[i].join()
                # scheduler.download()
                break

            for i in range(self.thread_count):
                print("Initializing download thread: ", i, "\n")
                scheduler = DownloadScheduler(self.download_q)
                download_schedulers_list.append(scheduler)

            for i, j in und.get_svg(self.pagecount).items():
                self.download_q.put((i, j))
                print("Added to download queue: ", i, "\n")


def main():
    download_q = Queue()
    scrape_q = Queue()
    scraper_schedulers_list = []

    # initialize 10 threads for downloading and scraping

    # initializing scraping
    for pagecount in range(0, int(os.getenv("PAGE_COUNT"))):
        for j in range(int(os.getenv("SCRAPER_THREAD_COUNT"))):
            print("Initializing scraper thread: ", j, "\n")
            scheduler = ScrapeScheduler(scrape_q, pagecount=pagecount, output_q=download_q)
            scraper_schedulers_list.append(scheduler)

        # download queue is initialised inside scrape queue
        scrape_q.put(pagecount)

        for i in range(len(scraper_schedulers_list)):
            scrape_q.put("DONE")

        for i in range(len(scraper_schedulers_list)):
            scraper_schedulers_list[i].join()


if __name__ == "__main__":
    main()
    print(len(os.listdir("images/")))
