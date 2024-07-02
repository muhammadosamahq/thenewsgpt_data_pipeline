from datetime import datetime
import os
import json

# Path to the categories folder
today_date = datetime.now().strftime("%Y-%m-%d")
categories_dir = f'./../data/pakistan/{today_date}/categories'

# Iterate through each subfolder in the categories folder
for category in os.listdir(categories_dir):
    category_path = os.path.join(categories_dir, category)
    if os.path.isdir(category_path):
        print(category_path)
        # Collect all JSON files in the current category folder
        json_files = [f for f in os.listdir(category_path) if f.endswith('.json')]
        
        # Sort JSON files based on their numeric ID in the filename
        json_files.sort(key=lambda x: int(os.path.splitext(x)[0]))

        new_id = 1

        for old_filename in json_files:
            old_filepath = os.path.join(category_path, old_filename)
            new_filename = f"{new_id}.json"
            new_filepath = os.path.join(category_path, new_filename)

            # Read the content of the JSON file
            with open(old_filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Update the 'id' field inside the JSON content
            data['id'] = new_id
            
            # Write the updated content to the new file
            with open(new_filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            
            # Remove the old file
            os.remove(old_filepath)
            
            print(f"Renamed {old_filename} to {new_filename} and updated 'id' to {new_id}")

            new_id += 1

print("Renaming and ID updating complete.")
