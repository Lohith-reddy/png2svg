import requests
from bs4 import BeautifulSoup as bs
import yaml

with open("config.yaml", 'r') as file:
    yaml_data = yaml.safe_load(file)
    file.close()


def download_img(tup):
    title, img = tup
    title = yaml_data["ENVIRONMENT_VARIABLES"]["IMAGE_DIR"] + "/" + title + ".svg"
    with open(title, 'wb') as file:
        file.write(requests.get(img).content)
        file.close()
    print("Downloaded:", title, "\n")
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
