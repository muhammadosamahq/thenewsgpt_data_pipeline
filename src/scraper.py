import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from phi.tools.newspaper4k import Newspaper4k
import time
import json
import os

def get_website_html_tags(url):
    headers = {
    'authority': 'cdn.unibotscdn.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://pakobserver.net',
    'referer': 'https://pakobserver.net/',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    session = requests.session()
    response = session.get(str(url), headers=headers)
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

def fetch_save_articles(urls):
    current_date = datetime.now()
    #yesterday_5 = (current_date - timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone(timedelta(hours=5)))
    yesterday = (current_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    newspaper_tool = Newspaper4k()
    counter = 0

    for c, object in enumerate(urls):
        status, html = get_website_html_tags(object["url"])
        print(object["source"])
        if status == 200:
            try:
                urls = get_all_urls(html, object["attr"])
                urls = filtered_urls(urls)    
                for url in urls:
                    article_data = newspaper_tool.get_article_data(url)
                    given_date = datetime.fromisoformat(article_data["publish_date"])
                    given_date_filtered = datetime.strptime(str(given_date).split("+")[0], "%Y-%m-%d %H:%M:%S")
                    if  given_date_filtered >= yesterday:
                        counter = counter + 1
                        article_data["id"] = counter 
                        article_data["url"] = url
                        article_data["source"] = object["source"]
                        with open(f'.././data/{today_date}/business/articles/business_article_{counter}_{object["source"]}.json', 'w') as json_file:
                            json.dump(article_data, json_file, indent=4)
                        print("fetching...", counter)
                    else:
                        print("outdated article, not getting fetch")
                    time.sleep(5)

            except:
                pass

if __name__ == "__main__":
    today_date = datetime.now().strftime("%Y-%m-%d")
    directory_path = f".././data/{today_date}/business/articles"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)

    with open(".././urls/business_urls.json", 'r') as file:
        urls = json.load(file)

    fetch_save_articles(urls)

        

    

