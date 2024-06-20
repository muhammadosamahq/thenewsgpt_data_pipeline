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
from datetime import datetime, timedelta
import seaborn as sns
import torch
import numpy as np
import time
import json
import os


def preprocess_text(text: str) -> str:
    nltk.download('punkt')
    nltk.download('stopwords')
    # Ensure text is a string
    if not isinstance(text, str):
        return ""
    # remove links
    text = re.sub(r"http\S+", "", text)
    # remove special chars and numbers
    text = re.sub("[^A-Za-z]+", " ", text)

    # remove stopwords
    tokens = nltk.word_tokenize(text)
    tokens = [w for w in tokens if not w.lower() in stopwords.words("english")]
    text = " ".join(tokens)
    text = text.lower().strip()

    return text

def fetch_today_file(directory):
    # Get today's date in YYYY-MM-DD format
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Construct the expected filename pattern
    expected_filename = f"all_business_articles_{today_date}.json"

    # List all files in the directory
    files = os.listdir(directory)

    # Find the file that matches today's date
    for file in files:
        if file == expected_filename:
            return os.path.join(directory, file)

    return None  # Return None if today's file is not found

def tfidvectorizer_embeddings(df):
    vectorizer = TfidfVectorizer(sublinear_tf=True, min_df=5, max_df=0.95)
    X = vectorizer.fit_transform(df['text_cleaned']).toarray()

def sentance_transformers_embeddings(df):
    st = time.time()

    model = SentenceTransformer('all-MiniLM-L6-v2')
    df['encode_transforemers'] = df['text_cleaned'].apply(lambda text: model.encode(text, convert_to_numpy=True).flatten())

    et = time.time()

    print("Elapsed time: {:.2f} seconds".format(et - st))

    X_transformers = np.vstack(df['encode_transforemers'])
    return X_transformers

def eval_cluster(embedding, target):
    kmeans = KMeans(n_clusters=3, random_state=42)
    y_pred = kmeans.fit_predict(embedding)
    
    # Evaluate the performance using ARI, NMI, and FMI
    ari = adjusted_rand_score(target, y_pred)
    nmi = normalized_mutual_info_score(target, y_pred)
    fmi = fowlkes_mallows_score(target, y_pred)

    # Print Metrics scores
    print("Adjusted Rand Index (ARI): {:.3f}".format(ari))
    print("Normalized Mutual Information (NMI): {:.3f}".format(nmi))
    print("Fowlkes-Mallows Index (FMI): {:.3f}".format(fmi))
    
    return y_pred

def dimension_reduction(embedding, method):

    pca = PCA(n_components=2, random_state=42)

    pca_vecs = pca.fit_transform(embedding)

    # save our two dimensions into x0 and x1
    x0 = pca_vecs[:, 0]
    x1 = pca_vecs[:, 1]
    
    df[f'x0_{method}'] = x0 
    df[f'x1_{method}'] = x1

def plot_pca(x0_name, x1_name, cluster_name, method):

    plt.figure(figsize=(12, 7))

    plt.title(f"TF-IDF + KMeans 20newsgroup clustering with {method}", fontdict={"fontsize": 18})
    plt.xlabel("X0", fontdict={"fontsize": 16})
    plt.ylabel("X1", fontdict={"fontsize": 16})

    sns.scatterplot(data=df, x=x0_name, y=x1_name, hue=cluster_name, palette="viridis")
    plt.show()


def save_cluster_to_json(df, cluster_value):
    columns_to_keep = ['title', 'authors', 'source', 'publish_date', 'url', 'text_cleaned']
    rename_columns = {'text_cleaned': 'text'}

    today_date = datetime.now().strftime("%Y-%m-%d")
    df_cluster = df[df['cluster_transformers'] == cluster_value]
    df_cluster = df_cluster[columns_to_keep].rename(columns=rename_columns)

    json_data = df_cluster.to_json(orient='records', indent=4)

    directory_path = f'.././data/{today_date}/business/clusters'
    filename = f'{directory_path}/cluster_{cluster_value}_records.json'
    
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)

    with open(filename, 'w') as file:
        file.write(json_data)
    
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    today_date = datetime.now().strftime("%Y-%m-%d")
    today_file_path = fetch_today_file(f".././data/{today_date}/business/articles")
    df = pd.read_json(today_file_path)
    df['text_cleaned'] = df['text'].apply(lambda text: preprocess_text(text))
    df = df[df['text_cleaned'] != '']
    X_transformers = sentance_transformers_embeddings(df)
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_transformers)
    clusters_result_name = 'cluster_transformers'
    df[clusters_result_name] = clusters
    dimension_reduction(X_transformers, 'transformers')
    method = "transformers"
    #plot_pca(f'x0_{method}', f'x1_{method}', cluster_name=clusters_result_name, method=method)
    
    for cluster in [0, 1, 2]:
        save_cluster_to_json(df, cluster)
    

     #Elbow method
    # sse = []
    # k_rng = range(1,10)
    # for k in k_rng:
    #     kmeans = KMeans(n_clusters=k, random_state=42)
    #     kmeans.fit(df[['x0_transformers','x1_transformers']])
    #     sse.append(kmeans.inertia_)

    # plt.xlabel('K')
    # plt.ylabel('Sum of squared error')
    # plt.plot(k_rng,sse)
    