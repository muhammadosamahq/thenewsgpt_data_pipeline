import os
import json
from datetime import datetime

today_date = datetime.now().strftime("%Y-%m-%d")

# Set the directories
raw_articles_dir = f'./../data/pakistan/{today_date}/raw_articles'
articles_dir = f'./../data/pakistan/{today_date}/articles'

# Create the articles directory if it doesn't exist
if not os.path.exists(articles_dir):
    os.makedirs(articles_dir, exist_ok=True)

# Dictionary to track URLs and corresponding file paths
url_tracker = {}
unique_articles = []


# List to keep track of processed files
processed_files = []

def filter_articles():
    current_id = 1
    # Iterate through each JSON file in the raw_articles directory
    for filename in os.listdir(raw_articles_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(raw_articles_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    article = json.load(file)
                    url = article.get('url')
                    if url:
                        if url in url_tracker:
                            print(f"Duplicate URL found: {url} in {filename} (already exists in {url_tracker[url]})")
                        else:
                            url_tracker[url] = filename
                            article['id'] = current_id
                            unique_articles.append(article)
                            current_id += 1
                            processed_files.append(filename)
                except json.JSONDecodeError as e:
                    print(f"Error reading {filename}: {e}")

    # Save the unique articles to the articles directory
    for article in unique_articles:
        new_filename = f"{article['id']}.json"
        new_filepath = os.path.join(articles_dir, new_filename)
        with open(new_filepath, 'w', encoding='utf-8') as file:
            json.dump(article, file, ensure_ascii=False, indent=4)

    # Print the count of files in raw_articles and articles
    raw_files_count = len([name for name in os.listdir(raw_articles_dir) if name.endswith('.json')])
    articles_count = len(unique_articles)

    print(f"Total files in raw_articles: {raw_files_count}")
    print(f"Total unique articles saved: {articles_count}")

if __name__ == "__main__":
    filter_articles()
