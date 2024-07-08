import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser
import dateparser
from phi.tools.newspaper4k import Newspaper4k
import time
import json
import re
from typing import Tuple, List, Dict, Union
import os

def get_status_code_and_soup(url: str) -> Tuple[int, BeautifulSoup]:
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
    response = session.get(url, headers=headers)
    print(response.status_code)
    soup = BeautifulSoup(response.text, "html.parser")
    return response.status_code, soup

def get_filtered_url(url: str) -> str:
    filtered_url = url.replace("/index.php", "https://dunyanews.tv")
    if url.startswith("https://"):
        filtered_url = url
    elif url.startswith('/about'):
        filtered_url = 'https://92newshd.tv' + url
    else:
        filtered_url = None

    return filtered_url

def standardize_date(raw_date):
    raw_date = raw_date.strip()
    print(raw_date)
    try:
        date = dateparser.parse(raw_date).strftime("%Y-%m-%d")
        print(date)
        return date
    except:
        unwanted_characters = ["| Published", "|", "News Desk", "PM", "AM", "Web Desk", "Edit", "Delete", ".", "Updated"]
        for char in unwanted_characters:
            raw_date = raw_date.replace(char, "")
        months_list = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        for month in months_list:
            if month in raw_date:
                raw_date = (month + raw_date.split(month)[1]).strip()
                date = dateparser.parse(raw_date).strftime("%Y-%m-%d")
                print(date)
                return date
        
        if "today" in raw_date.lower():
            print(datetime.now().strftime("%Y-%m-%d"))
            return datetime.now().strftime("%Y-%m-%d")
        if "yesterday" in raw_date.lower():
            print((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
            return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if 'ago' in raw_date.lower():
            date = dateparser.parse(raw_date).strftime("%Y-%m-%d")
            print(date)
            return date

def get_url_meta_data(soup, object):
    get_url_meta_data_list: List[str] = []
    get_url_meta_data_dict: Dict[str, Union[str, datetime]] = {}
    titles = soup.find_all(object["object_attr"][0], {object["object_attr"][1]: object["object_attr"][2]})
    print(len(titles))
    for element in titles:
        try:
            if object["href_attr"] == "no-attr-href":
                get_url_meta_data_dict["url"] = element.a["href"]
            else:
                get_url_meta_data_dict["url"] = element.find(attrs=str(object["href_attr"])).a["href"]

            get_url_meta_data_dict["datetime"] = element.find(attrs=str(object["date_attr"])).get_text().strip()
            get_url_meta_data_dict["title"] = element.find(attrs=str(object["title_attr"])).get_text().strip()

            if all(get_url_meta_data_dict.values()):
                get_url_meta_data_list.append(get_url_meta_data_dict)

            get_url_meta_data_dict = {}

        except Exception as e:
            if type(e).__name__ == "AttributeError" and "NoneType" in str(e):
                pass
            else:
                print(f"Raise error: {e}")

    return get_url_meta_data_list

def article_processing(articles_meta_data, counter):
    newspaper_tool: Newspaper4k = Newspaper4k()
    for obj in articles_meta_data:
        print(obj["url"])
        print(obj["datetime"])
        date = standardize_date(obj["datetime"])
        if date == yesterday_date:
            url = get_filtered_url(obj["url"])
            if url:
                try:     
                    
                    print("successful... Date under range", date, counter)
                    print(url)
                    article_data: Dict[str, Union[str, List[str]]] = newspaper_tool.get_article_data(url)
                    #obj["id"] = f"pk-{object["source"]}-{counter}"
                    obj["authors"] = article_data["authors"]
                    obj["source"] = object["source"]
                    obj["text"] = article_data["text"]
                    obj["datetime"] = date
                    with open(f'.././data/pakistan/{today_date}/raw_articles/{counter}.json', 'w') as json_file:
                        json.dump(obj, json_file, indent=4)
                        print("file saved successfully")
                        counter = counter + 1  
                    time.sleep(2)
                except Exception as e:
                    print(f"Error processing article {url}: {e}")
                continue
    return counter

if __name__ == "__main__":
    today_date: datetime = datetime.now().strftime("%Y-%m-%d")
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    raw_articles_directory_path = f'.././data/pakistan/{today_date}/raw_articles'
    if not os.path.exists(raw_articles_directory_path):
        os.makedirs(raw_articles_directory_path)

    business_json_path = '.././urls/business_urls_updated.json'
    pakistan_json_path = '.././urls/pakistan_urls_updated.json'
    urls_info = []
    data = []
    counter = 0

    categories: List[str] = ["politics", "governance", "sports", "international relations", "business", "health", "science and technology", "culture", "security", "weather", "fashion", "energy", "others"]
    
    pagination_sources_list: List[str] = ["propakistani", "theexpresstribune", "hum", "92news", "abbtakk"]
    directories = ["raw_articles", "articles", "clusters", "summary", "stats"]
    # for sub_directory in directories:
    #     directory_path = f".././data/pakistan/{today_date}/{directories}"
    #     if not os.path.exists(directory_path):
    #         os.makedirs(directory_path, exist_ok=True)

    

    # Load business_json
    with open(business_json_path, 'r', encoding='utf-8') as business_file:
        business_data = json.load(business_file)
        urls_info.extend(business_data)  # Extend combined_data with business_data

    # Load pakistan_json
    with open(pakistan_json_path, 'r', encoding='utf-8') as pakistan_file:
        pakistan_data = json.load(pakistan_file)
        urls_info.extend(pakistan_data) 

    
    for c, object in enumerate(urls_info):
        print(object["source"])
        print(c)
        if object["source"] in pagination_sources_list:
            for page in range(1, 6):
                try:
                    status, soup = get_status_code_and_soup(object["url"] + str(page))
                    if status == 200:
                        articles_meta_data = get_url_meta_data(soup, object)
                        print("len of urls", len(articles_meta_data))
                        counter = article_processing(articles_meta_data, counter, yesterday_date, today_date)
                    time.sleep(1)
                except Exception as e:
                    print(f"Raise error: {e}")
        else:
            try:
                status, soup = get_status_code_and_soup(object["url"])
                if status == 200:
                    articles_meta_data = get_url_meta_data(soup, object)
                    print("len of urls", len(articles_meta_data))
                    counter = article_processing(articles_meta_data, counter, yesterday_date)

                    time.sleep(1)
            except Exception as e:
                print(f"Raise error: {e}")

    