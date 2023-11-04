import os
import threading
from multiprocessing import Queue

import requests
from bs4 import BeautifulSoup as bs
import re
from json import loads
from dotenv import load_dotenv

load_dotenv()


def download_img(tup):
    title, img = tup
    title = "images/" + title + ".svg"
    with open(title, 'wb') as file:
        file.write(requests.get(img).content)
        file.close()
    print("Downloaded:", title,"\n")
    return title


def get_soup(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error: ", response.status_code)
        return None
    else:
        response = requests.get(url).text
        links = bs(response, "html.parser")
    return links


class UnDraw(threading.Thread):

    def __init__(self):
        super(UnDraw, self).__init__()
        self.page_ext = "?page="

    def get_svg(self, pagecount=0):
        svg = []
        names = []
        download_dict = {}
        url = os.getenv("WEBSITE_URL")
        if pagecount == 0:
            url = url
            for link_1 in get_soup(url).find_all('div', "ClassicGrid__Media-sc-td9pmq-2 ffqsDq"):
                link_1 = str(link_1)
                svg.append(re.search(r'data-src="([^"]*)', link_1).group(1))
            for link_2 in get_soup(url).find_all('div', "ClassicGrid__Content-sc-td9pmq-3 jCxkJm"):
                link_2 = str(link_2)
                names.append(link_2.split(">")[1].split("<")[0])
        else:
            url = os.getenv("SECOND_URL")
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
    def __init__(self, queue):
        super(DownloadScheduler, self).__init__()
        self.queue = queue
        self.start()

    def run(self):
        print("Starting Download")
        while True:
            val = self.queue.get()
            if val == "DONE":
                break
            title = download_img(val)


class ScrapeScheduler(threading.Thread):
    def __init__(self, queue, pagecount=0, download_q=None):
        super(ScrapeScheduler, self).__init__()
        self.queue = queue
        self.pagecount = pagecount
        self.download_q = download_q
        self.start()

    def run(self):
        print("Starting Scrape of page: ", self.pagecount, "\n")
        und = UnDraw()
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
            for i in range(int(os.getenv("DOWNLOAD_THREAD_COUNT"))):
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
    for page in range(0, int(os.getenv("PAGE_COUNT"))):
        for j in range(int(os.getenv("SCRAPER_THREAD_COUNT"))):
            print("Initializing scraper thread: ", j, "\n")
            scheduler = ScrapeScheduler(scrape_q, pagecount=page, download_q=download_q)
            scraper_schedulers_list.append(scheduler)

        # download queue is initialised inside scrape queue
        scrape_q.put(page)

        for i in range(len(scraper_schedulers_list)):
            scrape_q.put("DONE")

        for i in range(len(scraper_schedulers_list)):
            scraper_schedulers_list[i].join()


if __name__ == "__main__":
    main()
    print(len(os.listdir("images/")))
