import logging
import asyncio
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class NumberFilterController:
    """
    Controller for parsing Excel files, extracting numbers, 
    and executing WhatsApp validation.
    """

    def __init__(self) -> None:
        self.file_path: Optional[str] = None
        self._running: bool = False
        self._extracted_numbers: List[str] = []
        self._valid_numbers: List[str] = []

    def set_file_path(self, file_path: str) -> None:
        """Stores the uploaded Excel file path."""
        target_path = Path(file_path)
        if not target_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.file_path = str(target_path)
        logger.info("File path mapped successfully: %s", self.file_path)

    def get_sheet_names(self) -> List[str]:
        """Reads the Excel file and returns all sheet names."""
        if not self.file_path:
            raise ValueError("File path cannot be empty before getting sheets.")

        try:
            excel_file = pd.ExcelFile(self.file_path)
            sheets = [str(name) for name in excel_file.sheet_names]
            logger.info("Detected %d sheet(s) in %s", len(sheets), self.file_path)
            return sheets
        except Exception as err:
            logger.error("Pandas failed to parse sheets: %s", err)
            raise

    def process_excel_file(self, sheet_name: str, target_column: Optional[str] = None) -> Tuple[List[str], List[str]]:
        """Extracts and heavily cleans phone numbers from a specific sheet/column."""
        if not self.file_path:
            raise ValueError("File path cannot be empty before processing.")

        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            
            # Stringified column safety
            columns: List[str] = [str(col) for col in df.columns.tolist()]
            raw_numbers = pd.Series(dtype=str)

            # Assign extraction target
            if target_column and target_column in df.columns:
                raw_numbers = df[target_column].astype(str)
            elif not df.empty:
                # Default to the first column if no specific column is given
                first_col = df.columns[0]
                raw_numbers = df[first_col].astype(str)

            # Cleansing process: RegEx only allows digits. Strip spaces, '+', '-', etc.
            cleaned_series = raw_numbers.str.replace(r'\D', '', regex=True)
            
            # Filter blanks and drop duplicates
            valid_series = cleaned_series[cleaned_series != ""]
            cleaned_numbers = valid_series.drop_duplicates().tolist()

            self._extracted_numbers = cleaned_numbers
            logger.info(
                "Processed %s. Column '%s'. Found %d unique cleaned numbers.", 
                sheet_name, target_column or "Default(First)", len(cleaned_numbers)
            )
            
            return columns, cleaned_numbers

        except (ValueError, KeyError, TypeError) as err:
            logger.error("Failed executing data extraction pipeline: %s", err)
            raise

    async def run_validation(self) -> Dict[str, int]:
        """Initiates async validation loop over extracted numbers."""
        self._running = True
        self._valid_numbers = []
        
        total = len(self._extracted_numbers)
        valid = 0
        invalid = 0

        logger.info("Starting WhatsApp number validation for %d entries.", total)

        for number in self._extracted_numbers:
            # Graceful Kill Switch
            if not self._running:
                logger.info("Validation loop aborted manually.")
                break

            # Network Mock Delay
            await asyncio.sleep(0.01)

            # TODO: ربط بـ Evolution API للتحقق الفعلي
            # Placeholder: Validate numbers with len >= 10
            if len(number) >= 10:
                self._valid_numbers.append(number)
                valid += 1
            else:
                invalid += 1

        self._running = False
        logger.info("Validation concluded. Total: %d, Valid: %d, Invalid: %d", total, valid, invalid)
        
        return {
            "total": total,
            "valid": valid,
            "invalid": invalid
        }

    def stop_validation(self) -> None:
        """Trigger global halt for the validation process."""
        logger.info("Kill switch activated: Stopping current validation loop.")
        self._running = False

    def export_valid(self, file_path: str) -> Optional[str]:
        """Saves valid entries to an Excel destination."""
        if not self._valid_numbers:
            logger.warning("Export requested but no valid numbers array found. Aborting.")
            return None

        try:
            export_path = Path(file_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

            df = pd.DataFrame({"Valid_WhatsApp_Numbers": self._valid_numbers})
            # index=False avoids the first unnamed index column in Excel
            df.to_excel(str(export_path), index=False)

            logger.info("Successfully exported %d verified entries to %s", len(self._valid_numbers), file_path)
            return str(export_path)

        except OSError as err:
            logger.error("File system I/O error during export: %s", err)
            raise
