from duckduckgo_search import DDGS
from phi.tools.newspaper4k import Newspaper4k
from datetime import datetime
import json

news_articles = []
article_topic = 'what is latest in pakistan?'
ddgs = DDGS()
newspaper_tool = Newspaper4k()
results=ddgs.text(article_topic, max_results=200)

for r in results:
    if "href" in r:
        article_data = newspaper_tool.get_article_data(r["href"])

        if article_data and "text" in article_data:
            r["text"] = article_data["text"]
            news_articles.append(r)
        
        if article_data and "publish_date" in article_data:
            r["publish_date"] = article_data["publish_date"]

timestamp = datetime.now()
with open(f'../data/google_articles/google_articles_{timestamp}.json', 'w') as file:
    json.dump(news_articles, file, indent=4)