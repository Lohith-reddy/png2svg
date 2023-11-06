import threading
import os
from utils import get_soup

import re
from json import loads
from dotenv import load_dotenv
import yaml

load_dotenv()
with open("config.yaml", 'r') as file:
    yaml_data = yaml.safe_load(file)
    file.close()


class UnDraw(threading.Thread):

    def __init__(self):
        super(UnDraw, self).__init__()
        self.page_ext = yaml_data["ENVIRONMENT_VARIABLES"]["PAGE_EXT"]

    def get_svg(self, pagecount=0):
        print("received page number: ", pagecount)
        svg = []
        names = []
        download_dict = {}
        url = os.getenv("WEBSITE_URL")
        if pagecount == 0:
            url = url
            for link_1 in get_soup(url).find_all('div', yaml_data["ENVIRONMENT_VARIABLES"]["CLASS_NAME_SVG"]):
                link_1 = str(link_1)
                svg.append(re.search(r'data-src="([^"]*)', link_1).group(1))
            for link_2 in get_soup(url).find_all('div', yaml_data["ENVIRONMENT_VARIABLES"]["CLASS_NAME_TITLE"]):
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


