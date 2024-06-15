import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from phi.tools.newspaper4k import Newspaper4k
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
    newspaper_tool = Newspaper4k()
    urls: list = []
    all_urls: list = []
    current_date = datetime.now()
    yesterday = (current_date - timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone(timedelta(hours=5)))
    

    with open(".././urls/static/business_urls.json", 'r') as file:
        data = json.load(file)

    for c, object in enumerate(data):
        status, html = get_website_html_tags(object["url"])
        print(object["source"])
        if status == 200:
            try:
                if object["source"] == "propakistani":
                    urls = get_urls_pagination(html, object["attr"])
                    urls = filtered_urls(urls)
                    for url in urls:
                        article_data = newspaper_tool.get_article_data(url)
                        given_date = datetime.fromisoformat(article_data["publish_date"])
                        if  given_date >= yesterday:
                            article_data["id"] = c
                            article_data["url"] = url
                            article_data["source"] = object["source"]
                            list_of_articles.append(article_data)
                        time.sleep(5)
                else:
                    urls = get_all_urls(html, object["attr"])
                    urls = filtered_urls(urls)    
                    for url in urls:
                        article_data = newspaper_tool.get_article_data(url)
                        given_date = datetime.fromisoformat(article_data["publish_date"])
                        if  given_date >= yesterday:
                            article_data["id"] = c
                            article_data["url"] = url
                            article_data["source"] = object["source"]
                            list_of_articles.append(article_data)
                        time.sleep(5)

            except:
                pass

            # for url in urls:
            #     all_urls.append({"url": url, "source": object["source"]})

            # print(len(all_urls))

    with open(f'.././data/business/all_business_articles_{datetime.now().date()}.json', 'w') as json_file:
        json.dump(list_of_articles, json_file, indent=4)

