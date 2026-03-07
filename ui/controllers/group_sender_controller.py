from typing import Callable, Dict, List, Optional
from backend.campaign_manager import CampaignManager
from backend.cloud_service import cloud_service
from backend.excel_processor import ExcelProcessor


class GroupSenderController:
    """
    Stateless Controller for Group Sender UI (SaaS Multitenant).
    """

    def __init__(self):
        self.campaign_manager = CampaignManager(cloud_service)
        self.excel_processor = ExcelProcessor()

    def get_sheets(self, file_path: str) -> List[str]:
        return self.excel_processor.get_sheets(file_path)

    def get_columns(self, file_path: str, sheet_name: str) -> List[str]:
        return self.excel_processor.get_columns(file_path, sheet_name=sheet_name)

    def load_contacts(self, file_path: str, sheet_name: str) -> List[Dict]:
        return self.excel_processor.read_contacts(file_path, sheet_name=sheet_name)

    async def run_campaign(
        self,
        user_id: str,
        instance_name: str,
        contacts: List[Dict],
        message,
        media_file: Optional[str] = None,
        group_link: Optional[str] = None,
        delay_min: int = 5,
        delay_max: int = 15,
        progress_callback: Optional[Callable] = None,
    ):
        """
        Run a messaging campaign with user isolation context.
        """
        if not contacts:
            return {"error": "No contacts provided"}

        numbers = [c["phone"] for c in contacts if c.get("phone")]

        results = await self.campaign_manager.run_smart_campaign(
            user_id=user_id,
            instance_name=instance_name,
            numbers=numbers,
            message=message,
            media_file=media_file,
            group_link=group_link,
            delay_min=delay_min,
            delay_max=delay_max,
            progress_callback=progress_callback,
        )
        return results
