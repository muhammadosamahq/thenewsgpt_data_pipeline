from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import GoogleGenerativeAI
from datetime import datetime, timedelta
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import streamlit as st
import os

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

if __name__ == "__main__":
    data_list = []
    #llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0, model_name="gpt-4o-2024-05-13")
    llm = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")
    chain = load_summarize_chain(llm, chain_type="stuff")
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    clusters_path = get_all_file_paths(f".././clusters/business/{today_date}")

    st.set_page_config(page_title="News Summary", page_icon="💁")
    st.header("A bot for latest Pakistani news💁")
   
    for c, cluster in enumerate(clusters_path):
        docs = json_load(cluster)
        result = chain.invoke(docs)
        data_list.append(result["output_text"])
        print(result["output_text"])
        
    st.write(f"Summary 1: ", data_list[0])
    st.write(f"Summary 2: ", data_list[1])
    st.write(f"Summary 3: ", data_list[2])
        