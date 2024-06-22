from fastapi import FastAPI, HTTPException
from fastapi_utils.tasks import repeat_every
from datetime import datetime
import os
import json

app = FastAPI()

data_directory = "../data"

@app.on_event("startup")
@repeat_every(seconds=60*60*24)  # Repeat every 24 hours
async def load_data():
    today_date = datetime.now().strftime("%Y-%m-%d")
    global data
    data = {
        "business": {
            "summary": get_all_file_paths(f"{data_directory}/{today_date}/business/summary"),
            "stats": get_all_file_paths(f"{data_directory}/{today_date}/business/stats")
        },
        "pakistan": {
            "summary": get_all_file_paths(f"{data_directory}/{today_date}/pakistan/summary"),
            "stats": get_all_file_paths(f"{data_directory}/{today_date}/pakistan/stats")
        }
    }
    print("Data loaded successfully")

def get_all_file_paths(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    return file_paths

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/load_data")
async def load_data_endpoint():
    await load_data()
    return {"status": "Data loaded successfully"}

@app.get("/summaries/{category}")
async def get_summaries(category: str):
    if category not in data:
        raise HTTPException(status_code=404, detail="Category not found")
    summaries = []
    for summary_path in data[category]["summary"]:
        with open(summary_path, 'r', encoding='utf-8') as file:
            summary = json.load(file)
            summaries.append(summary["summary"])
    return {"summaries": summaries, "len": len(summaries)}

@app.get("/meta_data/{category}")
async def get_summaries(category: str):
    if category not in data:
        raise HTTPException(status_code=404, detail="Category not found")
    meta_data_list = []
    for meta_data_path in data[category]["summary"]:
        with open(meta_data_path, 'r', encoding='utf-8') as file:
            meta_data = json.load(file)
            meta_data_list.append(meta_data["meta_data"])
    return {"meta_data": meta_data_list, "len": len(meta_data_list)}

@app.get("/stats/{category}")
async def get_stats(category: str):
    if category not in data:
        raise HTTPException(status_code=404, detail="Category not found")
    stats = []
    for stats_path in data[category]["stats"]:
        with open(stats_path, 'r', encoding='utf-8') as file:
            stat = json.load(file)
            stats.append(stat)
    return {"stats": stats}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)