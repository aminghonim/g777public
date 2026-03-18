
import pytest
import os
from unittest.mock import MagicMock, patch

try:
    from backend.search_service import AzureSearchService
    HAS_AZURE = True
except (ImportError, ModuleNotFoundError):
    HAS_AZURE = False

@pytest.mark.skipif(not HAS_AZURE, reason="Azure Search libraries not installed")
class TestSearchServiceSurgical:

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================

    def test_init_success(self):
        """اختبار تهيئة المحرك بنجاح عند وجود الإعدادات"""
        with patch.dict(os.environ, {
            "AZURE_AI_SEARCH_ENDPOINT": "http://test-search.com",
            "AZURE_AI_SEARCH_KEY": "secret"
        }):
            with patch('azure.search.documents.SearchClient', MagicMock()):
                service = AzureSearchService()
                assert service.client is not None

    @pytest.mark.asyncio
    async def test_find_relevant_data_success(self):
        """اختبار جلب البيانات وتنسيقها بنجاح"""
        with patch.dict(os.environ, {"AZURE_AI_SEARCH_ENDPOINT": "https://test.search.windows.net", "AZURE_AI_SEARCH_KEY": "y"}):
            # Create a complete mock for the SearchClient
            mock_client_instance = MagicMock()
            mock_results = [
                {'content': 'Trip to Dahab', 'source': 'excel'},
                {'content': 'Cheap prices', 'source': 'db'}
            ]
            mock_client_instance.search.return_value = iter(mock_results)
            
            with patch('backend.search_service.SearchClient', return_value=mock_client_instance):
                service = AzureSearchService()
                
                res = await service.find_relevant_data("Dahab")
                assert "المعلومات المستخرجة" in res
                assert "Trip to Dahab" in res

    # =================================================================
    # ❌ LOGIC FAILURE STATE TESTS
    # =================================================================

    def test_init_missing_creds(self):
        """حالة غياب الإعدادات (تعطيل الخدمة تلقائياً)"""
        with patch.dict(os.environ, {}, clear=True):
            service = AzureSearchService()
            assert service.client is None

    @pytest.mark.asyncio
    async def test_find_relevant_data_no_results(self):
        """حالة عدم وجود نتائج مطابقة للبحث"""
        with patch.dict(os.environ, {"AZURE_AI_SEARCH_ENDPOINT": "x", "AZURE_AI_SEARCH_KEY": "y"}):
            mock_client = MagicMock()
            mock_client.search.return_value = []
            
            with patch('azure.search.documents.SearchClient', return_value=mock_client):
                service = AzureSearchService()
                
                res = await service.find_relevant_data("Empty")
                assert res == ""

    # =================================================================
    # 💥 SYSTEM FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_find_relevant_data_exception(self):
        """تغطية الـ except في حالة فشل الاتصال بـ Azure Search"""
        with patch.dict(os.environ, {"AZURE_AI_SEARCH_ENDPOINT": "x", "AZURE_AI_SEARCH_KEY": "y"}):
            mock_client = MagicMock()
            mock_client.search.side_effect = Exception("Azure Offline")
            
            with patch('azure.search.documents.SearchClient', return_value=mock_client):
                service = AzureSearchService()
                
                res = await service.find_relevant_data("query")
                assert res == ""

    @pytest.mark.asyncio
    async def test_find_relevant_data_no_client(self):
        """اختبار البحث بدون client متاح"""
        with patch.dict(os.environ, {}, clear=True):
            service = AzureSearchService()
            assert service.client is None
            
            res = await service.find_relevant_data("query")
            assert res == ""

