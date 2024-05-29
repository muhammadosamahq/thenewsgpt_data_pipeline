import nest_asyncio
from typing import Optional

import streamlit as st 
from duckduckgo_search import DDGS

from phi.tools.newspaper4k import Newspaper4k

import os
import openai
import json

from dotenv import load_dotenv

load_dotenv()

news_articles = []
article_topic = 'what are good tips about gym?'
ddgs = DDGS()
newspaper_tool = Newspaper4k()
results=ddgs.text(article_topic, max_results=5)

for r in results:
    if "href" in r:
        article_data = newspaper_tool.get_article_data(r["href"])

        if article_data and "text" in article_data:
            r["text"] = article_data["text"]
            news_articles.append(r)
        
        if article_data and "publish_date" in article_data:
            r["publish_date"] = article_data["publish_date"]

with open('../data/google_articles/testing.json', 'w') as file:
    json.dump(news_articles, file, indent=4)