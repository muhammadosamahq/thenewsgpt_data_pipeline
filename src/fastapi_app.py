from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from glob import glob
from datetime import datetime
import json

app = FastAPI()

data_directory: str = ".././data"

def get_all_file_paths(directory: str) -> List[str]:
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    return file_paths

def read_json_file(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file {file_path}: {str(e)}")

class DateInput(BaseModel):
    date: str

@app.post("/load-data/")
async def load_data(date_input: DateInput):
    date = date_input.date
    global data

    try:
        data = {
            "business": {
                "summary": [read_json_file(file_path) for file_path in get_all_file_paths(f"{data_directory}/{date}/business/summary")],
                "stats": [read_json_file(file_path) for file_path in get_all_file_paths(f"{data_directory}/{date}/business/stats")]
            },
            "pakistan": {
                "summary": [read_json_file(file_path) for file_path in get_all_file_paths(f"{data_directory}/{date}/pakistan/summary")],
                "stats": [read_json_file(file_path) for file_path in get_all_file_paths(f"{data_directory}/{date}/pakistan/stats")]
            }
        }
 
        print(f"Loaded data: {data}")
        return {"msg": "We got data successfully", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/summaries/{category}")
async def get_summaries(category: str):
    print(f"Requested category: {category}")
    print(f"Available categories: {list(data.keys())}")
    if category in data:
        return {"summaries": data[category]["summary"]}
    else:
        raise HTTPException(status_code=404, detail="Category not found")
    
# @app.get("/summaries/{category}/all")
# async def get_summaries(category: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     summaries = {}
#     for file_path in data[category]["summary"]:
#         file_name = os.path.basename(file_path)
#         file_id = os.path.splitext(file_name)[0]
#         summary = read_json_file(file_path)
#         summaries[file_id] = summary.get("summary", "Summary not found")
#     return {"summaries": summaries, "len": len(summaries)}

@app.get("/summaries/{category}/{summary_id}")
async def get_summary_by_id(category: str, summary_id: str):
    if category in data:
        return {"summary": data[category]["summary"][0]}
    else:
        raise HTTPException(status_code=404, detail="Category not found")

# @app.get("/meta_data/{category}/all")
# async def get_meta_data(category: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     meta_data = {}
#     for meta_data_path in data[category]["summary"]:
#         file_name = os.path.basename(meta_data_path)
#         file_id = os.path.splitext(file_name)[0]
#         with open(meta_data_path, 'r', encoding='utf-8') as file:
#             meta = json.load(file)
#             meta_data[file_id] = meta["meta_data"]
#     return {"meta_data": meta_data, "len": len(meta_data)}

# @app.get("/meta_data/{category}/{meta_id}")
# async def get_meta_data_by_id(category: str, meta_id: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     meta_data_path = f".././data/{datetime.now().strftime('%Y-%m-%d')}/{category}/summary/{meta_id}.json"
#     if not os.path.exists(meta_data_path):
#         raise HTTPException(status_code=404, detail="Meta data not found")
#     with open(meta_data_path, 'r', encoding='utf-8') as file:
#         meta_data = json.load(file)
#     return {"meta_data": meta_data["meta_data"]}

# @app.get("/stats/{category}/all")
# async def get_stats(category: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     stats = []
#     for stats_path in data[category]["stats"]:
#         with open(stats_path, 'r', encoding='utf-8') as file:
#             stat = json.load(file)
#             stats.append(stat)
#     return {"stats": stats}

# @app.get("/stats/{category}/{stat_id}")
# async def get_stat_by_id(category: str, stat_id: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     stats_path = f".././data/{datetime.now().strftime('%Y-%m-%d')}/{category}/stats/{stat_id}.json"
#     if not os.path.exists(stats_path):
#         raise HTTPException(status_code=404, detail="Stat not found")
#     with open(stats_path, 'r', encoding='utf-8') as file:
#         stat = json.load(file)
#     return {"stat": stat}

# @app.get("/counts/{category}")
# async def get_counts(category: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     summary_count = len(data[category]["summary"])
#     stats_count = len(data[category]["stats"])
    
#     # Count the number of objects in each meta_data file
#     meta_data_counts = []
#     for meta_data_path in data[category]["summary"]:
#         file_name = os.path.basename(meta_data_path)
#         file_id = os.path.splitext(file_name)[0]
#         with open(meta_data_path, 'r', encoding='utf-8') as file:
#             meta = json.load(file)
#             meta_data_counts.append({"id": file_id, "len": len(meta["meta_data"])})
    
#     return {
#         "summaries_count": summary_count,
#         "meta_data_counts": meta_data_counts,
#         "stats_count": stats_count
#     }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)





# from fastapi import FastAPI, HTTPException
# from fastapi_utils.tasks import repeat_every
# from pydantic import BaseModel
# from typing import List, Dict
# import os
# from glob import glob
# from datetime import datetime
# import os
# import json

# app = FastAPI()

# # data_directory = "../data"

# # @app.on_event("startup")
# # @repeat_every(seconds=60*60*24)  # Repeat every 24 hours
# # async def load_data():
# #     today_date = datetime.now().strftime("%Y-%m-%d")
# #     global data
# #     data = {
# #         "business": {
# #             "summary": get_all_file_paths(f"{data_directory}/{today_date}/business/summary"),
# #             "stats": get_all_file_paths(f"{data_directory}/{today_date}/business/stats")
# #         },
# #         "pakistan": {
# #             "summary": get_all_file_paths(f"{data_directory}/{today_date}/pakistan/summary"),
# #             "stats": get_all_file_paths(f"{data_directory}/{today_date}/pakistan/stats")
# #         }
# #     }
# #     print("Data loaded successfully")

# # Function to get all file paths in a directory
# def get_all_file_paths(directory: str) -> List[str]:
#     return glob(f"{directory}/*")

# # Pydantic model for the input data
# class DirectoryPath(BaseModel):
#     dir_path: str

# @app.post("/load-data")
# async def load_data(directory: DirectoryPath):
#     data_directory = directory.dir_path

#     # Ensure the directory exists
#     if not os.path.exists(data_directory):
#         raise HTTPException(status_code=400, detail="Directory does not exist")

#     data = {
#         "business": {
#             "summary": get_all_file_paths(f"{data_directory}/business/summary"),
#             "stats": get_all_file_paths(f"{data_directory}/business/stats")
#         },
#         "pakistan": {
#             "summary": get_all_file_paths(f"{data_directory}/pakistan/summary"),
#             "stats": get_all_file_paths(f"{data_directory}/pakistan/stats")
#         }
#     }

#     return {"message": "Data loaded successfully", "data": data}

# def get_all_file_paths(directory):
#     file_paths = []
#     for root, _, files in os.walk(directory):
#         for file in files:
#             file_path = os.path.join(root, file)
#             file_paths.append(file_path)
#     return file_paths

# @app.get("/health")
# async def health_check():
#     return {"status": "ok"}

# @app.post("/load_data")
# async def load_data_endpoint():
#     await load_data()
#     return {"status": "Data loaded successfully"}

# @app.get("/summaries/{category}/all")
# async def get_summaries(category: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     summaries = {}
#     for summary_path in data[category]["summary"]:
#         file_name = os.path.basename(summary_path)
#         file_id = os.path.splitext(file_name)[0]
#         with open(summary_path, 'r', encoding='utf-8') as file:
#             summary = json.load(file)
#             summaries[file_id] = summary["summary"]
#     return {"summaries": summaries, "len": len(summaries)}

# @app.get("/summaries/{category}/{summary_id}")
# async def get_summary_by_id(category: str, summary_id: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     summary_path = f"{data_directory}/{datetime.now().strftime('%Y-%m-%d')}/{category}/summary/{summary_id}.json"
#     if not os.path.exists(summary_path):
#         raise HTTPException(status_code=404, detail="Summary not found")
#     with open(summary_path, 'r', encoding='utf-8') as file:
#         summary = json.load(file)
#     return {"summary": summary["summary"]}

# @app.get("/meta_data/{category}/all")
# async def get_meta_data(category: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     meta_data = {}
#     for meta_data_path in data[category]["summary"]:
#         file_name = os.path.basename(meta_data_path)
#         file_id = os.path.splitext(file_name)[0]
#         with open(meta_data_path, 'r', encoding='utf-8') as file:
#             meta = json.load(file)
#             meta_data[file_id] = meta["meta_data"]
#     return {"meta_data": meta_data, "len": len(meta_data)}

# @app.get("/meta_data/{category}/{meta_id}")
# async def get_meta_data_by_id(category: str, meta_id: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     meta_data_path = f"{data_directory}/{datetime.now().strftime('%Y-%m-%d')}/{category}/summary/{meta_id}.json"
#     if not os.path.exists(meta_data_path):
#         raise HTTPException(status_code=404, detail="Meta data not found")
#     with open(meta_data_path, 'r', encoding='utf-8') as file:
#         meta_data = json.load(file)
#     return {"meta_data": meta_data["meta_data"]}

# @app.get("/stats/{category}/all")
# async def get_stats(category: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     stats = []
#     for stats_path in data[category]["stats"]:
#         with open(stats_path, 'r', encoding='utf-8') as file:
#             stat = json.load(file)
#             stats.append(stat)
#     return {"stats": stats}

# @app.get("/stats/{category}/{stat_id}")
# async def get_stat_by_id(category: str, stat_id: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     stats_path = f"{data_directory}/{datetime.now().strftime('%Y-%m-%d')}/{category}/stats/{stat_id}.json"
#     if not os.path.exists(stats_path):
#         raise HTTPException(status_code=404, detail="Stat not found")
#     with open(stats_path, 'r', encoding='utf-8') as file:
#         stat = json.load(file)
#     return {"stat": stat}

# # @app.get("/counts/{category}")
# # async def get_counts(category: str):
# #     if category not in data:
# #         raise HTTPException(status_code=404, detail="Category not found")
# #     summary_count = len(data[category]["summary"])
# #     meta_data_count = len(data[category]["summary"])
# #     stats_count = len(data[category]["stats"])
# #     return {
# #         "summaries_count": summary_count,
# #         "meta_data_count": meta_data_count,
# #         "stats_count": stats_count
# #     }

# @app.get("/counts/{category}")
# async def get_counts(category: str):
#     if category not in data:
#         raise HTTPException(status_code=404, detail="Category not found")
#     summary_count = len(data[category]["summary"])
#     stats_count = len(data[category]["stats"])
    
#     # Count the number of objects in each meta_data file
#     meta_data_counts = []
#     for meta_data_path in data[category]["summary"]:
#         file_name = os.path.basename(meta_data_path)
#         file_id = os.path.splitext(file_name)[0]
#         with open(meta_data_path, 'r', encoding='utf-8') as file:
#             meta = json.load(file)
#             meta_data_counts.append({"id": file_id, "len": len(meta["meta_data"])})
    
#     return {
#         "summaries_count": summary_count,
#         "meta_data_counts": meta_data_counts,
#         "stats_count": stats_count
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)
