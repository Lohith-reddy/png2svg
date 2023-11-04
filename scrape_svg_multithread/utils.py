import requests
from bs4 import BeautifulSoup as bs


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