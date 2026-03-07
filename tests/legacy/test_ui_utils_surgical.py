import pytest
from unittest.mock import MagicMock, AsyncMock
import asyncio
from ui.utils import get_safe_upload_data

class TestUIUtilsSurgical:
    """
    Surgical tests for ui/utils.py
    """
    
    @pytest.mark.asyncio
    async def test_get_safe_upload_data_content_coroutine(self):
        """Test reading content when it's a coroutine (async read)."""
        mock_event = MagicMock()
        mock_event.name = "test.txt"
        
        # Mock content.read as async
        mock_event.content.read = AsyncMock(return_value=b"async content")
        # delete other attributes to strictly test this path
        if hasattr(mock_event, 'file'): del mock_event.file
        if hasattr(mock_event, 'files'): del mock_event.files
        
        content, filename = await get_safe_upload_data(mock_event)
        
        assert content == b"async content"
        assert filename == "test.txt"

    @pytest.mark.asyncio
    async def test_get_safe_upload_data_content_sync(self):
        """Test reading content when it's a sync function."""
        mock_event = MagicMock()
        mock_event.name = "sync.txt"
        
        # Mock content.read as sync
        mock_event.content.read.return_value = b"sync content"
        if hasattr(mock_event, 'file'): del mock_event.file
        if hasattr(mock_event, 'files'): del mock_event.files

        content, filename = await get_safe_upload_data(mock_event)
        
        assert content == b"sync content"
        assert filename == "sync.txt"

    @pytest.mark.asyncio
    async def test_get_safe_upload_data_file_starlette(self):
        """Test Starlette UploadFile pattern (e.file)."""
        mock_event = MagicMock()
        del mock_event.content
        del mock_event.name # Simulate name missing on event object
        del mock_event.files
        
        mock_event.file.read = AsyncMock(return_value=b"starlette content")
        mock_event.file.filename = "starlette.file"
        
        content, filename = await get_safe_upload_data(mock_event)
        
        assert content == b"starlette content"
        assert filename == "starlette.file"

    @pytest.mark.asyncio
    async def test_get_safe_upload_data_files_list(self):
        """Test fallback to e.files list."""
        mock_event = MagicMock()
        del mock_event.content
        del mock_event.file
        mock_event.name = "list.txt"
        
        mock_event.files = [b"list content"]
        
        content, filename = await get_safe_upload_data(mock_event)
        
        assert content == b"list content"
        assert filename == "list.txt"

    @pytest.mark.asyncio
    async def test_get_safe_upload_data_exception(self):
        """Test exception handling"""
        mock_event = MagicMock()
        # Ensure content triggers exception
        mock_event.content.read.side_effect = Exception("Read Error")
        
        content, filename = await get_safe_upload_data(mock_event)
        
        assert content is None
        assert filename == "error"
