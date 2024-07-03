import os
import json
from typing import List
from datetime import datetime

# Function to get all file paths in a directory
def get_all_file_paths(directory: str) -> List[str]:
    file_paths: List[str] = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path: str = os.path.join(root, file)
            file_paths.append(file_path)
    return file_paths

# Get today's date
today_date = datetime.now().date()

# Function to flatten nested lists
def flatten_list(nested_list):
    return [item for sublist in nested_list for item in (sublist if isinstance(sublist, list) else [sublist])]

categories: List[str] = ["politics", "business"]

for category in categories:
    
    # Directory containing the stats JSON files
    stats_directory_path = get_all_file_paths(f".././data/pakistan/{today_date}/stats/{category}")
    print(stats_directory_path)

    # Directory to save filtered JSON files
    directory = f'.././data/pakistan/{today_date}/stats/{category}'

    # Create the testing folder if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    for stat in stats_directory_path:
        with open(stat, 'r', encoding='utf-8') as file:
            stats_json_list = json.load(file)

        # Check each object in stats_json_list
        filtered_stats = []
        seen_objects = set()
        
        for item in stats_json_list:
            # Flatten the lists inside 'data' if they contain nested lists
            data_values = flatten_list(item['data'])
            
            # Check if any value in 'data' is numerical
            # if not any(any(char.isdigit() for char in str(value)) for value in data_values):
            #     continue

            # Check if all values in 'data' and 'headings' are the same
            if len(set(data_values)) == 1 or len(set(item['headings'])) == 1:
                continue

            # Check if the object is repeating
            if item['object'] in seen_objects:
                continue

            seen_objects.add(item['object'])
            filtered_stats.append(item)

        # Save the filtered list to a new file in the testing folder
        base_filename = os.path.basename(stat)
        new_filename = os.path.join(directory, base_filename)

        with open(new_filename, 'w', encoding='utf-8') as outfile:
            json.dump(filtered_stats, outfile, indent=4)

        print(f"Processed {stat}")
        print(f"Filtered results saved to {new_filename}")
        print(f"Original length: {len(stats_json_list)}, Filtered length: {len(filtered_stats)}")