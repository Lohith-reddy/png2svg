import requests
from bs4 import BeautifulSoup as bs
import re
from threading import Thread


def download_img(img, title):
    with open(title, 'wb') as file:
        file.write(requests.get(img).content)
        file.close()


class UnDraw:

    def __init__(self, page_count):
        self.page_count = page_count
        self.svg = []
        self.main_url = "https://undraw.co/illustrations"
        self.page_ext = "?page="

    def get_soup(self,url):
        response = requests.get(url)
        if response.status_code != 200:
            print("Error: ", response.status_code)
            return None
        else:
            response = requests.get(url).text
            links = bs(response, "html.parser")
        return links

    def get_svg(self):
        svg = []
        for i in range(0, self.page_count):
            url = "https://undraw.co/illustrations"
            if i == 0:
                url = url
            else:
                url = url + self.page_ext + str(i)
            for link in self.get_soup(url).find_all('div', "ClassicGrid__Media-sc-td9pmq-2 ffqsDq"):
                link = str(link)
                svg.append(re.search(r'data-src="([^"]*)', link).group(1))
        yield svg

    def find_name(self):
        svg = []
        for i in range(0, self.page_count):
            url = "https://undraw.co/illustrations"
            if i == 0:
                url = url
            else:
                url = url + self.page_ext + str(i)
            for link in self.get_soup(url).find_all('div', "ClassicGrid__Content-sc-td9pmq-3 jCxkJm"):
                link = str(link)
                svg.append(link.split(">")[1].split("<")[0])

    def run(self):
        pass
