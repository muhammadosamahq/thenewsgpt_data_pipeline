#import what we need
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from dateutil import parser
import dateparser
from phi.tools.newspaper4k import Newspaper4k
import time
import json
import re
import os
from typing import Tuple, List, Any, Dict, Union
import pandas as pd



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

def get_filtered_urls(urls: List[str]) -> List[str]:
    print(len(urls))
    filtered_urls: List[str] = list(map(lambda url: url.replace("/index.php", "https://dunyanews.tv"), urls))
    #filtered_urls = list(map(lambda url: url.replace("/index.php/en", "https://dunyanews.tv"), urls))
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

    # Clean multiple spaces and newlines
    raw_date = re.sub(r'\s+', ' ', raw_date).strip()

    # Special handling for "Today" and "Yesterday"
    if "Today" in raw_date:
        return datetime.now().strftime("%Y-%m-%d")
    if "Yesterday" in raw_date:
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Handle specific formats using regular expressions
    # Example: "by Web Desk Staff June 25, 2024"
    match = re.search(r'(\w+\s+\d{1,2},?\s+\d{4})', raw_date)
    if match:
        try:
            date = parser.parse(match.group(1))
            return date.strftime("%Y-%m-%d")
        except ValueError:
            pass  # Handle the case if parsing fails, maybe return "Invalid date format"

    # Handle "Updated 24 Jun, 2024" format
    if "Updated" in raw_date:
        updated_date = re.search(r'\b\d{1,2}\s+\w{3},?\s+\d{4}\b', raw_date)
        if updated_date:
            try:
                raw_date = updated_date.group(0)
                date = parser.parse(raw_date)
                return date.strftime("%Y-%m-%d")
            except ValueError:
                pass  # Handle the case if parsing fails, maybe return "Invalid date format"

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


def get_url_meta_data(soup, object):
    get_url_meta_data_list: List[str] = []
    get_url_meta_data_dict: Dict[str, Union[str, datetime]] = {}
    #objects = soup.find_all(attrs="tt-post-info prr-post-5-info-md")
    titles = soup.find_all(object["object_attr"][0], {object["object_attr"][1]: object["object_attr"][2]})
    print(len(titles))
    for element in titles:
        try:
            #print(element.find(attrs="media__item").a["href"])
            #print(element.find(attrs="story__time").get_text())
            if object["href_attr"] == "no-attr-href":
                get_url_meta_data_dict["url"] = element.a["href"]
            else:
                get_url_meta_data_dict["url"] = element.find(attrs=str(object["href_attr"])).a["href"]

            get_url_meta_data_dict["datetime"] = element.find(attrs=str(object["date_attr"])).get_text().strip()
            get_url_meta_data_dict["title"] = element.find(attrs=str(object["title_attr"])).get_text().strip()

            if all(get_url_meta_data_dict.values()):
                get_url_meta_data_list.append(get_url_meta_data_dict)

            get_url_meta_data_dict = {}
            #print(element)

        except Exception as e:
            if type(e).__name__ == "AttributeError" and "NoneType" in str(e):
                # Handle NoneType error silently by passing
                pass
            else:
                # Print other exceptions
                print(f"Raise error: {e}")
                # Optionally, print the element causing the error
                # print(element)
    
    return get_url_meta_data_list

if __name__ == "__main__":
    data = []
    pagination_sources_list: List[str] = ["propakistani", "theexpresstribune", "hum", "92news", "abbtakk"]

    today_date: datetime = datetime.now().strftime("%Y-%m-%d")
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    with open(f"./urls/business_urls_updated.json", 'r') as file:
        urls_info = json.load(file)
    
    for c, object in enumerate(urls_info):
        print(object["source"])
        #if object["source"] == "dailypakistan":
        print(c)
        if object["source"] in pagination_sources_list:
            for page in range(1, 6):
                status, soup = get_status_code_and_soup(object["url"]+str(page))
                if status == 200:
                    url_meta_data = get_url_meta_data(soup, object)
                    for obj in url_meta_data:
                        date = standardize_date(obj["datetime"])
                        if date == yesterday_date:
                            with open(f'./testing/articles/{obj["datetime"]}_article.json', 'w') as json_file:
                                json.dump(obj, json_file, indent=4)
        
        status, soup = get_status_code_and_soup(object["url"])
        if status == 200:
            url_meta_data = get_url_meta_data(soup, object)
            for obj in url_meta_data:
                print(obj["datetime"])
                date = standardize_date(obj["datetime"])
                if date == yesterday_date:
                    with open(f'./testing/articles/{obj["datetime"]}_article.json', 'w') as json_file:
                        json.dump(obj, json_file, indent=4)

        
    df = pd.DataFrame(data)
    df.to_csv('testing_data.csv', index=False, header=True)

    #df.to_json('testing_data.json', orient='records', indent=4)
    print("saved to json")

