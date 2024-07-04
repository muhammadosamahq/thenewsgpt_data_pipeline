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
from datetime import datetime
import seaborn as sns
#import torch
import numpy as np
import time
import json
import os
from typing import Tuple, List, Any, Dict, Union


def preprocess_text(text: str) -> str:
    # Ensure text is a string
    if not isinstance(text, str):
        return ""
    # remove links
    text: str = re.sub(r"http\S+", "", text)
    # remove special chars and numbers
    text: str = re.sub("[^A-Za-z]+", " ", text)

    # remove stopwords
    tokens: str = nltk.word_tokenize(text)
    tokens: List[str] = [w for w in tokens if not w.lower() in stopwords.words("english")]
    text: str = " ".join(tokens)
    text: str = text.lower().strip()

    return text

def get_next_file_number(directory: str) -> int:
    # Get a list of all files in the directory
    files: List[str] = os.listdir(directory)
    
    # Filter out non-JSON files and strip the .json extension
    json_files: List[str] = [f for f in files if f.endswith('.json')]
    json_numbers: List[int] = [int(f.replace('.json', '')) for f in json_files if f.replace('.json', '').isdigit()]
    
    # If there are no JSON files, start from 0
    if not json_numbers:
        return 0
    
    # Otherwise, return the next number after the highest current number
    return max(json_numbers) + 1

def fetch_and_merge_json_files(directory: str) -> List[Dict[str, Union[str, int, List[str]]]]:
    # List all files in the directory
    files: List[str] = os.listdir(directory)

    # Initialize an empty list to hold the merged JSON objects
    merged_data: List[Dict[str, Union[str, int, List[str]]]] = []

    # Iterate through each file in the directory
    for file in files:
        if file.endswith('.json'):
            # Construct the full file path
            file_path: str = os.path.join(directory, file)
            
            # Open and read the JSON file
            with open(file_path, 'r') as f:
                data: Dict[str, Union[str, int, List[str]]] = json.load(f)
                
                # If the data is a list, extend the merged_data list
                if isinstance(data, list):
                    merged_data.extend(data)
                else:
                    # If the data is a single object, append it to the merged_data list
                    merged_data.append(data)

    return merged_data
def sentance_transformers_embeddings(df: pd.DataFrame) -> np.ndarray:
    model: SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2')
    st: float = time.time()

    # Assuming `model` is initialized somewhere in your code
    df['encode_transforemers'] = df['text_cleaned'].apply(lambda text: model.encode(text, convert_to_numpy=True).flatten())

    et: float = time.time()

    print("Elapsed time: {:.2f} seconds".format(et - st))

    X_transformers: np.ndarray = np.vstack(df['encode_transforemers'])
    return X_transformers

def dimension_reduction(df: pd.DataFrame, embedding: np.ndarray, method: str) -> None:

    pca = PCA(n_components=2, random_state=42)

    pca_vecs: np.ndarray = pca.fit_transform(embedding)

    # save our two dimensions into x0 and x1
    x0: np.ndarray = pca_vecs[:, 0]
    x1: np.ndarray = pca_vecs[:, 1]
    
    df[f'x0_{method}'] = x0 
    df[f'x1_{method}'] = x1

def get_clustered_dataframe(all_articles_json_list: list[Dict[str, Union[str, int, List[str]]]]) -> pd.DataFrame:

    df: pd.DataFrame = pd.DataFrame.from_records(all_articles_json_list)
    #df = pd.read_json(today_file_path)
    df['text_cleaned'] = df['text'].apply(lambda text: preprocess_text(text))
    df = df[df['text_cleaned'] != '']
    X_transformers: np.ndarray = sentance_transformers_embeddings(df)
    kmeans: KMeans = KMeans(n_clusters=3, random_state=42)
    clusters: np.ndarray = kmeans.fit_predict(X_transformers)
    clusters_result_name: str = 'cluster_transformers'
    df[clusters_result_name] = clusters
    dimension_reduction(df, X_transformers, 'transformers')
    #method = "transformers"
    #plot_pca(df, f'x0_{method}', f'x1_{method}', cluster_name=clusters_result_name, method=method)
    
    return df

def get_clusters_list(df: pd.DataFrame, category: str, today_date: datetime) -> List[List[Dict[str, str]]]:
    columns_to_keep: List[str] = ['id', 'datetime','title', 'authors', 'url', 'text_cleaned', "text"]
    #rename_columns: Dict[str, str] = {'text_cleaned': 'text'}

    category_directory_path: str = f'.././data/pakistan/{today_date}/clusters/{category}'
    json_files_count = 0

    # # Walk through the directory
    # for root, dirs, files in os.walk(category_directory_path):
    #     for file in files:
    #         if file.endswith('.json'):
    #             json_files_count += 1

    cluster_directory_path = f'.././data/pakistan/{today_date}/clusters'
    if not os.path.exists(cluster_directory_path):
        os.makedirs(cluster_directory_path, exist_ok=True)
    
    #if json_files_count >= 10:
    clusters_list: List = []
    for cluster in range(3):
        df_cluster = df[df['cluster_transformers'] == cluster]
        df_cluster = df_cluster[columns_to_keep]#.rename(columns=rename_columns)

        json_data: str = df_cluster.to_json(orient='records', indent=4)
        json_objects_list: List[Dict[str: str]] = json.loads(json_data)
        
        if len(json_objects_list) <= 15:
            if not os.path.exists(category_directory_path):
                os.makedirs(category_directory_path)
            file_no: int = get_next_file_number(category_directory_path)
            filename: str = f'{category_directory_path}/{file_no}.json'

            # if not os.path.exists(category_directory_path):
            #     os.makedirs(category_directory_path, exist_ok=True)

            with open(filename, 'w') as file:
                file.write(json_data)
            
            print(f"Data saved to {filename}")

        else:
            clusters_list.append(json_objects_list)
    return clusters_list

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

def main() -> None:
    today_date: datetime = datetime.now().strftime("%Y-%m-%d")
    #today_file_path = fetch_today_file(f".././data/{today_date}/business/articles")
    categories: List[str] = ["politics", "governance", "sports", "international relations", "business", "health", "science and technology", "culture", "security", "weather", "fashion", "energy", "others"]
    #categories: List[str] = ["politics", "business"]
    
    for category in categories:
        process_clusters(category, today_date)

if __name__ == "__main__":
    columns_to_keep: List[str] = ['title', 'authors', 'source', 'url', 'text_cleaned', "text"]
    #rename_columns: Dict[str, str] = {'text_cleaned': 'text'}

    model: SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2')
    nltk.download('punkt')
    nltk.download('stopwords')

    

    main()