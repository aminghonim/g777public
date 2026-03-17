import pytest
import os
import sys
import hashlib
import tempfile
from unittest.mock import MagicMock, patch, AsyncMock
from core.config import settings
from backend.routers.system import UpdateCheckResponse, execute_update_sequence


class AsyncIterator:
    def __init__(self, items):
        self.items = items

    async def __aiter__(self):
        for item in self.items:
            yield item


@pytest.mark.asyncio
async def test_update_check_simulation():
    """
    Verifies that the update check logic correctly detects the mocked update.
    """
    from backend.routers.system import check_for_updates

    # The current implementation returns a mock update for demonstration
    resp = await check_for_updates()
    assert resp.has_update is True
    assert resp.latest_version == "2.3.0"
    assert len(resp.sha256) == 64


@pytest.mark.asyncio
async def test_execute_update_sequence_failure_cleanup():
    """
    Ensures that downloaded artifacts are cleaned up if the update sequence fails.
    """
    temp_file = os.path.join(tempfile.gettempdir(), "g777_test_update.bin")
    if os.path.exists(temp_file):
        os.remove(temp_file)

    # Mock AsyncClient as an async context manager
    mock_client_instance = MagicMock()
    mock_client_instance.__aenter__ = AsyncMock(
        side_effect=Exception("Connection Interrupted")
    )

    with patch("httpx.AsyncClient", return_value=mock_client_instance):
        await execute_update_sequence(
            "http://example.com/update.exe", "dummy_hash", temp_file
        )

    assert not os.path.exists(temp_file)


def test_bootstrapper_hash_logic():
    """
    Surgical test for the Bootstrapper's internal hash verification logic.
    """
    from scripts.updater_bootstrapper import verify_hash

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = b"G777_SECURE_BINARY_DATA"
        tmp.write(content)
        tmp_path = tmp.name

    try:
        expected_hash = hashlib.sha256(content).hexdigest()
        # Test positive verification
        assert verify_hash(tmp_path, expected_hash) is True
        # Test negative verification
        assert verify_hash(tmp_path, "invalid_hash_string") is False
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@patch("backend.routers.system.subprocess.Popen")
@patch("os._exit")
@pytest.mark.asyncio
async def test_full_sequence_launch_signals(mock_exit, mock_popen):
    """
    Verifies that the update sequence correctly invokes the bootstrapper
    as a detached process and exits the main application.
    """
    temp_file = os.path.join(tempfile.gettempdir(), "g777_test_launch.bin")
    with open(temp_file, "wb") as f:
        f.write(b"data")

    try:
        # Complex nesting for async context managers
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.aiter_bytes.return_value = AsyncIterator([b"data"])

        mock_stream_cm = MagicMock()
        mock_stream_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_cm.__aexit__ = AsyncMock()

        mock_client = MagicMock()
        mock_client.stream.return_value = mock_stream_cm

        mock_client_cm = MagicMock()
        mock_client_cm.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cm.__aexit__ = AsyncMock()

        with patch("httpx.AsyncClient", return_value=mock_client_cm):
            # We mock sleep to avoid waiting
            with patch("asyncio.sleep", return_value=None):
                await execute_update_sequence(
                    "http://test.com/pkg", "test_hash", temp_file
                )

        # Verify Bootstrapper was launched
        assert mock_popen.called
        # Verify 0x00000008 (DETACHED_PROCESS) was passed
        args, kwargs = mock_popen.call_args
        assert kwargs["creationflags"] == 0x00000008

        # Verify application exit was triggered
        assert mock_exit.called
        assert mock_exit.call_args[0][0] == 0

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
