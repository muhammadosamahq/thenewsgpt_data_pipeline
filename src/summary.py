from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
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

def is_json_file_not_empty(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            # If the file cannot be decoded, it might be completely empty or malformed
            return False
    
    # Check if the data is an empty object or array
    if data == {} or data == []:
        return False
    
    # Check if the file is completely empty
    with open(file_path, 'r', encoding='utf-8') as file:
        if file.read().strip() == '':
            return False

    return True

# def convert_to_dict(string):
#     data_dict = ast.literal_eval(string)
    
#     return data_dict

def get_save_summary_stats(clusters_directory_path: List[str], summary_directory_path: str) -> None:  
    g_llm: GoogleGenerativeAI = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")

    # Define prompt
    summary_prompt_template = """Write a comprehensive summary of the following:
    "{text}" 
    Summary:
    """
    heading_prompt_template = """Write a clear and proper heading of following given summary return only most relevent one:
    "{text}" 
    Heading:
    """

    summary_prompt = PromptTemplate.from_template(summary_prompt_template)
    heading_prompt = PromptTemplate.from_template(heading_prompt_template)

    # Define LLM chain
    summary_llm_chain = LLMChain(llm=g_llm, prompt=summary_prompt)
    heading_llm_chain = heading_prompt | g_llm

    # Define StuffDocumentsChain
    summarization_chain = StuffDocumentsChain(llm_chain=summary_llm_chain, document_variable_name="text")

    # g_llm: GoogleGenerativeAI = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")
    # summarization_chain = load_summarize_chain(g_llm, chain_type="stuff")
    for c, cluster in enumerate(clusters_directory_path):
        print(cluster)
        # Extract the last part of the path
        last_part: str = cluster.split('/')[-1]

        # Extract the number before .json
        id: str = last_part.split('.')[0]

        json_file = is_json_file_not_empty(cluster)
        if json_file:
            with open(cluster, 'r', encoding='utf-8') as file:
                meta: List[Dict[str, Union[str, int, List[str]]]] = json.load(file)
            #print(meta)
        
            docs: List[Document] = json_load(cluster)
            #result = chain.invoke({"input": docs})
            summarization_result: Dict = summarization_chain.invoke(docs)
            time.sleep(3)
            heading_result = heading_llm_chain.invoke({"text": summarization_result["output_text"]})
            print("generated summary", id)
            metadata_list: List[Dict[str, Union[str, int, List[str]]]] = [obj for obj in meta]
            for idx, meta in enumerate(metadata_list):
                meta["id"] = idx
                
            #len(metadata_list)
            filename: str = f'{summary_directory_path}/{id}.json'

            summery_dict: Dict[str, Union[str, List[Any]]] = {
                            "id": int(id),
                            "heading": heading_result,
                            "summary": summarization_result["output_text"],
                            "meta_data": metadata_list,}

            with open(filename, 'w') as json_file:
                json.dump(summery_dict, json_file, indent=4) 
                print("saved summary", id)

            time.sleep(5)

def main():
    today_date: datetime.date = datetime.now().date()
    categories: List[str] = ["politics", "governance", "sports", "international relations", "business", "health", "science and technology", "culture", "security", "weather", "fashion", "energy", "others"]
    for category in categories:
        summary_directory_path: str = f'.././data/pakistan/{today_date}/summary/{category}'
        if not os.path.exists(summary_directory_path):
            os.makedirs(summary_directory_path)

        clusters_directory_path: List[str] = get_all_file_paths(f".././data/pakistan/{today_date}/clusters/{category}")
        get_save_summary_stats(clusters_directory_path, summary_directory_path)

if __name__ == "__main__":
    #o_llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0, model_name="gpt-4o")
    g_llm: GoogleGenerativeAI = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")
    summarization_chain = load_summarize_chain(g_llm, chain_type="stuff")

    main()

    