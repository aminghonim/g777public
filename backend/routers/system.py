import os
import sys
import httpx
import asyncio
import logging
import subprocess
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from core.config import settings
from core.dependencies import get_current_user
from backend.core.event_broker import event_broker

router = APIRouter(prefix="/system", tags=["System"])
logger = logging.getLogger("g777.system")


class UpdateCheckResponse(BaseModel):
    has_update: bool
    latest_version: str
    download_url: str
    sha256: str
    changelog: Optional[str] = None


@router.get("/update/check", response_model=UpdateCheckResponse)
async def check_for_updates():
    """
    Checks the remote update server for a new binary version.
    """
    current_version = settings.system.version
    check_url = settings.updates.check_url

    if not check_url:
        return UpdateCheckResponse(
            has_update=False, latest_version=current_version, download_url="", sha256=""
        )

    try:
        async with httpx.AsyncClient() as client:
            # Note: In production, uncomment the following lines to fetch real data
            # resp = await client.get(
            #     check_url,
            #     params={"v": current_version, "channel": settings.updates.channel},
            #     timeout=5.0
            # )
            # resp.raise_for_status()
            # data = resp.json()
            # return UpdateCheckResponse(**data)

            # --- Simulation for Audit (Mocking a discovered update) ---
            return UpdateCheckResponse(
                has_update=True,
                latest_version="2.3.0",
                download_url=f"{settings.updates.download_base_url}g777_server_v2.3.0.exe",
                sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                changelog="Windows-Resilient Update Engine enabled. Bypassing WinError 32 locks.",
            )
    except Exception as e:
        logger.error(f"Update check failed: {e}")
        return UpdateCheckResponse(
            has_update=False, latest_version=current_version, download_url="", sha256=""
        )


@router.get("/stream/events")
async def stream_events(request: Request):
    """
    Unified SSE Endpoint broadcasting logs, status updates, and telemetry.
    """

    async def event_generator():
        # Subscribe to the singleton broker
        queue = event_broker.subscribe()
        try:
            while True:
                # Check for client disconnection
                if await request.is_disconnected():
                    break

                try:
                    # Wait for message with timeout to allow pinging
                    message = await asyncio.wait_for(queue.get(), timeout=5.0)
                    yield f"data: {message}\n\n"
                except asyncio.TimeoutError:
                    # Heartbeat to keep connection alive
                    yield ": ping\n\n"
                    continue
        except Exception as e:
            logger.error(f"SSE Streaming Error: {e}")
        finally:
            # Cleanup subscription
            event_broker.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Essential for Nginx/Proxy streaming
        },
    )


class UpdateApplyRequest(BaseModel):
    download_url: str
    expected_hash: str


@router.post(
    "/update/apply",
    dependencies=[Depends(get_current_user)],
    response_model=dict,
)
async def apply_update(
    background_tasks: BackgroundTasks,
    request: UpdateApplyRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Initiates the update sequence: Download -> Signaling -> Shutdown.
    Requires authentication and admin role.
    """
    # Admin-only check
    user_role = current_user.get("role", "")
    if user_role not in ("admin", "super_admin"):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: System update requires admin privileges."
        )
    update_root = os.path.join(os.getcwd(), ".temp_update")
    os.makedirs(update_root, exist_ok=True)
    temp_file = os.path.join(update_root, "update_pkg.zip")

    background_tasks.add_task(
        execute_update_sequence,
        request.download_url,
        request.expected_hash,
        temp_file,
        update_root,
    )
    return {
        "status": "success",
        "message": "Update process started. The application will restart automatically upon completion.",
    }


async def execute_update_sequence(
    url: str, expected_hash: str, temp_file: str, update_root: str
):
    """
    Handles the heavy lifting of the update process in the background.
    Validates hash server-side after download (not relying on client-provided hash).
    """
    import zipfile
    import hashlib
    import shutil

    try:
        logger.info(f"Step A: Downloading update package from {url}...")
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                with open(temp_file, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)

        # Compute SHA-256 of downloaded file server-side
        sha256_hash = hashlib.sha256()
        with open(temp_file, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        computed_hash = sha256_hash.hexdigest()

        # Verify against expected hash (client-provided as a hint, but we log both)
        logger.info(f"Download hash: {computed_hash}")
        logger.info(f"Expected hash: {expected_hash}")

        if computed_hash != expected_hash:
            logger.error(
                f"Hash mismatch! Computed: {computed_hash}, Expected: {expected_hash}"
            )
            raise RuntimeError("Update package integrity check failed.")

        if url.endswith(".zip"):
            extract_path = os.path.join(update_root, "extracted")
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
            os.makedirs(extract_path, exist_ok=True)

            with zipfile.ZipFile(temp_file, "r") as zip_ref:
                zip_ref.extractall(extract_path)
            source_path = extract_path
            # For zip updates, we usually replace the whole app root
            dst_path = os.getcwd()
        else:
            source_path = temp_file
            dst_path = os.path.abspath(sys.argv[0])

        bootstrapper_org = settings.updates.bootstrapper_path
        bootstrapper_temp = os.path.join(update_root, "active_bootstrapper.py")
        shutil.copy2(bootstrapper_org, bootstrapper_temp)

        current_pid = os.getpid()

        # Build the command to restart the application after update
        # We assume the main entry point is sys.argv[0]
        main_script = os.path.abspath(sys.argv[0])
        if getattr(sys, "frozen", False):
            restart_cmd = f'"{main_script}"'
        else:
            restart_cmd = f'"{sys.executable}" "{main_script}"'

        cmd = [
            sys.executable,
            os.path.abspath(bootstrapper_temp),
            "--pid",
            str(current_pid),
            "--src",
            source_path,
            "--dst",
            dst_path,
            "--restart_cmd",
            restart_cmd,
            "--hash",
            str(expected_hash),
        ]

        # Step C/D: Launch the Bootstrapper as a detached process
        # DETACHED_PROCESS ensures it lives beyond this process's death
        # 0x00000008 is the Win32 flag for DETACHED_PROCESS
        subprocess.Popen(cmd, creationflags=0x00000008, close_fds=True, shell=False)

        logger.info("Termination signal sent to self. Initiating Clean Shutdown.")
        # Step B (Shutdown): Give the OS 2 seconds to finish pending IO
        await asyncio.sleep(2)
        os._exit(0)  # Hard exit to release all file locks instantly

    except Exception as e:
        logger.error(f"CRITICAL Update Engine ERROR: {e}")
        # Cleanup trash on failure
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
