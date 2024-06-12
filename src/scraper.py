import requests
from bs4 import BeautifulSoup
from datetime import datetime
import newspaper
import time
import json

articles_json: dict[str:str] = {}
list_of_articles: list[dict[str:str]] = []

def get_website_html_tags(url):
    session = requests.session()
    response = session.get(str(url))
    print(response.status_code)
    soup = BeautifulSoup(response.text, "html.parser")
    return response.status_code, soup

def get_urls_pagination(soup, attr):
    urls: list = []
    c = 0
    title = soup.find_all(attrs=str(attr))
    for element in title:
        urls.append(element.a['href'])
    next_page = soup.find_all(attrs="page-link")[-1].a['href']
    while next_page:
        c = c + 1
        session = requests.session()
        response = session.get(str(next_page))
        print(response.status_code)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find_all(attrs=str(attr))
        for element in title:
            urls.append(element.a['href'])
        next_page = soup.find_all(attrs="page-link")[-1].a['href']
        if c == 5:
            return urls

def get_all_urls(soup, attr):
    urls: list = []
    title = soup.find_all(attrs=str(attr))
    for element in title:
        urls.append(element.a['href'])
    return urls


if __name__ == "__main__":
    geo_status, geo_html = get_website_html_tags("https://www.geo.tv/category/business")
    dawn_status, dawn_html = get_website_html_tags("https://www.dawn.com/business")
    propakistani_status, propakistani_html = get_website_html_tags("https://propakistani.pk/category/business/")
    dailypakistani_status, dailypakistani_html = get_website_html_tags("https://en.dailypakistan.com.pk/business")
    aaj_status, aaj_html = get_website_html_tags("https://english.aaj.tv/business-economy")
    daily_status, daily_html = get_website_html_tags("https://dunyanews.tv/en/Business")
    if geo_status == 200 and dawn_status == 200 and propakistani_status == 200 and dailypakistani_status == 200 and aaj_status == 200 and daily_status == 200:
        geo_urls = get_all_urls(geo_html, "border-box")
        dawn_urls = get_all_urls(dawn_html, "story")
        aaj_urls = get_all_urls(aaj_html, "story")
        dunya_urls = get_all_urls(daily_html, "media__title media__title--threelines")
        dailypakistani_urls = get_all_urls(dailypakistani_html, "tt-post type-2")
        propakistani_urls = get_urls_pagination(propakistani_html, "entry-title")
        print(len(geo_urls))
        print(len(dawn_urls))
        print(len(propakistani_urls))
        print(len(dailypakistani_urls))
        print(len(aaj_urls))
        dunya_urls = list(map(lambda url: url.replace("/index.php", "https://dunyanews.tv"), dunya_urls))
        print(len(dunya_urls))
        all_urls = []
        all_urls.extend(geo_urls)
        all_urls.extend(dawn_urls)
        all_urls.extend(aaj_urls)
        all_urls.extend(dunya_urls)
        all_urls.extend(dailypakistani_urls)
        all_urls.extend(propakistani_urls)
        
        print(len(all_urls))
        print(all_urls)

