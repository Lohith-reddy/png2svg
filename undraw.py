import requests
from bs4 import BeautifulSoup as bs
import re
import threading
from multiprocessing import Queue
import os
from json import loads
from dotenv import load_dotenv

load_dotenv()


def download_img(tup):
    title, img = tup
    title = "images/" + title + ".svg"
    # print("Downloading: ", title)
    with open(title, 'wb') as file:
        file.write(requests.get(img).content)
        file.close()
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

    def __init__(self, page_count):
        super(UnDraw, self).__init__()
        self.page_count = page_count
        self.svg = []
        self.page_ext = "?page="

    def get_svg(self):
        svg = []
        names = []
        download_dict = {}
        for i in range(0, self.page_count):
            url = os.getenv("website_url")
            if i == 0:
                url = url
                for link_1 in get_soup(url).find_all('div', "ClassicGrid__Media-sc-td9pmq-2 ffqsDq"):
                    link_1 = str(link_1)
                    svg.append(re.search(r'data-src="([^"]*)', link_1).group(1))
                for link_2 in get_soup(url).find_all('div', "ClassicGrid__Content-sc-td9pmq-3 jCxkJm"):
                    link_2 = str(link_2)
                    names.append(link_2.split(">")[1].split("<")[0])
            else:
                url = os.getenv("second_url")
                url = url + self.page_ext + str(i)
                link = get_soup(url)
                link = str(link)
                link = loads(link)
                for obj in range(len(link["illos"])):
                    svg.append(link["illos"][obj]["image"])
                    names.append(link["illos"][obj]["title"])
            
        for i in range(len(svg)):
            download_dict[names[i]] = svg[i]
        
        print("length before returning download_dict", len(set(download_dict)))
        return download_dict


class Scheduler(threading.Thread):
    def __init__(self, queue):
        super(Scheduler, self).__init__()
        self.queue = queue
        self.start()

    def run(self):
        # print("Starting Download")
        while True:
            val = self.queue.get()
            if val == "DONE":
                break
            title = download_img(val)
            print("Downloaded: ", title + "\n")


def main():
    q = Queue()
    und = UnDraw(2)
    schedulers_list = []
    for i in range(10):
        scheduler = Scheduler(q)
        schedulers_list.append(scheduler)
    for i, j in und.get_svg().items():
        q.put((i, j))
        print("Added: ", i, "\n")

    for i in range(len(schedulers_list)):
        q.put("DONE")
    # scheduler.download()

    for i in range(len(schedulers_list)):
        schedulers_list[i].join()


if __name__ == "__main__":
    main()
    print(len(os.listdir("images")))

