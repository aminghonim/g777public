import json
import asyncio
from pathlib import Path
import shutil
from typing import Optional, List, Dict, Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    UploadFile,
    Depends,
    HTTPException,
)
from fastapi.responses import JSONResponse, StreamingResponse

from backend.campaign_state import campaign_state
from ui.controllers.group_sender_controller import GroupSenderController
from core.dependencies import get_current_user

router = APIRouter(prefix="/api/group_sender", tags=["Group Sender"])
controller = GroupSenderController()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_excel(
    file: UploadFile = File(...), user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload Excel file (User-specific sandbox)"""
    user_id = str(user.get("user_id"))
    user_dir = UPLOAD_DIR / user_id
    user_dir.mkdir(exist_ok=True)

    file_path = user_dir / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    sheets = controller.get_sheets(str(file_path))
    columns = []
    if sheets:
        columns = controller.get_columns(str(file_path), sheet_name=sheets[0])

    return {
        "filename": file.filename,
        "sheets": sheets,
        "columns": columns,
        "full_path": str(file_path.absolute()),
    }


@router.post("/launch")
async def launch_campaign(
    messages: str = Form(...),
    sheet_name: str = Form(...),
    file_name: str = Form(...),  # Client should provide filename from previous upload
    delay_min: int = Form(5),
    delay_max: int = Form(15),
    group_link: Optional[str] = Form(None),
    direct_contacts: Optional[str] = Form(
        None
    ),  # JSON List of Dicts [{"phone": "...", "name": "..."}]
    media_file: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user: Dict[str, Any] = Depends(get_current_user),
):
    """Launch SaaS campaign in background with user context."""
    user_id = str(user.get("user_id"))
    instance_name = user.get("instance_name")

    contacts = []
    user_dir = UPLOAD_DIR / user_id

    if file_name and file_name != "None" and file_name != "":
        file_path = user_dir / file_name
        if file_path.exists():
            contacts = controller.load_contacts(str(file_path), sheet_name)
        else:
            raise HTTPException(
                status_code=404, detail="Excel file not found. Please upload again."
            )
    elif direct_contacts:
        try:
            contacts = json.loads(direct_contacts)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid direct_contacts format: {e}"
            )

    if not contacts:
        raise HTTPException(status_code=400, detail="No contacts found to send to.")

    try:
        message_list = json.loads(messages)
    except:
        message_list = [messages]
    # 2. Handle media
    media_path = None
    if media_file:
        media_path = str(user_dir / media_file.filename)
        with open(media_path, "wb") as buffer:
            shutil.copyfileobj(media_file.file, buffer)

    # 3. Start campaign
    campaign_state.start_campaign(user_id, len(contacts))

    background_tasks.add_task(
        controller.run_campaign,
        user_id=user_id,
        instance_name=instance_name,
        contacts=contacts,
        message=message_list,
        media_file=media_path,
        group_link=group_link,
        delay_min=delay_min,
        delay_max=delay_max,
        progress_callback=campaign_state.update_progress,
    )

    return {"status": "started", "total": len(contacts), "instance": instance_name}


@router.get("/preview")
async def preview_contacts(
    sheet_name: str, file_name: str, user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = str(user.get("user_id"))
    file_path = UPLOAD_DIR / user_id / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    contacts = controller.load_contacts(str(file_path), sheet_name)
    return {"contacts": contacts}
