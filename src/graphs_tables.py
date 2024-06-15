from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime, timedelta
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import os
import re

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
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "you are an assisstent to generate then return most relevent tables from given content only if applicable in pandas dataframe",
        ),
        ("human", "{input}"),
    ]
)

    
    llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0, model_name="gpt-4o-2024-05-13")
    #llm = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")
    chain = prompt | llm

    st.set_page_config(page_title="News Summary", page_icon="💁")
    st.header("A bot for latest Pakistani news💁")

    today_date = datetime.now().strftime("%Y-%m-%d")
    clusters_path = get_all_file_paths(f".././clusters/business/{today_date}")

    for c, cluster in enumerate(clusters_path):
        docs = json_load(cluster)
        result = chain.invoke({"input": docs})
        #data_list.append(result["output_text"])
        #print(result["output_text"])
        r = result.content.split("Table")
        data_list.append(r)
        
        print(r)

    #extracted_code = re.search(r'data = \{.*?pd.DataFrame\(data\)', data_list[0][3], re.DOTALL).group(0)
    #exec(extracted_code)
    st.write(data_list)
    #st.table(df_wage_salary_increase)