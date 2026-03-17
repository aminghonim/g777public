
import pytest
import pandas as pd
import os
from unittest.mock import MagicMock, patch
from backend.excel_processor import ExcelProcessor

class TestExcelProcessorSurgical:
    
    @pytest.fixture
    def processor(self):
        return ExcelProcessor()

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================
    
    def test_get_sheets_success(self, processor):
        """اختبار قراءة الأوراق بنجاح"""
        with patch('pandas.ExcelFile') as mock_excel:
            mock_excel.return_value.sheet_names = ['Sheet1', 'Sheet2']
            sheets = processor.get_sheets("fake_path.xlsx")
            assert sheets == ['Sheet1', 'Sheet2']

    def test_get_columns_success(self, processor):
        """اختبار قراءة الأعمدة بنجاح"""
        with patch('pandas.read_excel') as mock_read:
            mock_read.return_value.columns = ['Name', 'Phone']
            cols = processor.get_columns("fake.xlsx")
            assert cols == ['Name', 'Phone']

    def test_read_contacts_success_auto_find(self, processor):
        """اختبار قراءة جهات الاتصال مع البحث التلقائي عن الأعمدة"""
        # Create a mock dataframe that mimics Excel output
        # pd.read_excel typically returns a DataFrame
        mock_df = pd.DataFrame({
            'الاسم': ['Ali', 'NoPhone'],
            'phone': ['01012345678', 'invalid']
        })
        with patch('pandas.read_excel', return_value=mock_df):
            contacts = processor.read_contacts("fake.xlsx")
            # 01012345678 should become +201012345678 via _clean_phone
            assert len(contacts) >= 1
            # Check if Ali was found
            ali = next((c for c in contacts if c['name'] == 'Ali'), None)
            assert ali is not None
            assert ali['phone'] == '+201012345678'

    def test_clean_phone_variants(self, processor):
        """اختبار كافة حالات تنظيف الأرقام (تغطية 100% للمنطق)"""
        assert processor._clean_phone("01112223334") == "+201112223334" # Egyptian 11 digits
        assert processor._clean_phone("0101234567") == "+20101234567"  # Egyptian 10 digits
        assert processor._clean_phone("1012345678") == "+201012345678" # Missing 0
        assert processor._clean_phone("201222333444") == "+201222333444" # Already has 20
        assert processor._clean_phone("00201222333444") == "+201222333444" # Starts with 00
        assert processor._clean_phone("123") == ""                   # Too short
        assert processor._clean_phone("nan") == ""                   # NaN handle
        assert processor._clean_phone(None) == ""                    # None handle

    # =================================================================
    # ❌ LOGIC FAILURE STATE TESTS
    # =================================================================
    
    def test_read_contacts_empty_df(self, processor):
        """اختبار استلام ملف فارغ"""
        with patch('pandas.read_excel', return_value=pd.DataFrame()):
            contacts = processor.read_contacts("empty.xlsx")
            assert contacts == []

    def test_count_rows_failure(self, processor):
        """اختبار فشل عد الصفوف"""
        with patch('pandas.read_excel', side_effect=Exception("Read Error")):
            assert processor.count_rows("bad.xlsx") == 0
            
    def test_count_rows_success(self, processor):
        mock_df = pd.DataFrame({'a': [1,2,3]})
        with patch('pandas.read_excel', return_value=mock_df):
            assert processor.count_rows("file.xlsx") == 3

    # =================================================================
    # 💥 SYSTEM FAILURE STATE TESTS (Covering 'except' blocks)
    # =================================================================
    
    def test_get_sheets_critical_failure(self, processor):
        """تغطية بلوكات except في حالة الفشل الكلي لقراءة الأوراق"""
        with patch('pandas.ExcelFile', side_effect=Exception("Pandas Crash")):
            # محاكاة فشل Fallback أيضاً عبر استثناء استيراد أو استدعاء openpyxl
            with patch('openpyxl.load_workbook', side_effect=Exception("Openpyxl Crash")):
                sheets = processor.get_sheets("corrupt.xlsx")
                assert sheets == []

    def test_preview_data_exception(self, processor):
        """تغطية بلوك except في المعاينة"""
        with patch('pandas.read_excel', side_effect=Exception("IO Error")):
            df = processor.preview_data("none.xlsx")
            assert df.empty

    def test_get_columns_exception(self, processor):
        """تغطية بلوك except في الأعمدة"""
        with patch('pandas.read_excel', side_effect=Exception("Permission Denied")):
            cols = processor.get_columns("locked.xlsx")
            assert cols == []
