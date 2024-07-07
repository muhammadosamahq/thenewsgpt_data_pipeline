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


from scraper import *
from cluster import *
from summary import *
from stats import *
from filter_articles import *
from filter_stats import *
from clusters_by_llm import *

today_date = datetime.now().strftime("%Y-%m-%d")
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

raw_articles_dir = f'./../data/pakistan/{today_date}/raw_articles'
articles_dir = f'./../data/pakistan/{today_date}/articles'
categories_dir = f'./../data/pakistan/{today_date}/categories'
business_json_path = '.././urls/business_urls_updated.json'
pakistan_json_path = '.././urls/pakistan_urls_updated.json'

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

def process_clusters(category: str, today_date: datetime) -> None:
    all_articles_json_list: list[Dict[str, Union[str, int, List[str]]]] = fetch_and_merge_json_files(f".././data/pakistan/{today_date}/categories/{category}")
    if len(all_articles_json_list) > 15:
        df: pd.DataFrame = get_clustered_dataframe(all_articles_json_list)
        limit_exceeded_clusters: List[List[Dict[str: str]]] = get_clusters_list(df, category, today_date)
        
        while limit_exceeded_clusters:
            new_clusters: List = []
            for cluster_json in limit_exceeded_clusters:
                df: pd.DataFrame = get_clustered_dataframe(cluster_json)
                new_clusters.extend(get_clusters_list(df, category, today_date))
            limit_exceeded_clusters = new_clusters
    else:
        category_directory_path: str = f'.././data/pakistan/{today_date}/clusters/{category}'
        if not os.path.exists(category_directory_path):
            os.makedirs(category_directory_path)
        file_no: int = get_next_file_number(category_directory_path)
        filename: str = f'{category_directory_path}/{file_no}.json'

        # if not os.path.exists(category_directory_path):
        #     os.makedirs(category_directory_path, exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_articles_json_list, f, ensure_ascii=False, indent=4)
        
        print(f"Data saved to {filename}")

if __name__ == "__main__":

    counter = 0

    urls_info = []

    pagination_sources_list: List[str] = ["propakistani", "theexpresstribune", "hum", "92news", "abbtakk"]
    categories: List[str] = ["politics", "governance", "sports", "international relations", "business", "health", "science and technology", "culture", "security", "weather", "fashion", "energy", "others"]
    directories = ["raw_articles", "articles", "categories", "clusters", "summary"]

    for dir in directories:
        directory_path = f".././data/pakistan/{today_date}/{dir}"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True) 
        if dir in  directories[2:]:
            for category in categories:
                category_directory_path = f"{directory_path}/{category}"
                if not os.path.exists(category_directory_path):
                    os.makedirs(category_directory_path, exist_ok=True)

    # Load business_json
    with open(business_json_path, 'r', encoding='utf-8') as business_file:
        business_data = json.load(business_file)
        urls_info.extend(business_data)

    # Load pakistan_json
    with open(pakistan_json_path, 'r', encoding='utf-8') as pakistan_file:
        pakistan_data = json.load(pakistan_file)
        urls_info.extend(pakistan_data)

    # # scraper.py 
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
                        counter = article_processing(articles_meta_data, counter)
                    time.sleep(1)
                except Exception as e:
                    print(f"Raise error: {e}")
        else:
            try:
                status, soup = get_status_code_and_soup(object["url"])
                if status == 200:
                    articles_meta_data = get_url_meta_data(soup, object)
                    print("len of urls", len(articles_meta_data))
                    counter = article_processing(articles_meta_data, counter)

                    time.sleep(1)
            except Exception as e:
                print(f"Raise error: {e}")

    # filter_articles.py
    filter_articles(raw_articles_dir, articles_dir)

    # clusters_by_llm.py
    docs = json_directory_loader(articles_dir)
    chain = cluster_chain()
    all_json_objects_list = get_clusters_by_llm(categories, docs, chain)
    
    # Iterate through the list and move JSON files to respective category folders
    for item in all_json_objects_list:
        article_id = item['id']
        category = item['category']
        if category in categories:
            move_article_to_category_folder(articles_dir, categories_dir, article_id, category)
        else:
            print(f'Unknown category: {category}')

    # cluster.py
    model: SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2')
    nltk.download('punkt')
    nltk.download('stopwords')

    for category in categories:
        process_clusters(category, today_date)

    # summary.py
    #o_llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0, model_name="gpt-4o")
    g_llm: GoogleGenerativeAI = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")
    summarization_chain = load_summarize_chain(g_llm, chain_type="stuff")

    for category in categories:
        summary_directory_path = f'.././data/pakistan/{today_date}/summary/{category}'
        clusters_category_directory_path = f".././data/pakistan/{today_date}/clusters/{category}"
        all_clusters_path: List[str] = get_all_file_paths(clusters_category_directory_path)
        get_save_summary_stats(all_clusters_path, summary_directory_path)

    # stats.py
    for category in categories:
        all_clusters_path = get_all_file_paths(f".././data/pakistan/{today_date}/clusters/{category}")
        create_stats(category, all_clusters_path)
    
    # filter_stats.py
    for category in categories:
    
        # Directory containing the stats JSON files
        stats_directory_path = get_all_file_paths(f".././data/pakistan/{today_date}/summary/{category}")
        print(stats_directory_path)

        # Directory to save filtered JSON files
        save_directory = f".././data/pakistan/{today_date}/summary/{category}"

        for stat in stats_directory_path:
            print(stat)
            with open(stat, 'r', encoding='utf-8') as file:
                summary = json.load(file)
            
            stats_json_list = summary.get('stats', [])

            # Check each object in stats_json_list
            filtered_stats = []
            seen_objects = set()
            
            for item in stats_json_list:
                # Flatten the lists inside 'data' if they contain nested lists
                data_values = flatten_list(item['data'])
                
                # Check if any value in 'data' is numerical
                # if not any(any(char.isdigit() for char in str(value)) for value in data_values):
                #     continue

                # Check if all values in 'data' and 'headings' are the same
                if len(set(data_values)) == 1 or len(set(item['headings'])) == 1:
                    continue

                # Check if the object is repeating
                if item['object'] in seen_objects:
                    continue

                seen_objects.add(item['object'])
                filtered_stats.append(item)

            # Save the filtered list to a new file in the testing folder
            base_filename = os.path.basename(stat)
            new_filename = os.path.join(save_directory, base_filename)

            summary["stats"] = filtered_stats
            with open(new_filename, 'w') as json_file:
                json.dump(summary, json_file, indent=4) 

            print(f"Processed {stat}")
            print(f"Filtered results saved to {new_filename}")
            print(f"Original length: {len(stats_json_list)}, Filtered length: {len(filtered_stats)}")
 
