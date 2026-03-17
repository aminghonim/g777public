
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from backend.excel_processor import ExcelProcessor

@pytest.fixture
def processor():
    return ExcelProcessor()

def test_get_sheets(processor):
    with patch('openpyxl.load_workbook') as mock_wb:
        mock_wb.return_value.sheetnames = ['Sheet1', 'Sheet2']
        sheets = processor.get_sheets("dummy.xlsx")
        assert sheets == ['Sheet1', 'Sheet2']
        mock_wb.assert_called_once()

def test_get_columns(processor):
    with patch('pandas.read_excel') as mock_read:
        # Mocking an empty DF with columns
        mock_read.return_value = pd.DataFrame(columns=['Name', 'Phone'])
        cols = processor.get_columns("dummy.xlsx")
        assert cols == ['Name', 'Phone']
        mock_read.assert_called_once()

def test_read_contacts_auto_detect(processor):
    """Test reading contacts with auto-detection of columns"""
    data = {
        'Customer Name': ['Ahmed', 'Mohamed'],
        'Mobile Number': ['01012345678', '01112345678'],
        'City': ['Cairo', 'Giza']
    }
    df = pd.DataFrame(data)
    
    with patch('pandas.read_excel', return_value=df):
        contacts = processor.read_contacts("dummy.xlsx")
        
        assert len(contacts) == 2
        assert contacts[0]['name'] == 'Ahmed'
        # Check phone cleaning (+20 for Egyptian numbers starting with 0)
        assert contacts[0]['phone'] == '+201012345678'
        assert contacts[1]['phone'] == '+201112345678'

def test_read_contacts_explicit_columns(processor):
    """Test reading contacts with specified column names"""
    data = {
        'A': ['User1'],
        'B': ['999999']
    }
    df = pd.DataFrame(data)
    
    with patch('pandas.read_excel', return_value=df):
        contacts = processor.read_contacts("dummy.xlsx", phone_column='B', name_column='A')
        
        assert len(contacts) == 1
        assert contacts[0]['name'] == 'User1'
        assert contacts[0]['phone'] == '+999999'

def test_read_contacts_messy_phones(processor):
    """Test cleaning messy phone numbers"""
    data = {
        'Phone': ['(010) 123-4567', '0020123456', 'invalid', None],
        'Name': ['A', 'B', 'C', 'D']
    }
    df = pd.DataFrame(data)
    
    with patch('pandas.read_excel', return_value=df):
        contacts = processor.read_contacts("dummy.xlsx")
        
        # Should filter out invalid/empty phones
        assert len(contacts) == 2
        assert contacts[0]['phone'] == '+20101234567'
        assert contacts[1]['phone'] == '+20123456'  # 002 -> +2

def test_read_contacts_empty_file(processor):
    with patch('pandas.read_excel', return_value=pd.DataFrame()):
        contacts = processor.read_contacts("dummy.xlsx")
        assert contacts == []

def test_preview_data(processor):
    df = pd.DataFrame({'A': [1, 2]})
    with patch('pandas.read_excel', return_value=df):
        preview = processor.preview_data("dummy.xlsx")
        assert not preview.empty
        assert len(preview) == 2

def test_count_rows(processor):
    df = pd.DataFrame({'A': range(10)})
    with patch('pandas.read_excel', return_value=df):
        count = processor.count_rows("dummy.xlsx")
        assert count == 10
