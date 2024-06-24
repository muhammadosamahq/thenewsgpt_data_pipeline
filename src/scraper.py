import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from phi.tools.newspaper4k import Newspaper4k
import time
import json
import os
from typing import Tuple, List, Any, Dict, Union

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
    response = session.get(str(url), headers=headers)
    print(response.status_code)
    soup = BeautifulSoup(response.text, "html.parser")
    return response.status_code, soup

def get_all_source_urls(soup: BeautifulSoup, attr: str) -> List[str]:
    urls: List[str] = []
    title = soup.find_all(attrs=str(attr))
    for element in title:
        urls.append(element.a['href'])
    return urls

def get_filtered_urls(urls: List[str]) -> List[str]:
    print(len(urls))
    filtered_urls: List[str] = list(map(lambda url: url.replace("/index.php", "https://dunyanews.tv"), urls))
    filtered_urls = list(map(lambda url: url.replace("/index.php/en/", "https://dunyanews.tv"), urls))
    filtered_urls = ['https://92newshd.tv' + url if url.startswith('/about') else url for url in filtered_urls]
    filtered_urls = list(filter(lambda url: url.startswith("https://"), filtered_urls))
    print(len(filtered_urls))
    return filtered_urls

# def get_urls_pagination(soup, attr):
#     urls: list = []
#     c = 0
#     title = soup.find_all(attrs=str(attr))
#     for element in title:
#         urls.append(element.a['href'])
#     next_page = soup.find_all(attrs="page-link")[-1].a['href']
#     while next_page:
#         c = c + 1
#         session = requests.session()
#         response = session.get(str(next_page))
#         print(response.status_code)
#         soup = BeautifulSoup(response.text, "html.parser")
#         title = soup.find_all(attrs=str(attr))
#         for element in title:
#             urls.append(element.a['href'])
#         next_page = soup.find_all(attrs="page-link")[-1].a['href']
#         if c == 5:
#             return urls



# def get_individual_pages_urls(url):
#     all_pages_url = []
#     for page in range(1, 6):
#         status, soup = get_status_code_and_soup(url+str(page))
#         if status == 200:
#             urls = get_all_source_urls(soup, object["attr"])
#             urls = get_filtered_urls(urls)
#             all_pages_url.append(urls)
#         time.sleep(2)
#     return all_pages_url



# def fetch_pagination_articles(object, category, today_date):
#     counter = 0
#     current_date = datetime.now()
#     #yesterday_5 = (current_date - timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone(timedelta(hours=5)))
#     yesterday = (current_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

#     newspaper_tool = Newspaper4k()
    

#     for page in range(1, 6):
#         status, soup = get_status_code_and_soup(object["url"]+str(page))
#         if status == 200:
#             try:
#                 urls = get_all_source_urls(soup, object["attr"])
#                 urls = get_filtered_urls(urls)    
#                 for url in urls:
#                     try:
#                         article_data = newspaper_tool.get_article_data(url)
#                         # Check if 'publish_date' exists in the article data
#                         if 'publish_date' in article_data:
#                             given_date = datetime.fromisoformat(article_data["publish_date"])
#                             given_date_filtered = datetime.strptime(str(given_date).split("+")[0], "%Y-%m-%d %H:%M:%S")
#                             if given_date_filtered >= yesterday:
#                                 counter += 1
#                                 #print(counter, article_data)
#                                 article_data["id"] = counter
#                                 article_data["url"] = url
#                                 article_data["source"] = "dawn"
#                                 with open(f'.././data/{today_date}/{category}/articles/{category}_article_{counter}_{object["source"]}.json', 'w') as json_file:
#                                         json.dump(article_data, json_file, indent=4)
#                                 print("fetching...", counter)
#                             else:
#                                 print("outdated article, not getting fetched")
#                         else:
#                             print("publish_date not found in article_data")
#                         time.sleep(5)
#                     except Exception as e:
#                         print(f"Error processing article {url}: {e}")
#                         continue
#             except Exception as e:
#                 print(f"Raise error: {e}")


def fetch_articles(object: Dict[str, Union[str, int, List[str]]], category: str, today_date: datetime, soup: BeautifulSoup, counter: int) -> None:
    
    newspaper_tool: Newspaper4k = Newspaper4k()
    current_date = datetime.now()
    yesterday_12am: datetime = (current_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    today_12am: datetime = (current_date).replace(hour=0, minute=0, second=0, microsecond=0)

    # 
    # #yesterday_5 = (current_date - timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone(timedelta(hours=5)))
    # yesterday = (current_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    # newspaper_tool = Newspaper4k()
    
    
    # status, soup = get_status_code_and_soup(object["url"])
    #if status == 200:
    try:
        urls: List[str] = get_all_source_urls(soup, object["attr"])
        urls: List[str] = get_filtered_urls(urls)   
        for url in urls:
            try:
                article_data: Dict[str, Union[str, List[str]]] = newspaper_tool.get_article_data(url)
                # Check if 'publish_date' exists in the article data
                if 'publish_date' in article_data:
                    given_date: datetime  = datetime.fromisoformat(article_data["publish_date"])
                    given_date_filtered: datetime  = datetime.strptime(str(given_date).split("+")[0], "%Y-%m-%d %H:%M:%S")
                    if today_12am <= given_date_filtered >= yesterday_12am:
                        counter += 1
                        #print(counter, article_data)
                        article_data["id"] = counter
                        article_data["url"] = url
                        article_data["source"] = "dawn"
                        with open(f'.././data/{today_date}/{category}/articles/{category}_article_{counter}_{object["source"]}.json', 'w') as json_file:
                                json.dump(article_data, json_file, indent=4)
                        print("fetching...", counter)
                    else:
                        print("outdated article, not getting fetched")
                else:
                    print("publish_date not found in article_data")
                time.sleep(1)
            except Exception as e:
                print(f"Error processing article {url}: {e}")
                continue
    except Exception as e:
        print(f"Raise error: {e}")

    return counter

def fetch_save_articles(urls_info: List[Dict[str, Union[str, int]]], category: str, today_date: datetime) -> None:
    pagination_sources_list: List[str] = ["theexpresstribune", "hum", "92news", "abbtakk"]
    counter: int = 0
    status: int
    soup: BeautifulSoup
    for c, object in enumerate(urls_info):
        print(object["source"])
        if object["source"] in pagination_sources_list:
            for page in range(1, 6):
                status, soup = get_status_code_and_soup(object["url"]+str(page))
                if status == 200:
                    counter = fetch_articles(object, category, today_date, soup, counter)
        else:
            status, soup = get_status_code_and_soup(object["url"])
            if status == 200:
                counter = fetch_articles(object, category, today_date, soup, counter)


# def fetch_save_articles(urls, category):
#     current_date = datetime.now()
#     yesterday = (current_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

#     newspaper_tool = Newspaper4k()
#     counter = 0

#     for url_info in urls:
#         source = url_info['source']
#         url = url_info['url']
#         attr = url_info['attr']

#         # Handle pagination for URLs with 'page' or 'pno'
#         paginated_urls = []
#         if 'page' in url or 'pno' in url:
#             for i in range(1, 6):
#                 paginated_urls.append(url + str(i))
#         else:
#             paginated_urls.append(url)

#         for paginated_url in paginated_urls:
#             status, html = get_website_html_tags(paginated_url)
#             if status == 200:
#                 try:
#                     extracted_urls = get_all_urls(html, attr)
#                     filtered_urls_list = filtered_urls(extracted_urls)

#                     for article_url in filtered_urls_list:
#                         try:
#                             article_data = newspaper_tool.get_article_data(article_url)
#                             if 'publish_date' in article_data:
#                                 given_date = datetime.fromisoformat(article_data["publish_date"])
#                                 given_date_filtered = datetime.strptime(str(given_date).split("+")[0], "%Y-%m-%d %H:%M:%S")
#                                 if given_date_filtered >= yesterday:
#                                     counter += 1
#                                     article_data["id"] = counter
#                                     article_data["url"] = article_url
#                                     article_data["source"] = source
#                                     with open(f'.././data/{today_date}/{category}/articles/{category}_article_{counter}_{object["source"]}.json', 'w') as json_file:
#                                         json.dump(article_data, json_file, indent=4)
#                                     print("fetching...", counter)
#                                 else:
#                                     print("outdated article, not getting fetched")
#                             else:
#                                 print("publish_date not found in article_data")
#                             time.sleep(5)
#                         except Exception as e:
#                             print(f"Error processing article {article_url}: {e}")
#                             continue
#                 except Exception as e:
#                     print(f"Error processing URL {paginated_url}: {e}")

def main() -> None:
    #today_date = datetime.now().strftime("%Y-%m-%d")
    for category in categories:
        directory_path: str = f".././data/{today_date}/{category}/articles"
       #pakistan_directory_path = f".././data/{today_date}/pakistan/articles"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
        # if not os.path.exists(pakistan_directory_path):
        #     os.makedirs(pakistan_directory_path, exist_ok=True)

        with open(".././urls/{category}_urls.json", 'r') as file:
            urls_info: List[Dict[str, Union[str, int]]] = json.load(file)
        # with open(".././urls/pakistan_urls.json", 'r') as file:
        #     pakistan_urls = json.load(file)
        fetch_save_articles(urls_info, category, today_date)

        # for urls, category in zip([business_urls, pakistan_urls], categories):
        #     fetch_save_articles(urls, category, today_date)

if __name__ == "__main__":
    categories: List[str] = ["business", "pakistan"]
    
    today_date: datetime = datetime.now()
    #yesterday_5 = (current_date - timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone(timedelta(hours=5)))
    

    main()

        

    

