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


from news_tool_scraper import *
from k_means_cluster import *
from summarization import *
from stats import *


if __name__ == "__main__":
    categories = ["business", "pakistan"]
    sub_directories = ["articles", "clusters", "summary", "stats"]

    today_date = datetime.now().strftime("%Y-%m-%d")
    
    columns_to_keep = ['title', 'authors', 'source', 'publish_date', 'url', 'text_cleaned']
    rename_columns = {'text_cleaned': 'text'}

    model = SentenceTransformer('all-MiniLM-L6-v2')
    nltk.download('punkt')
    nltk.download('stopwords')

    for category in categories:
        for sub_directory in sub_directories:
            directory_path = f".././data/{today_date}/{category}/{sub_directory}"
            if not os.path.exists(directory_path):
                os.makedirs(directory_path, exist_ok=True)
        
        with open(f".././urls/{category}_urls.json", 'r') as file:
            urls_info = json.load(file)
        
        fetch_save_articles(urls_info, category, today_date)

        process_clusters(category, today_date)

        clusters_directory_path = get_all_file_paths(f".././data/{today_date}/{category}/clusters")
        summary_directory_path = f'.././data/{today_date}/{category}/summary'
        get_save_summary_stats(clusters_directory_path, summary_directory_path)

        create_stats(category, clusters_directory_path)