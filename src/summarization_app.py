from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime, timedelta
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from datetime import datetime, timedelta
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import os
import re
import ast # convert string to dict
import json

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

if __name__ == "__main__":
    data_list = []
    no_of_tables = []
    tables_data = []
    rejected = []
    tables = {}

    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "you are an assisstent to generate then return most relevent tables from given content only if applicable in pandas dataframe as e.g object 1: # heading: headings of table must be clear and proper and and provide table in a dict form where All arrays must be of the same length"
        ),
        ("human", "{input}"),
    ]
)

    
    llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0, model_name="gpt-4o-2024-05-13")
    #llm = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")
    summarization_chain = load_summarize_chain(llm, chain_type="stuff")
    chain = prompt | llm

    st.set_page_config(page_title="News Summary", page_icon="💁")
    st.header("A bot for latest Pakistani news💁")

    today_date = datetime.now().strftime("%Y-%m-%d")
    clusters_path = get_all_file_paths(f".././clusters/business/{today_date}")

    for c, cluster in enumerate(clusters_path):
        docs = json_load(cluster)
        result = chain.invoke({"input": docs})
        summarization_result = summarization_chain.invoke(docs)
        data_list.append(summarization_result["output_text"])
        
        st.write(f"**Summary {c}:**", summarization_result["output_text"])
        #print(result["output_text"])
        r = result.content.split("Table")
        for c, data in enumerate(r):
            if c == 0:
                print(c, data)
            else:
                try:
                    tables["id"] = c
                    tables["heading"] = data.split("```")[0]
                    tables["data"] = convert_to_dict("{" + data.split("{")[1].split("df")[0])
                    st.write(data.split("```")[0])
                    df = pd.DataFrame.from_dict(convert_to_dict("{" + data.split("{")[1].split("df")[0]))
                    df = df.drop_duplicates()
                    st.table(df)
                    no_of_tables.append(tables)
                    tables = {}
                
                except:
                    pass
        tables_data.extend(no_of_tables)
        print(len(tables_data))
 


    # for obj in tables_data:
    #     st.write(obj["heading"])
    #     df = pd.DataFrame.from_dict(obj["data"])
    #     df = df.drop_duplicates()
    #     st.table(df)
    # st.write(tables["heading"])
    # df = pd.DataFrame.from_dict(t["data"])
    # df = df.drop_duplicates()
    # st.table(df)
    # with open('sample.json', 'w') as json_file:
    #     json.dump(tables_data, json_file, indent=4)   
    
    # for t in no_of_tables:
  
    #     st.write(t["heading"])
    #     df = pd.DataFrame.from_dict(t["data"])
    #     df = df.drop_duplicates()
    #     st.table(df)



    # with open('rejeced.json', 'w') as json_file:
    #     json.dump(rejected, json_file, indent=4)
    #extracted_code = re.search(r'data = \{.*?pd.DataFrame\(data\)', data_list[0][3], re.DOTALL).group(0)
    #exec(extracted_code)
    #st.write(no_of_tables)
    #st.table(df_wage_salary_increase)