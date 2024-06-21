from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime, timedelta
from langchain_community.document_loaders import JSONLoader
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI
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

today_date = datetime.now().date()
directory_path = f'.././data/{today_date}/business/stats'
if not os.path.exists(directory_path):
    os.makedirs(directory_path)

llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0, model_name="gpt-4o-2024-05-13")
#llm = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            '''Extract all statistical data from the given text and present it in JSON format. Ensure that all arrays in the JSON are of the same length and that the JSON keys have consistent and standardized headings. Use the following structure for the JSON output: {{
    "object": "title of the object"
    "headings": [], 
    "data": [],

    return all json objects in a list named all_json_object_list = []

    if there is no statistical data in given text then return None
}}'''
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm

today_date = datetime.now().strftime("%Y-%m-%d")
clusters_path = get_all_file_paths(f"../data/{today_date}/business/clusters")

all_json_objects_list = []

for c, cluster in enumerate(clusters_path):
    with open(cluster, 'r', encoding='utf-8') as file:
        meta = json.load(file)
    docs = json_load(cluster)
    result = chain.invoke({"input": docs})
    # For openai llm
    all_json_objects_list = json.loads(result.content.replace('```json', '').replace('```', '').strip())
    # For google llm
    #all_json_objects_list = json.loads(result.replace('```json', '').replace('```', '').strip())
    
    print(all_json_objects_list)

    with open(f'.././data/{today_date}/business/stats/stats_{c}.json', 'w', encoding='utf-8') as file:
        json.dump(all_json_objects_list, file, ensure_ascii=False, indent=4)
    
    print("Data has been successfully saved to the existing JSON file.")


        #st.write(f"**Summary {c}:**", summarization_result["output_text"])
        #print(result["output_text"])

        
        # r = result.content.split("Object")
        # print(r)
        # for c, data in enumerate(r):
            
        #     #st.write(data)
        #     if c == 0:
        #         print("first indices")
        #     else:
        #         heading = data.split("```")[0].strip() 
        #         d = convert_to_dict(data.split("```")[1].replace("json", "").strip())
        #         tables["heading"]= heading
        #         tables["data"] = d
        #         no_of_tables.append(tables)
        #         if "heading" in d.keys():
        #             del d["heading"]
        #         # Get the maximum length of any array in the data
        #         my_data = dict([ (k, pd.Series(v)) for k,v in d.items() ])
        #         # Create a DataFrame with column names set to the keys
        #         df = pd.DataFrame.from_dict(my_data)
        #         #st.write(heading)
        #         #st.table(df)
        #         tables = {}
                    
        # #tables_data.extend(no_of_tables)
        # # print(len(tables_data))

        # summery_dict["stats"] = no_of_tables
        # no_of_tables = []
        
        


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