from datetime import datetime, timedelta
from phi.tools.newspaper4k import Newspaper4k
import time
import json
import os

articles_json: dict[str:str] = {}
list_of_articles: list[dict[str:str]] = []

def is_yesterday_before_8am(publish_date_str):
    publish_date = datetime.fromisoformat(publish_date_str)
    current_datetime = datetime.now()
    yesterday_date = current_datetime - timedelta(days=1)
    # Create datetime object for yesterday at 8 am
    yesterday_8am = datetime.combine(yesterday_date, datetime.min.time()) + timedelta(hours=8)
    return publish_date <= yesterday_8am

def get_article_content(url_object):
    news_articles = []
    urls = []
    newspaper_tool = Newspaper4k()
    for c, r in enumerate(url_object):
        try:
            if "url" in r:
                print("Article No:", c)
                article_data = newspaper_tool.get_article_data(r["url"])
                time.sleep(5)
                if is_yesterday_before_8am(article_data["publish_date"]):
                    print("Article No", c, "is under date range")
                    article_data["url"] = r["url"]
                    article_data["source"] = r["source"]
                    news_articles.append(article_data)
                    urls.append(r)
                    
        except:
            pass
    
    return news_articles

def fetch_today_file(directory):
    # Get today's date in YYYY-MM-DD format
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Construct the expected filename pattern
    expected_filename = f"all_business_urls_{today_date}.json"

    # List all files in the directory
    files = os.listdir(directory)

    # Find the file that matches today's date
    for file in files:
        if file == expected_filename:
            return os.path.join(directory, file)

    return None  # Return None if today's file is not found


if __name__ == "__main__":
    current_date = datetime.now().strftime("%Y-%m-%d")
    today_file_path = fetch_today_file(".././urls/dynamic")
    with open(today_file_path, 'r') as file:
        url_objects = json.load(file)
    articles = get_article_content(url_objects)
    with open(f'.././data/business/business_articles_{current_date}.json', 'w') as json_file:
        json.dump(articles, json_file, indent=4)

