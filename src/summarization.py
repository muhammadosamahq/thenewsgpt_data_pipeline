from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime, timedelta
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import os
import re
import ast # convert string to dict
import json
import time

load_dotenv()

def get_all_file_paths(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    return file_paths

def json_load(file_path):
    loader = JSONLoader(
                            file_path=file_path,
                            jq_schema=".[] | .text",
                            text_content=False
                            )
    return loader.load()

def convert_to_dict(string):
    data_dict = ast.literal_eval(string)
    
    return data_dict

def get_save_summary_stats(clusters_path):
    for c, cluster in enumerate(clusters_path):
        # Extract the last part of the path
        last_part = cluster.split('/')[-1]

        # Extract the number before .json
        id = last_part.split('.')[0]

        with open(cluster, 'r', encoding='utf-8') as file:
            meta = json.load(file)
        docs = json_load(cluster)
        #result = chain.invoke({"input": docs})
        summarization_result = summarization_chain.invoke(docs)

        metadata_list = [obj for obj in meta]
        #len(metadata_list)
        filename = f'{directory_path}/{id}.json'
        summery_dict = {"summary": summarization_result["output_text"],
                        "meta_data": metadata_list,}

        with open(filename, 'w') as json_file:
            json.dump(summery_dict, json_file, indent=4) 
        
        time.sleep(5)

if __name__ == "__main__":
    #o_llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0, model_name="gpt-4o")
    g_llm = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")
    summarization_chain = load_summarize_chain(g_llm, chain_type="stuff")

    today_date = datetime.now().date()
    categories = ["business", "pakistan"]
    for category in categories:
        directory_path = f'.././data/{today_date}/{category}/summary'
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        clusters_path = get_all_file_paths(f".././data/{today_date}/{category}/clusters")
        get_save_summary_stats(clusters_path)

    