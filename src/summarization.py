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
import ast # convert string to dict
import json
import time
from typing import Tuple, List, Any, Dict, Union
from langchain.schema import Document

load_dotenv()

def get_all_file_paths(directory: str) -> List[str]:
    file_paths: List[str] = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path: str = os.path.join(root, file)
            file_paths.append(file_path)
    return file_paths

def json_load(file_path: str) -> List[str]:
    loader: JSONLoader = JSONLoader(
                            file_path=file_path,
                            jq_schema=".[] | .text",
                            text_content=False
                            )
    return loader.load()

# def convert_to_dict(string):
#     data_dict = ast.literal_eval(string)
    
#     return data_dict

def get_save_summary_stats(clusters_directory_path: List[str], summary_directory_path: str) -> None:  
    for c, cluster in enumerate(clusters_directory_path):
        # Extract the last part of the path
        last_part: str = cluster.split('/')[-1]

        # Extract the number before .json
        id: str = last_part.split('.')[0]

        with open(cluster, 'r', encoding='utf-8') as file:
            meta: List[Dict[str, Union[str, int, List[str]]]] = json.load(file)
        docs: List[Document] = json_load(cluster)
        #result = chain.invoke({"input": docs})
        summarization_result: Dict = summarization_chain.invoke(docs)

        metadata_list: List[Dict[str, Union[str, int, List[str]]]] = [obj for obj in meta]
        #len(metadata_list)
        filename: str = f'{summary_directory_path}/{id}.json'
        summery_dict: Dict[str, Union[str, List[Any]]] = {"summary": summarization_result["output_text"],
                        "meta_data": metadata_list,}

        with open(filename, 'w') as json_file:
            json.dump(summery_dict, json_file, indent=4) 
        
        time.sleep(5)

def main():
    today_date: datetime.date = datetime.now().date()
    categories: list[str] = ["business", "pakistan"]
    for category in categories:
        summary_directory_path: str = f'.././data/{today_date}/{category}/summary'
        if not os.path.exists(summary_directory_path):
            os.makedirs(summary_directory_path)

        clusters_directory_path: List[str] = get_all_file_paths(f".././data/{today_date}/{category}/clusters")
        get_save_summary_stats(clusters_directory_path, summary_directory_path)

if __name__ == "__main__":
    #o_llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0, model_name="gpt-4o")
    g_llm: GoogleGenerativeAI = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")
    summarization_chain = load_summarize_chain(g_llm, chain_type="stuff")

    main()

    