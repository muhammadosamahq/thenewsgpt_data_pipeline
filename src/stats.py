from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from langchain_community.document_loaders import JSONLoader
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
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

llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0, model_name="gpt-4o")
#llm = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")

get_all_objects_json_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            '''Extract all statistical data from the given text and present it in JSON format. Ensure that all arrays in the JSON are of the same length and that the JSON keys have consistent and standardized headings. Use the following structure for the JSON output: 
            all_json_object_list = [
                {{
                    "object": "comprehensive and clear title of the object",
                    "headings": [], 
                    "data": []
                }},
                {{
                    "object": "comprehensive and clear title of the object",
                    "headings": [], 
                    "data": []
                }},
                {{
                    "object": "comprehensive and clear title of the object",
                    "headings": [], 
                    "data": []
                }},
                {{
                    "object": "comprehensive and clear title of the object",
                    "headings": [], 
                    "data": []
                }}
            ]
            Keep column names identical.
            If there is no statistical data in the given text, then return None.'''
        ),
        ("human", "{input}")
    ]
)

# json_schema_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             '''You are responsible for extracting all JSON objects from the given context in the following format:
#             all_json_object_list = [
#                 {{
#                     "object": "comprehensive and clear title of the object",
#                     "headings": [], 
#                     "data": []
#                 }},
#                 {{
#                     "object": "comprehensive and clear title of the object",
#                     "headings": [], 
#                     "data": []
#                 }},
#                 {{
#                     "object": "comprehensive and clear title of the object",
#                     "headings": [], 
#                     "data": []
#                 }},
#                 {{
#                     "object": "comprehensive and clear title of the object",
#                     "headings": [], 
#                     "data": []
#                 }}
#             ]
#             Note: you have to keep with this schema at any cost. If there is no JSON object, then just return None.'''
#         ),
#         ("human", "{input}")
#     ]
# )

json_objects_chain = get_all_objects_json_prompt | llm
#json_schema_chain = json_schema_prompt | llm

categories = ["business", "pakistan"]
today_date = datetime.now().date()

for category in categories:
    directory_path = f'../data/{today_date}/{category}/stats'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    clusters_path = get_all_file_paths(f"../data/{today_date}/{category}/clusters")

    all_json_objects_list = []

    for c, cluster in enumerate(clusters_path):
        with open(cluster, 'r', encoding='utf-8') as file:
            meta = json.load(file)
        docs = json_load(cluster)
        result = json_objects_chain.invoke({"input": docs})
        #final_result = json_schema_chain.invoke({"input": result.content})

        print(result.content)

        if result.content:
            try:
                # For openai llm
                all_json_objects_list = json.loads(result.content.replace('```json', '').replace('```', '').strip())
                # For google llm
                #all_json_objects_list = json.loads(result.replace('```json', '').replace('```', '').strip())
                
                print(all_json_objects_list)

                with open(f'../data/{today_date}/{category}/stats/stats_{c}.json', 'w', encoding='utf-8') as file:
                    json.dump(all_json_objects_list, file, ensure_ascii=False, indent=4)
                
                print("Data has been successfully saved to the stats folder as JSON file.")

            except:
                print(result.content)
                with open(f'../data/{today_date}/{category}/stats/stats_{c}.json', 'w', encoding='utf-8') as file:
                    json.dump(result.content, file, ensure_ascii=False, indent=4)