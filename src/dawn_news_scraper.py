import requests
from bs4 import BeautifulSoup
from datetime import datetime
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
    articles_content_list = dawn_articles_content(list_of_articles, 5)
    download_data_json(articles_content_list)

