import uuid
import logging
import json
import os
import asyncio
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from services.maps_scraper.scraper import MapsScraper
from services.maps_scraper.parser import MapsDataParser

# PERSISTENCE_FILE
RESULTS_FILE = "/app/data/scraper_results.json"

# Custom JSON encoder for datetime
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Initialize FastAPI app
app = FastAPI(
    title="Maps Scraper Microservice",
    description="Anti-Detection Google Maps Scraper (CNS Squad Edition)",
    version="1.0.0"
)

# In-memory status store
tasks_db: Dict[str, Dict[str, Any]] = {}

# Ensure data dir exists
os.makedirs("/app/data", exist_ok=True)

# Load existing results if any
if os.path.exists(RESULTS_FILE):
    try:
        with open(RESULTS_FILE, 'r') as f:
            tasks_db = json.load(f)
    except:
        tasks_db = {}

def save_db():
    try:
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks_db, f, cls=DateTimeEncoder, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Failed to save DB: {e}")

# Initialize Services
scraper = MapsScraper()
parser = MapsDataParser()

class ScrapeRequest(BaseModel):
    query: str
    zoom_level: Optional[str] = "fastest"

class TaskResponse(BaseModel):
    task_id: str
    status: str

async def run_scrape_task(task_id: str, query: str, zoom_level: str):
    tasks_db[task_id]["status"] = "processing"
    save_db()
    try:
        results = await scraper.scrape(query, zoom_level=zoom_level)
        # Handle Pydantic v1/v2 compatibility
        serialized_results = []
        for p in results:
            if hasattr(p, "model_dump"):
                serialized_results.append(p.model_dump())
            else:
                serialized_results.append(p.dict())
        
        tasks_db[task_id]["results"] = serialized_results
        tasks_db[task_id]["status"] = "completed"
    except Exception:
        tasks_db[task_id]["status"] = "failed"
        err_msg = traceback.format_exc()
        tasks_db[task_id]["error"] = err_msg
        logging.error(f"Task {task_id} failed with traceback:\n{err_msg}")
    finally:
        save_db()

@app.post("/api/v1/scraper/tasks", response_model=TaskResponse)
async def create_scrape_task(request: ScrapeRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = {
        "status": "pending",
        "query": request.query,
        "results": [],
        "created_at": datetime.utcnow().isoformat()
    }
    save_db()
    background_tasks.add_task(run_scrape_task, task_id, request.query, request.zoom_level)
    return {"task_id": task_id, "status": "pending"}

@app.get("/api/v1/scraper/tasks/{task_id}/results")
async def get_task_results(task_id: str):
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id,
        "status": task["status"],
        "query": task.get("query"),
        "count": len(task.get("results", [])),
        "data": task.get("results", []),
        "error": task.get("error")
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
