from datetime import datetime, timedelta
import os
import json
import pandas as pd
import streamlit as st
import time

def get_all_file_paths(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    return file_paths

if __name__ == "__main__":
    c = 0
    meta_data_list = []
    st.set_page_config(page_title="News Summary", page_icon="💁")
    st.header("A bot for latest Pakistani news💁")
    today_date = datetime.now().strftime("%Y-%m-%d")
    summaries_path = get_all_file_paths(f".././data/{today_date}/business/summary")
    stats_path = get_all_file_paths(f".././data/{today_date}/business/stats")


    for cluster, stats in zip(summaries_path, stats_path):
        with open(cluster, 'r', encoding='utf-8') as file:
            summary = json.load(file)
        with open(stats, 'r', encoding='utf-8') as file:
            statistics = json.load(file)
        
        c = c + 1
        st.write(f"***Summary {c}:***", summary["summary"])
        for meta in summary["meta_data"]:
            filtered_meta_data = {key: value for key, value in meta.items() if key != "text"}
            meta_data_list.append(filtered_meta_data)
        
        st.write(meta_data_list)
        meta_data_list = []
        for s in statistics["all_json_object_list"]:
            st.write(s["object"])
            headings = s["headings"]
            rows = s["data"]
            df = pd.DataFrame(rows, columns=headings)
            st.table(df)
        # for obj in summary["stats"]:
        #     if obj:
        #         st.write(obj["heading"])
        #         try:
        #             if len(obj["data"].keys()) == 1:
        #                 data = [key for key in obj["data"].keys()]
        #                 df = pd.DataFrame.from_dict(obj["data"][data[0]])
        #                 st.table(df)
        #             elif "headings" and "rows" in obj["data"].keys():
        #                 headings = obj["data"]["headings"]
        #                 rows = obj["data"]["rows"]
        #                 df = pd.DataFrame(rows, columns=headings)
        #                 st.table(df)
        #             elif "headings" and "data" in obj["data"].keys():
        #                 headings = obj["data"]["headings"]
        #                 rows = obj["data"]["data"]
        #                 df = pd.DataFrame(rows, columns=headings)
        #                 st.table(df)
        #             elif "Headings" and "Data" in obj["data"].keys():
        #                 headings = obj["data"]["Headings"]
        #                 rows = obj["data"]["Data"]
        #                 df = pd.DataFrame(rows, columns=headings)
        #                 st.table(df)
        #             else:
        #                 df = pd.DataFrame.from_dict(obj["data"])
        #                 st.table(df)

        #         except ValueError:
        #             if len(obj["data"].keys()) == 1:
        #                 data = [key for key in obj["data"].keys()]
        #                 my_data = dict([ (k, pd.Series(v)) for k,v in obj["data"][data[0]].items() ])
        #                 df = pd.DataFrame.from_dict(my_data)
        #                 st.table(df)
        #             else:
        #                 my_data = dict([ (k, pd.Series(v)) for k,v in obj["data"].items() ])
        #                 df = pd.DataFrame.from_dict(my_data)
        #                 st.table(df)
                    

        # time.delay(5)


                   