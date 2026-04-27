"""
Persistence Layer for Grabber - حفظ المخرجات في Excel
"""

import os
import re
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple
from ..core.i18n import t


class GrabberPersistence:
    """
    Handles saving extracted members to Excel workbooks.
    """

    def __init__(self, project_root: str):
        self.project_root = project_root

    def save_members(
        self, members: Dict[str, dict], method: str, group_name: str = "Unknown"
    ) -> Tuple[str, str]:
        """
        حفظ الأعضاء في ملف Excel موحد.
        """
        try:
            cleaned_data = [
                {
                    "name": member["name"],
                    "phone": member["phone"],
                    "extraction_method": method,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                for member in members.values()
            ]

            output_dir = os.path.join(self.project_root, "data")
            os.makedirs(output_dir, exist_ok=True)

            safe_sheet_name = re.sub(r"[\\/:\?\*\[\]]", "", group_name)
            safe_sheet_name = safe_sheet_name[:30]

            if not safe_sheet_name or safe_sheet_name.strip() == "":
                safe_sheet_name = f"Group_{datetime.now().strftime('%M%S')}"

            main_file = "whatsapp_marketing_leads.xlsx"
            filepath = os.path.join(output_dir, main_file)

            df = pd.DataFrame(cleaned_data)

            if os.path.exists(filepath):
                try:
                    with pd.ExcelWriter(
                        filepath, mode="a", engine="openpyxl", if_sheet_exists="replace"
                    ) as writer:
                        df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                    message = t(
                        "grabber.logs.updated_workbook",
                        " Updated existing workbook. Added sheet: '{sheet}' ({count} members)",
                    ).format(sheet=safe_sheet_name, count=len(cleaned_data))
                except Exception as file_error:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filepath = os.path.join(
                        output_dir, f"leads_backup_{timestamp}.xlsx"
                    )
                    df.to_excel(filepath, sheet_name=safe_sheet_name, index=False)
                    message = t(
                        "grabber.logs.file_locked",
                        " Main file locked/error. Saved to new file: {path}",
                    ).format(path=filepath)
            else:
                df.to_excel(filepath, sheet_name=safe_sheet_name, index=False)
                message = t(
                    "grabber.logs.created_workbook",
                    " Created new workbook. Sheet: '{sheet}' ({count} members)",
                ).format(sheet=safe_sheet_name, count=len(cleaned_data))

            return filepath, message

        except Exception as e:
            raise e
