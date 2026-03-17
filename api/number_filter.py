from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional, Dict
from pathlib import Path
import shutil

from ui.controllers.number_filter_controller import NumberFilterController

router = APIRouter(prefix="/api/number-filter", tags=["Number Filter"])
controller = NumberFilterController()

@router.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    """Upload excel and get sheets"""
    try:
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        controller.set_file_path(str(file_path))
        sheets = controller.get_sheet_names()
        
        return {"filename": file.filename, "sheets": sheets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sheets/{sheet_name}/process")
async def process_sheet(sheet_name: str, column: Optional[str] = None):
    """Process a sheet and extract numbers"""
    cols, cleaned = controller.process_excel_file(sheet_name=sheet_name, target_column=column)
    return {"columns": cols, "count": len(cleaned), "numbers": cleaned}

@router.post("/validate")
async def start_validation():
    """Start WhatsApp validation sequence"""
    # Again, a long-running process in a basic REST call.
    # Returns final results.
    results = await controller.run_validation()
    return results

@router.post("/stop")
async def stop_validation():
    """Stop the running validation"""
    controller.stop_validation()
    return {"status": "stopped"}

@router.post("/export")
async def export_valid():
    """Export valid numbers to Excel"""
    export_dir = Path("data/exports")
    export_dir.mkdir(parents=True, exist_ok=True)
    file_path = str(export_dir / "valid_numbers.xlsx")
    result_path = controller.export_valid(file_path)
    if not result_path:
        raise HTTPException(status_code=400, detail="No valid numbers to export")
    return {"path": result_path, "filename": "valid_numbers.xlsx"}
