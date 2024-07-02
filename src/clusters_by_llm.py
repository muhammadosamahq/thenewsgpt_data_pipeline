from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from dotenv import load_dotenv
import json
import os
import shutil

load_dotenv()

today_date = datetime.now().strftime("%Y-%m-%d")
categories_dir = f'./../data/pakistan/{today_date}/categories'
articles_dir = f".././data/pakistan/{today_date}/articles"
raw_articles_dir = f".././data/pakistan/{today_date}/raw_articles"

def json_directory_loader(dir_path):
    loader = DirectoryLoader(
        dir_path, 
        glob="**/*.json", 
        loader_cls=JSONLoader,
        #loader_kwargs={'jq_schema': '.[] | {id: .id, text: .text}', 'text_content': False}
        loader_kwargs={'jq_schema': '.', 'text_content': False}
    )
    documents = loader.load()
    return documents

# Function to move JSON files to category folders
def move_article_to_category_folder(article_id, category):
    src_filepath = os.path.join(articles_dir, f'{article_id}.json')
    if os.path.exists(src_filepath):
        dest_dir = os.path.join(categories_dir, category)
        dest_filepath = os.path.join(dest_dir, f'{article_id}.json')
        shutil.move(src_filepath, dest_filepath)
        print(f'Moved {src_filepath} to {dest_filepath}')
    else:
        print(f'File {src_filepath} does not exist')

llm: GoogleGenerativeAI = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")

prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                '''you are given a list of documents with their content and IDs. Please classify each document into one of the following categories: ["politics", "governance", "sports", "international relations", "business", "health", "science and technology", "culture", "security", "weather", "fashion", "energy", "others"]
                   return output as follows in json:
                   {{
                        "id": 34,
                        "category": "business"
                    }}
                '''
            ),
            ("human", "{input}")
        ]
    )

chain = prompt | llm


if not os.path.exists(categories_dir):
    os.makedirs(categories_dir, exist_ok=True)

today_date = datetime.now().strftime("%Y-%m-%d")
docs = json_directory_loader(articles_dir)

categories = ["politics", "governance", "sports", "international relations", "business", "health", "science and technology", "culture", "security", "weather", "fashion", "energy", "others"]
for category in categories:
    if not os.path.exists(os.path.join(categories_dir, category)):
        os.makedirs(os.path.join(categories_dir, category), exist_ok=True)

print("llm processing....")
result = chain.invoke({"input": docs})
print("got cluster results by llm")

all_json_objects_list = json.loads(result.replace('```json', '').replace('```', '').strip())

category_counts = {}

# Iterate through the list of documents
for doc in all_json_objects_list:
    category = doc['category']
    if category in category_counts:
        category_counts[category] += 1
    else:
        category_counts[category] = 1

# Display the counts
for category, count in category_counts.items():
    print(f"{category}: {count}")


# Iterate through the list and move JSON files to respective category folders
for item in all_json_objects_list:
    article_id = item['id']
    category = item['category']
    if category in categories:
        move_article_to_category_folder(article_id, category)
    else:
        print(f'Unknown category: {category}')

# Check if the directory exists before attempting to delete
# if os.path.exists(articles_dir):
#     shutil.rmtree(articles_dir)
#     print(f"Directory {articles_dir} and all its contents have been deleted.")

# if os.path.exists(raw_articles_dir):
#     shutil.rmtree(raw_articles_dir)
#     print(f"Directory {raw_articles_dir} and all its contents have been deleted.")
