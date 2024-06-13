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

def filtered_urls(urls):
    print(len(urls))
    filtered_urls = list(map(lambda url: url.replace("/index.php", "https://dunyanews.tv"), urls))
    filtered_urls = list(filter(lambda url: url.startswith("https://"), filtered_urls))
    print(len(filtered_urls))
    return filtered_urls

if __name__ == "__main__":
    urls: list = []
    all_urls: list = []
    current_date = datetime.now().strftime("%Y-%m-%d")

    with open(".././urls/static/business_urls.json", 'r') as file:
        data = json.load(file)

    for object in data:
        status, html = get_website_html_tags(object["url"])
        print(object["source"])
        if status == 200:
            if object["source"] == "propakistani":
                urls = get_urls_pagination(html, object["attr"])
                urls = filtered_urls(urls)
            else:
                urls = get_all_urls(html, object["attr"])
                urls = filtered_urls(urls)             

            for url in urls:
                all_urls.append({"url": url, "source": object["source"]})

            print(len(all_urls))

    with open(f'.././urls/dynamic/all_business_urls_{current_date}.json', 'w') as json_file:
        json.dump(all_urls, json_file, indent=4)

