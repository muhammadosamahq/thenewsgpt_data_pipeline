from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from prompt_template import prompt_template
from dotenv import load_dotenv
import streamlit as st
import json
from datetime import datetime, timedelta
import os

load_dotenv()

def get_conversational_chain():
    model = GoogleGenerativeAI(google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")
    #model = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question", "date"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def input_response(query):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = db.similarity_search(query, k=2, fetch_k=8)
    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
    return response 

def main():
    st.set_page_config(page_title="Chat PDF", page_icon="💁")
    st.header("A bot for latest Pakistani news💁")
    
    # Date selection bar
    today = datetime.today().date()
    one_week_ago = today - timedelta(days=7)
    input_date = st.date_input("Select a date", value=today, min_value=one_week_ago, max_value=today)

    user_question = st.text_input("Ask a question about latest Pakistani news")
    query = user_question + " according to the date " + str(input_date)
    if user_question:
        response = input_response(query)
        st.write("Reply: ", response["output_text"])


# def opanai_google_response(user_question):
#     google_model = GoogleGenerativeAI(google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")
#     openai_model = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
#     prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
#     google_chain = load_qa_chain(google_model, chain_type="stuff", prompt=prompt)
#     openai_chain = load_qa_chain(openai_model, chain_type="stuff", prompt=prompt)
#     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#     db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
#     docs = db.similarity_search(user_question)
#     google_response = google_chain({"context": docs, "question": user_question}, return_only_outputs=True)
#     openai_response = openai_chain({"context": docs, "question": user_question}, return_only_outputs=True)
#     return {'google_response': google_response, 'openai_response': openai_response}  

# def main():
#     st.set_page_config(page_title="Chat PDF", page_icon="💁")
#     st.header("A bot for latest Pakistani news💁")
    
#     # Input for user question
#     user_question = st.text_input("Ask a question about the latest Pakistani news")
    
#     if user_question:
#         # Get responses from both models
#         responses = opanai_google_response(user_question)
        
#         # Display responses
#         st.write("Google Response: ", responses['google_response']["output_text"])
#         st.write("OpenAI Response: ", responses['openai_response']["output_text"])

if __name__ == "__main__":
    main()