from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from langchain_community.document_loaders import JSONLoader
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
import os
import json
import re
from typing import Tuple, List, Any, Dict, Union

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

def clean_json_string(json_string):
    # Remove trailing commas before closing brackets and braces
    json_string = re.sub(r',\s*([\]}])', r'\1', json_string)
    # Remove trailing commas before closing square brackets in arrays
    json_string = re.sub(r',\s*]', r']', json_string)
    return json_string

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

def get_chain():
    #llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0, model_name="gpt-4o")
    llm = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                '''Extract all statistical data from the given text and present it in JSON format. Ensure that all arrays in the JSON are of the same length and that the JSON keys have consistent and standardized headings. Use the following structure for the JSON output: 
                ```json 
                all_json_object_list = [
                    {{
                        "object": "comprehensive and clear title of the object as well as mentioned the administrative unit if applicable",
                        "headings": [], 
                        "data": []
                    }},
                    ..........
                ]
                ```
                it is must to Keep column names identical and values must be identical as well and there is no repetetion oj same json objects its your job you have to do it in a correct as told you.
                
                Note: most import thing is only create high quality json objects and ignore less qualitative stats. dont create extra delimiter.
                If there is no statistical data in the given text, then return None.'''
            ),
            ("human", "{input}")
        ]
    )

    chain = prompt | llm
    return chain

def create_stats(category, clusters_directory_path):
    stats_chain = get_chain()
    today_date = datetime.now().date()
    # directory_path = f'.././data/pakistan/{today_date}/stats/{category}'
    # if not os.path.exists(directory_path):
    #     os.makedirs(directory_path)

    all_json_objects_list = []

    for c, cluster in enumerate(clusters_directory_path):
        # Extract the last part of the path
        last_part = cluster.split('/')[-1]

        # Extract the number before .json
        id = last_part.split('.')[0]
        json_file = is_json_file_not_empty(cluster)
        if json_file:
            summary_path = f".././data/pakistan/{today_date}/summary/{category}/{id}.json"
            with open(summary_path, 'r', encoding='utf-8') as file:
                summary = json.load(file)
            docs = json_load(cluster)
            result = stats_chain.invoke({"input": docs})
            
            #final_result = json_schema_chain.invoke({"input": result.content})

            #print(result.content)
            print(result)
            #if result.content:
            if result:
                try:
                    # For openai llm
                    # cleaned_json_string = clean_json_string(result.content.replace('```json', '').replace('```', '').strip())
                    # all_json_objects_list = json.loads(cleaned_json_string)
                    #all_json_objects_list = json.loads(("["+result.content.split("[")).strip())
                    # For google llm
                    all_json_objects_list = json.loads(result.replace('```json', '').replace('```', '').strip())
                    summary["stats"] = all_json_objects_list
                    #print(summary)
                    ##print(all_json_objects_list)

                    with open(f'.././data/pakistan/{today_date}/summary/{category}/{id}.json', 'w') as file:
                        json.dump(summary, file, indent=4)
                    # with open(f'../data/pakistan/{today_date}/stats/{category}/{id}.json', 'w', encoding='utf-8') as file:
                    #     json.dump(summary, file, ensure_ascii=False, indent=4)
                    
                    print("Data has been successfully saved to the stats folder as JSON file.")

                        # print(result.content)
                        # with open(f'../data/{today_date}/{category}/stats/stats_{c}.json', 'w', encoding='utf-8') as file:
                        #     json.dump(result.content, file, ensure_ascii=False, indent=4)
                
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    print(result)
                    continue

def main():
    today_date = datetime.now().strftime("%Y-%m-%d")
    categories: List[str] = ["politics", "governance", "sports", "international relations", "business", "health", "science and technology", "culture", "security", "weather", "fashion", "energy", "others"]
    for category in categories:
        clusters_directory_path = get_all_file_paths(f".././data/pakistan/{today_date}/clusters/{category}")
        create_stats(category, clusters_directory_path)

if __name__ == "__main__":
    main()