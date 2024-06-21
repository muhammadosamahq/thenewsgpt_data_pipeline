import json
import streamlit as st
import pandas as pd


def are_all_lists_equal(data_dict):
    # Extract the first list to use as a reference
    reference_list = next(iter(data_dict.values()))
    
    # Iterate through the dictionary and compare each list to the reference list
    for key, lst in data_dict.items():
        if lst != reference_list:
            return False
            
    return True


if __name__ == "__main__":
    with open("sample.json", 'r') as json_file:
        data_list = json.load(json_file)
    
    
    for obj in data_list:
        st.write(obj["heading"])
        df = pd.DataFrame.from_dict(obj["data"])
        df = df.drop_duplicates()
        st.table(df)
