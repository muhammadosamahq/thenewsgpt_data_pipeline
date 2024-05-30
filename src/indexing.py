from langchain.text_splitter import NLTKTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_chroma import Chroma
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
import os

load_dotenv()
# os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def clean_combine_text(data):
    text = ""
    for c, object in enumerate(data):
        print(c)
        text += object['content'].split('SearchSearch')[-1]
    return text

def fetch_json_by_date(directory, date_str=None): # for custom date_str format "2024-05-26" 
    if date_str is None:
        target_date = date.today()  # Set default value to today's date
    else:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    for filename in os.listdir(directory):

        if filename.endswith(".json"):

            try:
                file_date_str = filename.split("_")[2]
                file_date = datetime.strptime(file_date_str.split(' ')[0], "%Y-%m-%d").date()
                
                if file_date == target_date:
                    file_path = os.path.join(directory, filename)
                    loader = JSONLoader(
                                file_path=file_path,
                                jq_schema=".[] | .content",
                                text_content=False
                                )
                    return loader.load()
                    
            except (IndexError, ValueError):
                continue

    return None

def json_directory_loader(dir_path):
    loader = DirectoryLoader(
    dir_path, 
    glob="**/*.json", 
    loader_cls=JSONLoader,
    loader_kwargs={'jq_schema': '.[] | .content'}
    )
    documents = loader.load()
    return documents

def NLTKchunking(text, chunk_size):
    text_splitter = NLTKTextSplitter(chunk_size=chunk_size)
    chunks = text_splitter.split_text(text)
    print('created', len(chunks), 'number of chunks', 'text lenght is', len(text))
    return chunks

def recursivecharacterchunking(docs, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_documents(docs)
    print('created', len(chunks), 'number of chunks', 'docs lenght is', len(docs))
    return chunks

def save_embeddings_to_vectorstore(chunks):
    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store_path = "chroma_db"

    try:
        # Check if the vector store file exists
        if os.path.isdir(vector_store_path):
            # Load existing vector store
            #vector_store = FAISS.load_local(vector_store_path, embeddings_model, allow_dangerous_deserialization=True)
            #print('Loaded existing vector store with', vector_store.index.ntotal, 'records')
            vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings_model)
            print('Loaded existing vector store with', vector_store._collection.count(), 'records')
            vector_store.add_documents(chunks)
            print('New docs added in vectore store', vector_store._collection.count(), 'records')
        else:
            # If vector store file does not exist, create a new one
            #vector_store = FAISS.from_documents(chunks, embedding=embeddings_model)
            #vector_store.save_local(vector_store_path)
            print('Vector store not found, creating new vector store.......')
            vector_store = Chroma.from_documents(chunks, embeddings_model, persist_directory="./chroma_db")
            print('created new vector store with', vector_store._collection.count(), 'records')
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    date_list = ["2024-05-23", "2024-05-24", "2024-05-25", "2024-05-26", "2024-05-27", "2024-05-28", "2024-05-29"]
    for l in date_list:
        docs = fetch_json_by_date('../data/dawn_articles', l) # for custom use parameter date_str="2024-05-26" 
        #text = clean_combine_text(data)
        if docs:
            chunks = recursivecharacterchunking(docs, 500, 100)
            save_embeddings_to_vectorstore(chunks)
        else:
            print('json is not present on specified date')
    

