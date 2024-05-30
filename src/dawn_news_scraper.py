import requests
from bs4 import BeautifulSoup
from datetime import datetime
from phi.tools.newspaper4k import Newspaper4k
import time
import json

dawn_articles_json: dict[str:str] = {}
list_of_articles: list[dict[str:str]] = []

def get_dawn_article_titles(url):
    session = requests.session()
    response = session.get(str(url))
    print(response.status_code)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find_all(attrs="sm:w-2/3 w-full sm:ml-6 sm:border-b border-gray-200")
    len(title)
    return title

def dawn_articles_metadata(title):
    for c, l in enumerate(range(len(title))):
        try:
            dawn_articles_dict = {
                'id': c,
                'timestamp': title[l].span.text.strip(),
                'title': title[l].h2.a.text.strip(),
                'url': title[l].a['href'],
                
            }
            print('count', c)
        except AttributeError:
            pass

        list_of_articles.append(dawn_articles_dict)
    return list_of_articles

def get_articles_data(list_of_articles):
    dawn_news_articles = []
    newspaper_tool = Newspaper4k()
    for c, r in enumerate(list_of_articles):
        article_data = {}
        if "url" in r:
            article_data = newspaper_tool.get_article_data(r["url"])
            article_data['id'] = c
            article_data['url'] = r["url"]
            dawn_news_articles.append(article_data)
            print(article_data)
            time.sleep(2)
    print(len(dawn_news_articles))
    return dawn_news_articles

def dawn_articles_content(list_of_articles, delay): #delay in sec
    for c, article in enumerate(list_of_articles):
        session = requests.session()
        response = session.get(article['url'])
        print(response.status_code)
        soup = BeautifulSoup(response.text, "html.parser")
        #print(soup.text.strip().replace("\n", ""))
        article['status_code'] = response.status_code
        article['content'] = soup.text.strip().replace("\n", "")
        print(c)
        print('.....finished.....')
        time.sleep(delay)
    return list_of_articles

def download_data_json(list_of_articles):
    timestamp = datetime.now()
    filename = f'../data/dawn_articles/dawn_articles_{timestamp}.json'
    with open(filename, 'w') as file:
        json.dump(list_of_articles, file, indent=4)
    print('downloaded in json format')

if __name__ == "__main__":
    title = get_dawn_article_titles("https://www.dawn.com/latest-news")
    list_of_articles = dawn_articles_metadata(title)
    dawn_news_articles = get_articles_data(list_of_articles)
    #articles_content_list = dawn_articles_content(list_of_articles, 5)
    download_data_json(dawn_news_articles)

