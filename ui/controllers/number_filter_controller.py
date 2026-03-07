
import asyncio
import pandas as pd
import re
from typing import List, Dict, Optional, Tuple, Callable
from backend.cloud_service import cloud_service
from backend.excel_processor import ExcelProcessor

class NumberFilterController:
    """
    Controller for Number Filter UI.
    Handles excel processing, number cleaning, and API validation orchestration.
    """
    def __init__(self):
        self.state = {
            'numbers': [],   # Cleaned numbers for filtering
            'results': [],   # Validation results [{'phone': '...', 'exists': True/False}]
            'cols': [],      # Columns in the uploaded file
            'sheets': [],    # Sheet names in the Excel file
            'file_path': None,
            'is_running': False
        }
        self.excel_processor = ExcelProcessor()

    def set_file_path(self, path: str):
        self.state['file_path'] = path

    def get_sheet_names(self) -> List[str]:
        """Returns list of sheet names in the current Excel file."""
        if not self.state['file_path']:
            return []
        try:
            xl = pd.ExcelFile(self.state['file_path'], engine='openpyxl')
            self.state['sheets'] = xl.sheet_names
            return xl.sheet_names
        except Exception as e:
            print(f"[RE-ERROR] Get Sheets: {e}")
            return []

    def process_excel_file(self, sheet_name: Optional[str] = None, target_column: Optional[str] = None) -> Tuple[List[str], List[str]]:
        """
        Processes the excel file, detects columns, and extracts/cleans numbers.
        Returns (columns_list, cleaned_numbers_list).
        """
        if not self.state['file_path']:
            return [], []
            
        try:
            # Read as DataFrame directly to get columns
            df = pd.read_excel(
                self.state['file_path'], 
                sheet_name=sheet_name if sheet_name else 0,
                dtype=str,
                engine='openpyxl'
            )
            
            self.state['cols'] = list(df.columns)
            
            # Smart Column Detection
            col = target_column
            if not col:
                possible_cols = ['phone', 'mobile', 'number', 'رقم', 'هاتف', 'موبايل', 'Cell', 'Phone Number', 'contact', 'tele']
                for c in df.columns:
                    if str(c).lower() in [p.lower() for p in possible_cols]:
                        col = c
                        break
                if not col: col = df.columns[0]
            
            # Extraction and Cleaning
            raw_numbers = df[col].astype(str).tolist()
            cleaned = []
            seen = set()
            for n in raw_numbers:
                if not n or n.lower() == 'nan': continue
                
                # Digit-only extraction
                num = re.sub(r'\D', '', n)
                if num and num not in seen:
                    cleaned.append(num)
                    seen.add(num)
            
            self.state['numbers'] = cleaned
            return self.state['cols'], cleaned
        except Exception as e:
            print(f"[RE-ERROR] Process Excel: {e}")
            return [], []

    async def run_validation(self, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Orchestrates the WhatsApp existence check for all loaded numbers."""
        if self.state['is_running'] or not self.state['numbers']:
            return []

        self.state['is_running'] = True
        self.state['results'] = []
        total = len(self.state['numbers'])
        
        try:
            for idx, num in enumerate(self.state['numbers']):
                if not self.state['is_running']: break
                
                # Call Cloud Service - Evolution API returns list:
                # [{"jid": "...", "exists": true/false, "number": "..."}]
                res_data = await asyncio.to_thread(cloud_service.check_numbers_exist, [num])
                
                exists = False
                # Handle list response (Evolution API format)
                if isinstance(res_data, list) and len(res_data) > 0:
                    first_item = res_data[0]
                    if isinstance(first_item, dict):
                        exists = first_item.get('exists', False)
                # Handle dict response (legacy/other API format)
                elif isinstance(res_data, dict):
                    if 'exists' in res_data:
                        exists = res_data['exists']
                    elif 'data' in res_data and isinstance(res_data['data'], list):
                        if len(res_data['data']) > 0:
                            exists = res_data['data'][0].get('exists', False)
                
                res = {'phone': num, 'exists': '✅ Yes' if exists else '❌ No'}
                self.state['results'].append(res)
                
                if progress_callback:
                    progress_callback(idx + 1, total, res)
                
                # Small delay to prevent API flooding
                await asyncio.sleep(0.05)
                
            return self.state['results']
        finally:
            self.state['is_running'] = False

    def stop_validation(self):
        self.state['is_running'] = False

    def export_valid(self, path: str = "data/valid_numbers.xlsx") -> Optional[str]:
        """Exports only the valid numbers to Excel."""
        valid = [r for r in self.state['results'] if 'Yes' in r['exists']]
        if not valid: return None
        
        try:
            pd.DataFrame(valid).to_excel(path, index=False)
            return path
        except:
            return None
