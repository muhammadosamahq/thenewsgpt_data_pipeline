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
    today_date = datetime.now().date()
    directory_path = f'.././summarization/{today_date}/business'
    if not os.path.exists(f"{directory_path}/summary"):
        os.makedirs(f"{directory_path}/summary")
    
    data_list = []
    no_of_tables = []
    tables_data = []
    rejected = []
    tables = {}

    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "you are an assisstent to generate then return most relevent tables from given content of numerical statistics only if applicable in json objects must be as e.g Object 1: Government Departments and Institutions\n```json\ headings of table must be clear and proper and provide table in a json objects form where All arrays must be of the same length"
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
        with open(cluster, 'r', encoding='utf-8') as file:
            meta = json.load(file)
        docs = json_load(cluster)
        result = chain.invoke({"input": docs})
        summarization_result = summarization_chain.invoke(docs)
        metadata_list = [obj for obj in meta]
        #len(metadata_list)
        filename = f'{directory_path}/summary/summary_{c}.json'
        summery_dict = {"summary": summarization_result["output_text"],
                        "meta_data": metadata_list}
        
        data_list.append(summarization_result["output_text"])
        
        st.write(f"**Summary {c}:**", summarization_result["output_text"])
        #print(result["output_text"])

        
        r = result.content.split("Object")
        print(r)
        for c, data in enumerate(r):
            
            #st.write(data)
            if c == 0:
                print("first indices")
            else:
                heading = data.split("```")[0].strip() 
                d = convert_to_dict(data.split("```")[1].replace("json", "").strip())
                tables["heading"]= heading
                tables["data"] = d
                no_of_tables.append(tables)
                if "heading" in d.keys():
                    del d["heading"]
                # Get the maximum length of any array in the data
                my_data = dict([ (k, pd.Series(v)) for k,v in d.items() ])
                # Create a DataFrame with column names set to the keys
                df = pd.DataFrame.from_dict(my_data)
                st.write(heading)
                st.table(df)
                tables = {}
                    
        #tables_data.extend(no_of_tables)
        # print(len(tables_data))

        summery_dict["stats"] = no_of_tables

        with open(filename, 'w') as json_file:
            json.dump(summery_dict, json_file, indent=4) 


    # for obj in tables_data:
    #     st.write(obj["heading"])
    #     df = pd.DataFrame.from_dict(obj["data"])
    #     df = df.drop_duplicates()
    #     st.table(df)
    # st.write(tables["heading"])
    # df = pd.DataFrame.from_dict(t["data"])
    # df = df.drop_duplicates()
    # st.table(df)
      
    
    # for t in no_of_tables:
  
    #     st.write(t["heading"])
    #     df = pd.DataFrame.from_dict(t["data"])
    #     df = df.drop_duplicates()
    #     st.table(df)



    
    #extracted_code = re.search(r'data = \{.*?pd.DataFrame\(data\)', data_list[0][3], re.DOTALL).group(0)
    #exec(extracted_code)
    #st.write(no_of_tables)
    #st.table(df_wage_salary_increase)