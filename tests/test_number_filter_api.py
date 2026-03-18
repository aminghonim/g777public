
import io
import pytest
from typing import Any, Dict
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock

from main import app
import api.number_filter as nf_module
from core.security import SecurityEngine


@pytest.fixture(autouse=True)
def mock_controller(monkeypatch: Any) -> Mock:
    """Replace the real NumberFilterController with a controllable mock.

    This prevents any external calls to WhatsApp APIs or DBs and ensures
    tests are deterministic (Zero-Regression Protocol).
    """
    mock = Mock()
    mock.set_file_path = Mock()
    mock.get_sheet_names = Mock(return_value=["Sheet1", "Sheet2"])  # type: ignore
    mock.process_excel_file = Mock(return_value=(["A", "B"], ["123", "456"]))
    mock.run_validation = AsyncMock(return_value={"total": 2, "valid": 2, "invalid": 0})
    mock.stop_validation = Mock()
    mock.export_valid = Mock(return_value="data/exports/valid_numbers.xlsx")

    monkeypatch.setattr(nf_module, "controller", mock)
    return mock


@pytest.fixture()
def client(monkeypatch: Any) -> TestClient:
    # Set up a fake session for the SecurityEngine
    fake_token = "test-token-123"
    monkeypatch.setattr(SecurityEngine, "get_current_session", lambda: {"token": fake_token})
    
    # Create client with the auth token in headers
    c = TestClient(app, raise_server_exceptions=False)
    c.headers.update({"X-G777-Auth-Token": fake_token})  # Using X-G777-Auth-Token as per config
    return c


def test_upload_file_success(client: TestClient, mock_controller: Mock) -> None:
    file_stream = io.BytesIO(b"dummy content")
    files = {
        "file": (
            "test.xlsx",
            file_stream,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    # Note on URL: The router is registered without prefix in router_registry.py?
    # No, router_registry.py includes router as is.
    # api/number_filter.py defines prefix="/api/number-filter".
    # So the URL is /api/number-filter/upload
    
    resp = client.post("/api/number-filter/upload", files=files)
    assert resp.status_code == 200
    body: Dict[str, Any] = resp.json()
    assert body["filename"] == "test.xlsx"
    assert body["sheets"] == ["Sheet1", "Sheet2"]
    
    # Verify controller logic was called
    mock_controller.set_file_path.assert_called_once()
    mock_controller.get_sheet_names.assert_called_once()


def test_upload_missing_file_returns_422(client: TestClient) -> None:
    # Sending request without 'file' field
    resp = client.post("/api/number-filter/upload", data={"other": "data"})
    assert resp.status_code == 422


def test_process_sheet_success(client: TestClient, mock_controller: Mock) -> None:
    resp = client.get("/api/number-filter/sheets/Sheet1/process")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 2
    assert data["numbers"] == ["123", "456"]
    
    mock_controller.process_excel_file.assert_called_with(
        sheet_name="Sheet1", target_column=None
    )


def test_process_sheet_with_column_param(client: TestClient, mock_controller: Mock) -> None:
    resp = client.get("/api/number-filter/sheets/Sheet1/process?column=Phone")
    assert resp.status_code == 200
    
    mock_controller.process_excel_file.assert_called_with(
        sheet_name="Sheet1", target_column="Phone"
    )


def test_process_sheet_raises_500_on_controller_error(
    client: TestClient, mock_controller: Mock
) -> None:
    # Simulate an error in the controller
    mock_controller.process_excel_file.side_effect = Exception("Excel Error")
    
    # Since we disabled raise_server_exceptions=False, assert 500
    # But wait, does the endpoint catch exceptions?
    # Inspecting api/number_filter.py: process_sheet does NOT wrap in try/except.
    # So generic error handler (if any) or 500.
    # If using Starlette TestClient with raise_server_exceptions=False, it returns 500.
    
    resp = client.get("/api/number-filter/sheets/Sheet1/process")
    assert resp.status_code == 500


def test_start_validation_calls_controller_and_returns_results(
    client: TestClient, mock_controller: Mock
) -> None:
    resp = client.post("/api/number-filter/validate")
    assert resp.status_code == 200
    assert resp.json() == {"total": 2, "valid": 2, "invalid": 0}
    
    mock_controller.run_validation.assert_called_once()


def test_stop_validation_calls_controller(client: TestClient, mock_controller: Mock) -> None:
    resp = client.post("/api/number-filter/stop")
    assert resp.status_code == 200
    assert resp.json() == {"status": "stopped"}
    
    mock_controller.stop_validation.assert_called_once()


def test_export_valid_success(client: TestClient, mock_controller: Mock) -> None:
    resp = client.post("/api/number-filter/export")
    assert resp.status_code == 200
    data = resp.json()
    assert "valid_numbers.xlsx" in data["filename"]
    assert "data/exports/valid_numbers.xlsx" in data["path"]
    
    mock_controller.export_valid.assert_called_once()


def test_export_valid_no_data_returns_400(client: TestClient, mock_controller: Mock) -> None:
    # Simulate return empty/None
    mock_controller.export_valid.return_value = None
    
    resp = client.post("/api/number-filter/export")
    assert resp.status_code == 400
    assert "No valid numbers" in resp.json()["detail"]
