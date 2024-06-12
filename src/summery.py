from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import GoogleGenerativeAI
import os



llm = GoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash-latest")

chain = load_summarize_chain(llm, chain_type="stuff")