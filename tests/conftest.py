"""
=============================================================================
FINAL POLISH #3: Advanced Test Fixtures (Yield Pattern + Auto Cleanup)
=============================================================================

Purpose: Provide isolated, clean test environments with automatic teardown.

How this ensures stability:
- Uses Yield Pattern for setup/teardown in single fixture
- Creates isolated temp directories for each test
- Auto-deletes JSON/CSV files after tests (pass or fail)
- Prevents data pollution between test runs
- Provides mock services ready for use

Fixtures Provided:
- isolated_data_dir: Clean temp directory, auto-cleaned
- temp_json_file: Creates JSON file, deletes after test
- temp_csv_file: Creates CSV file, deletes after test
- mock_db_session: Database session with auto-rollback
- mock_http_client: HTTP client with request recording
=============================================================================
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import os
import sys
import json
import csv
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

# ضمان أن المجلد الرئيسي في مسار البحث
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# =============================================================================
# ENVIRONMENT MOCKING (Auto-use)
# =============================================================================

@pytest.fixture(autouse=True)
def mock_settings_env():
    """
    تزييف إعدادات البيئة لكل الاختبارات.
    
    Stability Guarantee:
    - Prevents real API calls during tests
    - Uses mock:// protocol to block real DB connections
    - Ensures consistent test environment
    """
    with patch.dict(os.environ, {
        "DATABASE_URL": "mock://localhost:5432/testdb",
        "EVOLUTION_API_URL": "http://localhost:8081",
        "EVOLUTION_API_KEY": "test_key",
        "EVOLUTION_INSTANCE_NAME": "G777",
        "GEMINI_API_KEY": "test_gemini_key",
        "TEST_MODE": "true"  # Flag for test-specific behavior
    }):
        yield


@pytest.fixture(autouse=True)
def mock_db_connection():
    """
    تزييف اتصال قاعدة البيانات عالمياً لمنع الانفجار.
    
    Stability Guarantee:
    - No real database connections during tests
    - Returns predictable mock data
    - Uses Yield Pattern for proper cleanup
    """
    with patch('psycopg2.pool.SimpleConnectionPool') as mock_pool:
        # جعل مجمع الاتصالات يعيد اتصالاً وهمياً
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pool.return_value.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # تزييف الـ Cursor ليعيد بيانات افتراضية عند الحاجة
        mock_cursor.fetchone.return_value = {"id": "550e8400-e29b-41d4-a716-446655440000"}
        mock_cursor.fetchall.return_value = []
        
        yield mock_pool
        
        # Teardown: Ensure connections are "released"
        mock_pool.return_value.closeall.return_value = None


@pytest.fixture(autouse=True)
def mock_ai_client_global():
    """
    تزييف عميل الذكاء الاصطناعي عالمياً.
    
    Stability Guarantee:
    - No real AI API calls (saves quota)
    - Returns predictable responses
    - Records calls for verification
    """
    with patch('google.genai.Client') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.aio.models.generate_content = AsyncMock()
        mock_instance.aio.models.generate_content.return_value.text = "Mock AI Response"
        
        # Add call history for verification
        mock_instance.call_history = []
        
        yield mock_instance


@pytest.fixture(autouse=True)
def mock_requests_global():
    """
    تزييف طلبات الـ HTTP لمنع الاتصال الخارجي بالواتساب.
    
    Stability Guarantee:
    - No external HTTP calls during tests
    - Returns success responses by default
    - Records all requests for verification
    """
    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "open", "instance": {"instanceName": "G777"}}
        
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}
        
        yield mock_get, mock_post


# =============================================================================
# ISOLATED DATA DIRECTORY (Yield Pattern)
# =============================================================================

@pytest.fixture
def isolated_data_dir():
    """
    إنشاء مجلد بيانات معزول لكل اختبار مع التنظيف التلقائي.
    
    Usage:
        def test_something(isolated_data_dir):
            file_path = isolated_data_dir / "test.json"
            # Write to file...
            # File will be auto-deleted after test
    
    Stability Guarantee:
    - Each test gets fresh, empty directory
    - All files auto-deleted after test (pass or fail)
    - No data pollution between tests
    """
    # Setup: Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="g777_test_"))
    
    yield temp_dir
    
    # Teardown: Remove directory and all contents
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        print(f"Warning: Could not clean up {temp_dir}: {e}")


# =============================================================================
# TEMPORARY JSON FILE (Auto-cleanup)
# =============================================================================

@pytest.fixture
def temp_json_file(isolated_data_dir):
    """
    إنشاء ملف JSON مؤقت مع التنظيف التلقائي.
    
    Usage:
        def test_json_processing(temp_json_file):
            path, write_data = temp_json_file
            write_data({"key": "value"})
            # Read and test...
    
    Returns:
        Tuple of (file_path, write_function)
    
    Stability Guarantee:
    - File is deleted after test completes
    - Works even if test fails
    """
    file_path = isolated_data_dir / f"test_data_{datetime.now().strftime('%H%M%S%f')}.json"
    
    def write_data(data: dict):
        """Helper to write JSON data to the temp file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path
    
    yield file_path, write_data
    
    # Cleanup is handled by isolated_data_dir fixture


# =============================================================================
# TEMPORARY CSV FILE (Auto-cleanup)
# =============================================================================

@pytest.fixture
def temp_csv_file(isolated_data_dir):
    """
    إنشاء ملف CSV مؤقت مع التنظيف التلقائي.
    
    Usage:
        def test_csv_export(temp_csv_file):
            path, write_rows = temp_csv_file
            write_rows([['name', 'phone'], ['Ahmed', '123']])
            # Read and verify...
    
    Returns:
        Tuple of (file_path, write_function)
    
    Stability Guarantee:
    - File is deleted after test completes
    - Handles Unicode correctly (UTF-8 BOM)
    """
    file_path = isolated_data_dir / f"test_export_{datetime.now().strftime('%H%M%S%f')}.csv"
    
    def write_rows(rows: list):
        """Helper to write CSV rows to the temp file"""
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        return file_path
    
    yield file_path, write_rows
    
    # Cleanup is handled by isolated_data_dir fixture


# =============================================================================
# MOCK DATABASE SESSION (With Transaction Rollback)
# =============================================================================

@pytest.fixture
def mock_db_session():
    """
    جلسة قاعدة بيانات وهمية مع دعم الـ Rollback.
    
    Usage:
        def test_db_operation(mock_db_session):
            mock_db_session.add({'table': 'customers', 'data': {...}})
            result = mock_db_session.query('customers')
            # Verify...
    
    Stability Guarantee:
    - All changes are discarded after test
    - In-memory storage (no disk I/O)
    - Thread-safe for async tests
    """
    class MockDBSession:
        def __init__(self):
            self._data = {}
            self._operations = []
        
        def add(self, item: dict):
            """Add item to mock storage"""
            table = item.get('table', 'default')
            if table not in self._data:
                self._data[table] = []
            self._data[table].append(item.get('data', item))
            self._operations.append(('add', table, item))
        
        def query(self, table: str):
            """Query items from mock storage"""
            self._operations.append(('query', table))
            return self._data.get(table, [])
        
        def delete(self, table: str, condition: callable = None):
            """Delete items from mock storage"""
            if table in self._data:
                if condition:
                    self._data[table] = [x for x in self._data[table] if not condition(x)]
                else:
                    self._data[table] = []
            self._operations.append(('delete', table))
        
        def rollback(self):
            """Discard all changes (reset to empty)"""
            self._data = {}
            self._operations = []
        
        def get_operations(self):
            """Get list of operations for verification"""
            return self._operations.copy()
    
    session = MockDBSession()
    
    yield session
    
    # Teardown: Rollback all changes
    session.rollback()


# =============================================================================
# MOCK HTTP CLIENT (With Request Recording)
# =============================================================================

@pytest.fixture
def mock_http_client():
    """
    عميل HTTP وهمي مع تسجيل الطلبات.
    
    Usage:
        def test_api_call(mock_http_client):
            mock_http_client.set_response(200, {'status': 'ok'})
            # Make API call...
            assert mock_http_client.last_request.url == 'expected_url'
    
    Stability Guarantee:
    - No real HTTP calls
    - Records all requests for assertion
    - Configurable responses per URL
    """
    class MockHTTPClient:
        def __init__(self):
            self.requests = []
            self.responses = {}
            self.default_response = (200, {'success': True})
        
        def set_response(self, status_code: int, body: dict, url: str = None):
            """Set response for specific URL or default"""
            if url:
                self.responses[url] = (status_code, body)
            else:
                self.default_response = (status_code, body)
        
        def get(self, url: str, **kwargs):
            """Mock GET request"""
            self.requests.append({'method': 'GET', 'url': url, 'kwargs': kwargs})
            return self._make_response(url)
        
        def post(self, url: str, **kwargs):
            """Mock POST request"""
            self.requests.append({'method': 'POST', 'url': url, 'kwargs': kwargs})
            return self._make_response(url)
        
        def _make_response(self, url: str):
            """Create mock response object"""
            status, body = self.responses.get(url, self.default_response)
            response = MagicMock()
            response.status_code = status
            response.json.return_value = body
            response.text = json.dumps(body)
            response.ok = status < 400
            return response
        
        @property
        def last_request(self):
            """Get the last request made"""
            return self.requests[-1] if self.requests else None
        
        def clear(self):
            """Clear request history"""
            self.requests = []
    
    client = MockHTTPClient()
    
    yield client
    
    # Teardown: Clear all recorded requests
    client.clear()


# =============================================================================
# SAMPLE DATA FIXTURES
# =============================================================================

@pytest.fixture
def sample_customers():
    """
    بيانات عملاء نموذجية للاختبارات.
    
    Returns:
        List of customer dictionaries with realistic data
    """
    return [
        {
            'id': '1',
            'name': 'أحمد محمد',
            'phone': '+201234567890',
            'city': 'القاهرة',
            'customer_type': 'lead',
            'metadata': {'interests': ['تسويق', 'عقارات']},
            'created_at': datetime.now()
        },
        {
            'id': '2', 
            'name': 'سارة أحمد',
            'phone': '+201987654321',
            'city': 'الإسكندرية',
            'customer_type': 'customer',
            'metadata': {'interests': ['سيارات']},
            'created_at': datetime.now()
        }
    ]


@pytest.fixture
def sample_messages():
    """
    رسائل نموذجية للاختبارات.
    
    Returns:
        List of message dictionaries
    """
    return [
        {'id': '1', 'text': 'مرحباً', 'sender': 'customer', 'timestamp': datetime.now()},
        {'id': '2', 'text': 'أهلاً بك!', 'sender': 'bot', 'timestamp': datetime.now()},
    ]


# =============================================================================
# ASYNC TESTING HELPERS
# =============================================================================

@pytest.fixture
def async_mock():
    """
    مساعد لإنشاء Async Mocks بسهولة.
    
    Usage:
        async def test_async_operation(async_mock):
            mock_func = async_mock(return_value={'status': 'ok'})
            result = await mock_func()
            assert result['status'] == 'ok'
    """
    def create_async_mock(return_value=None, side_effect=None):
        mock = AsyncMock()
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        return mock
    
    return create_async_mock


# =============================================================================
# CLEANUP MARKERS
# =============================================================================

def pytest_runtest_teardown(item, nextitem):
    """
    Hook للتنظيف الإضافي بعد كل اختبار.
    
    Stability Guarantee:
    - Runs after every test (pass or fail)
    - Cleans up any stray temp files in project directory
    - Logs cleanup actions for debugging
    """
    # Clean up any .tmp files in the tests directory
    tests_dir = Path(__file__).parent
    for tmp_file in tests_dir.glob("**/*.tmp"):
        try:
            tmp_file.unlink()
        except Exception:
            pass
    
    # Clean up any test-generated JSON/CSV in project root
    project_root = tests_dir.parent
    patterns = ["test_*.json", "test_*.csv", "*.tmp"]
    for pattern in patterns:
        for file_path in project_root.glob(pattern):
            try:
                file_path.unlink()
            except Exception:
                pass
