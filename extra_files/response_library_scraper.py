import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from dateutil import parser
import dateparser
import time
import json
import os
from typing import Tuple, List, Any, Dict, Union
import re

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
    filtered_urls = list(map(lambda url: url.replace("/index.php/en", "https://dunyanews.tv"), urls))
    filtered_urls = ['https://92newshd.tv' + url if url.startswith('/about') else url for url in filtered_urls]
    filtered_urls = list(filter(lambda url: url.startswith("https://"), filtered_urls))
    print(len(filtered_urls))
    return filtered_urls

def remove_potential_author(text):
  # Split by newlines
  lines = text.splitlines()
  # If there are multiple lines, remove the first one (potential author name)
  if len(lines) > 1:
    return "\n".join(lines[1:])
  # Otherwise, return the original text
  return text

def standardize_date(raw_date: str) -> str:
    # Remove leading and trailing whitespace
    raw_date = raw_date.strip()

    # Remove author's name if present (alternative approach)
    raw_date = remove_potential_author(raw_date)

    # Remove unwanted characters and words
    unwanted_characters = ["| Published", "|", "News Desk", "PM", "AM", "Web Desk", "Edit", "Delete", ".", "Today", "Yesterday", "Updated"]
    for char in unwanted_characters:
        raw_date = raw_date.replace(char, "")

    # Special handling for "Today" and "Yesterday"
    if "Today" in raw_date:
        return datetime.now().strftime("%Y-%m-%d")
    if "Yesterday" in raw_date:
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Handle "Updated 24 Jun, 2024" format
    if "Updated" in raw_date:
        updated_date = re.search(r'\b\d{1,2}\s+\w{3},?\s+\d{4}\b', raw_date)
        if updated_date:
            raw_date = updated_date.group(0)

    # Clean multiple spaces and newlines
    raw_date = re.sub(r'\s+', ' ', raw_date).strip()

    # Handle relative dates like "4 days ago"
    if 'ago' in raw_date:
        date = dateparser.parse(raw_date)
    else:
        # Parse the date using dateutil's parser
        try:
            date = parser.parse(raw_date)
        except ValueError:
            return "Invalid date format"

    # Format the date to YYYY-MM-DD
    formatted_date = date.strftime("%Y-%m-%d")
    return formatted_date

def is_date_yesterday(date):
    date = datetime.strptime(standardize_date(date), "%Y-%m-%d")

    # Current date and time
    current_date: datetime = datetime.now()

    # Define yesterday 12:00 AM and today 12:00 AM
    yesterday_12am: datetime = (current_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    today_12am: datetime = current_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Check if given_date_filtered is between yesterday 12:00 AM and today 12:00 AM
    if yesterday_12am <= date < today_12am:
        return True
    else:
        return False

if __name__ == "__main__":
    article_data = {}
    today_date: datetime = datetime.now().strftime("%Y-%m-%d")
    categories: List[str] = ["business", "pakistan"]
    for category in categories:
        directory_path: str = f".././testing/{today_date}/{category}/articles"
       #pakistan_directory_path = f".././data/{today_date}/pakistan/articles"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
        # if not os.path.exists(pakistan_directory_path):
        #     os.makedirs(pakistan_directory_path, exist_ok=True)

        with open(f".././urls/{category}_urls.json", 'r') as file:
            urls_info: List[Dict[str, Union[str, int]]] = json.load(file)

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
                        
                        urls: List[str] = get_all_source_urls(soup, object["urls_attr"])
                        urls: List[str] = get_filtered_urls(urls)  
                        for url in urls:
                            try:
                                status, soup = get_status_code_and_soup(url)
                                if status == 200:
                                    date = standardize_date(soup.find(attrs=object["date_attr"]).get_text())
                                    if is_date_yesterday(date) == True:
                                        counter += 1
                                        article_data["id"] = counter
                                        article_data["source"] = object["source"]
                                        article_data["url"] = url
                                        article_data["title"] = soup.find(attrs=object["title_attr"]).get_text()
                                        article_data["text"] = soup.find(attrs=object["content_attr"]).get_text()
                                        article_data["date"] = soup.find(attrs=object["date_attr"]).get_text()
                                        with open(f'.././testing/{today_date}/{category}/articles/{category}_article_{counter}_{object["source"]}.json', 'w') as json_file:
                                            json.dump(article_data, json_file, indent=4)
                                        print("fetching...", counter)
                                else:
                                    print(status, url)
                                time.sleep(1)    
                            except Exception as e:
                                print("Exception is", e)
                                print(url)
                            

            else:
                status, soup = get_status_code_and_soup(object["url"])
                if status == 200:
                    #counter = fetch_articles(object, category, today_date, soup, counter)
                    urls: List[str] = get_all_source_urls(soup, object["urls_attr"])
                    urls: List[str] = get_filtered_urls(urls) 
                    for url in urls:
                        try:
                            status, soup = get_status_code_and_soup(url)
                            if status == 200:
                                date = standardize_date(soup.find(attrs=object["date_attr"]).get_text())
                                if is_date_yesterday(date) == True:
                                    counter += 1
                                    article_data["id"] = counter
                                    article_data["source"] = object["source"]
                                    article_data["url"] = url
                                    article_data["title"] = soup.find(attrs=object["title_attr"]).get_text()
                                    article_data["text"] = soup.find(attrs=object["content_attr"]).get_text()
                                    article_data["date"] = soup.find(attrs=object["date_attr"]).get_text()
                                    with open(f'.././testing/{today_date}/{category}/articles/{category}_article_{counter}_{object["source"]}.json', 'w') as json_file:
                                        json.dump(article_data, json_file, indent=4)
                                    print("fetching...", counter)
                            time.sleep(1) 
                        except Exception as e:
                                print("Exception is", e)
                                print(url)