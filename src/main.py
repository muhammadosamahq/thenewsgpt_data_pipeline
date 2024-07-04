import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import json
import os
import re
import nltk
from nltk.corpus import stopwords
import pandas as pd
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, fowlkes_mallows_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import numpy as np

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from dotenv import load_dotenv
import ast  # convert string to dict
import time


from scraper import process_each_category_data, get_filtered_url, standardize_date, get_status_code_and_soup
from cluster import *
from summary import *
from stats import *
   
# def get_status_code_and_soup(url: str) -> Tuple[int, BeautifulSoup]:
#     headers = {
#         'authority': 'cdn.unibotscdn.com',
#         'accept': '*/*',
#         'accept-language': 'en-US,en;q=0.9',
#         'origin': 'https://pakobserver.net',
#         'referer': 'https://pakobserver.net/',
#         'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
#         'sec-ch-ua-mobile': '?0',
#         'sec-ch-ua-platform': '"Linux"',
#         'sec-fetch-dest': 'empty',
#         'sec-fetch-mode': 'cors',
#         'sec-fetch-site': 'cross-site',
#         'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
#     }

#     session = requests.session()
#     response = session.get(url, headers=headers)
#     print(response.status_code)
#     soup = BeautifulSoup(response.text, "html.parser")
#     return response.status_code, soup

# def get_filtered_url(url: str) -> str:
#     filtered_url = url.replace("/index.php", "https://dunyanews.tv")
#     if url.startswith("https://"):
#         filtered_url = url
#     elif url.startswith('/about'):
#         filtered_url = 'https://92newshd.tv' + url
#     else:
#         filtered_url = None

#     return filtered_url

# def standardize_date(raw_date):
#     raw_date = raw_date.strip()
#     print(raw_date)
#     try:
#         date = dateparser.parse(raw_date).strftime("%Y-%m-%d")
#         print(date)
#         return date
#     except:
#         unwanted_characters = ["| Published", "|", "News Desk", "PM", "AM", "Web Desk", "Edit", "Delete", ".", "Updated"]
#         for char in unwanted_characters:
#             raw_date = raw_date.replace(char, "")
#         months_list = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
#         for month in months_list:
#             if month in raw_date:
#                 raw_date = (month + raw_date.split(month)[1]).strip()
#                 date = dateparser.parse(raw_date).strftime("%Y-%m-%d")
#                 print(date)
#                 return date
        
#         if "today" in raw_date.lower():
#             print(datetime.now().strftime("%Y-%m-%d"))
#             return datetime.now().strftime("%Y-%m-%d")
#         if "yesterday" in raw_date.lower():
#             print((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
#             return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
#         if 'ago' in raw_date.lower():
#             date = dateparser.parse(raw_date).strftime("%Y-%m-%d")
#             print(date)
#             return date

# def get_url_meta_data(soup, object):
#     get_url_meta_data_list: List[str] = []
#     get_url_meta_data_dict: Dict[str, Union[str, datetime]] = {}
#     titles = soup.find_all(object["object_attr"][0], {object["object_attr"][1]: object["object_attr"][2]})
#     print(len(titles))
#     for element in titles:
#         try:
#             if object["href_attr"] == "no-attr-href":
#                 get_url_meta_data_dict["url"] = element.a["href"]
#             else:
#                 get_url_meta_data_dict["url"] = element.find(attrs=str(object["href_attr"])).a["href"]

#             get_url_meta_data_dict["datetime"] = element.find(attrs=str(object["date_attr"])).get_text().strip()
#             get_url_meta_data_dict["title"] = element.find(attrs=str(object["title_attr"])).get_text().strip()

#             if all(get_url_meta_data_dict.values()):
#                 get_url_meta_data_list.append(get_url_meta_data_dict)

#             get_url_meta_data_dict = {}

#         except Exception as e:
#             if type(e).__name__ == "AttributeError" and "NoneType" in str(e):
#                 pass
#             else:
#                 print(f"Raise error: {e}")

#     return get_url_meta_data_list


if __name__ == "__main__":
    today_date = datetime.now().strftime("%Y-%m-%d")
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    business_json_path = '.././urls/business_urls_updated.json'
    pakistan_json_path = '.././urls/pakistan_urls_updated.json'
    urls_info = []

    pagination_sources_list: List[str] = ["propakistani", "theexpresstribune", "hum", "92news", "abbtakk"]
    categories: List[str] = ["politics", "governance", "sports", "international relations", "business", "health", "science and technology", "culture", "security", "weather", "fashion", "energy", "others"]
    directories = ["raw_articles", "articles", "clusters", "summary", "stats"]
    for sub_directory in directories:
        directory_path = f".././data/pakistan/{today_date}/{directories}"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)

    # Load business_json
    with open(business_json_path, 'r', encoding='utf-8') as business_file:
        business_data = json.load(business_file)
        urls_info.extend(business_data)

    # Load pakistan_json
    with open(pakistan_json_path, 'r', encoding='utf-8') as pakistan_file:
        pakistan_data = json.load(pakistan_file)
        urls_info.extend(pakistan_data)

    # Process each category data using functions from stats.py
    process_each_category_data(urls_info, pagination_sources_list)

    # columns_to_keep = ['title', 'authors', 'source', 'publish_date', 'url', 'text_cleaned']
    # rename_columns = {'text_cleaned': 'text'}

    # model = SentenceTransformer('all-MiniLM-L6-v2')
    # nltk.download('punkt')
    # nltk.download('stopwords')

    # for category in categories:
        
    #     fetch_save_articles(urls_info, category, today_date)

    #     process_clusters(category, today_date)

    #     clusters_directory_path = get_all_file_paths(f".././data/{today_date}/{category}/clusters")
    #     summary_directory_path = f'.././data/{today_date}/{category}/summary'
    #     get_save_summary_stats(clusters_directory_path, summary_directory_path)

    #     create_stats(category, clusters_directory_path)