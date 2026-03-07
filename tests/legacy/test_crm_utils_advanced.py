"""
Coverage Boost Tests - CRM & Utils Advanced Edge Cases
Target: 95%+ coverage
"""

import pytest
import asyncio
import io
import csv
import threading
from unittest.mock import MagicMock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tests.frontend.test_crm_logic import CRMDataLogic


@pytest.fixture
def crm_logic():
    return CRMDataLogic()


class TestNonUTF8Encoding:
    """Test handling of various character encodings"""
    
    def test_export_with_arabic_characters(self, crm_logic):
        customers = [{'name': 'أحمد محمد', 'phone': '+201234567890', 
                     'city': 'القاهرة', 'metadata': {'interests': ['عقارات']}}]
        csv_content = crm_logic.export_csv(customers)
        assert 'أحمد' in csv_content
    
    def test_export_with_special_csv_characters(self, crm_logic):
        customers = [{'name': 'Ahmed, Test', 'phone': '+201234567890',
                     'city': 'Cairo "Capital"', 'metadata': {'interests': []}}]
        csv_content = crm_logic.export_csv(customers)
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        assert len(rows) == 2


class TestConcurrentOperations:
    """Test thread safety"""
    
    def test_concurrent_filters(self, crm_logic):
        customers = [{'name': 'Test', 'customer_type': 'lead', 'metadata': {}}]
        results = []
        
        def do_filter():
            for _ in range(50):
                results.append(len(crm_logic.filter_customers(customers, filter_type='lead')))
        
        threads = [threading.Thread(target=do_filter) for _ in range(4)]
        for t in threads: t.start()
        for t in threads: t.join()
        
        assert len(results) == 200


class TestComplexNullHandling:
    """Test null/empty handling"""
    
    def test_filter_with_none_city(self, crm_logic):
        customers = [
            {'name': 'Test1', 'city': None, 'metadata': {}},
            {'name': 'Test2', 'city': 'Cairo', 'metadata': {}},
        ]
        result = crm_logic.filter_customers(customers, city='Cairo')
        assert len(result) == 1
    
    def test_stats_with_missing_type(self, crm_logic):
        customers = [{'name': 'Test'}]
        stats = crm_logic.calculate_stats(customers)
        assert stats['total'] == 1
        assert stats['leads'] == 0


class TestUtilsFunctions:
    """Test ui/utils.py"""
    
    @pytest.mark.asyncio
    async def test_get_safe_upload_data_content(self):
        from ui.utils import get_safe_upload_data
        mock_event = MagicMock()
        mock_event.name = "test.csv"
        mock_event.content = MagicMock()
        mock_event.content.read = MagicMock(return_value=b"test content")
        content, filename = await get_safe_upload_data(mock_event)
        assert content == b"test content"
    
    @pytest.mark.asyncio
    async def test_get_safe_upload_data_error(self):
        from ui.utils import get_safe_upload_data
        mock_event = MagicMock()
        mock_event.name = "test.csv"
        mock_event.content = MagicMock()
        mock_event.content.read = MagicMock(side_effect=Exception("Error"))
        content, filename = await get_safe_upload_data(mock_event)
        assert content is None
