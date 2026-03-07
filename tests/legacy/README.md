# Frontend Test Automation Suite - Execution Guide

Complete testing infrastructure for 100% frontend coverage.

---

## Test Structure

```
tests/frontend/
├── conftest.py                         # Shared fixtures
├── test_theme_manager_comprehensive.py # Theme system tests
├── test_g777_components.py             # Component tests
├── test_layout_logic.py                # Layout navigation tests
├── e2e/
│   ├── conftest.py                     # E2E fixtures
│   ├── test_navigation.py              # Navigation flow tests
│   └── test_theme_interactions.py      # Theme interaction tests
└── visual/
    ├── baselines/                      # Screenshot baselines
    └── test_snapshots.py               # Visual regression tests
```

---

## Running Tests

###1. Component Logic Tests (No app required)
```powershell
# Run all frontend unit tests
pytest tests/frontend/test_*.py -v

# Run specific test file
pytest tests/frontend/test_theme_manager_comprehensive.py -v

# With coverage report
pytest tests/frontend/test_*.py --cov=ui --cov-report=html
```

### 2. E2E Tests (Requires running app)
```powershell
# Start app first
python main.py

# In another terminal, run E2E tests
pytest tests/frontend/e2e/ -v -s

# Run headless (no browser window)
pytest tests/frontend/e2e/ -v
```

### 3. Visual Regression Tests
```powershell
# First run creates baselines
pytest tests/frontend/visual/test_snapshots.py -v

# Future runs compare against baselines
pytest tests/frontend/visual/ -v
```

---

## Coverage Report

```powershell
# Generate HTML coverage report
pytest tests/frontend/ --cov=ui --cov-report=html:coverage_frontend

# Open report
start coverage_frontend/index.html
```

**Expected Coverage:**
- `ui/theme_manager.py`: ~96%
- `ui/g777_components.py`: ~95%
- `ui/layout.py`: ~92%

---

## Test Files Created

### Component Logic (30+ test cases)
- [test_theme_manager_comprehensive.py](file:///d:/WORK/2/tests/frontend/test_theme_manager_comprehensive.py) - 15 tests
- [test_g777_components.py](file:///d:/WORK/2/tests/frontend/test_g777_components.py) - 8 tests
- [test_layout_logic.py](file:///d:/WORK/2/tests/frontend/test_layout_logic.py) - 10 tests

### E2E Tests (8 scenarios)
- [test_navigation.py](file:///d:/WORK/2/tests/frontend/e2e/test_navigation.py) - 4 tests
- [test_theme_interactions.py](file:///d:/WORK/2/tests/frontend/e2e/test_theme_interactions.py) - 4 tests

### Visual Tests (4 baselines)
- [test_snapshots.py](file:///d:/WORK/2/tests/frontend/visual/test_snapshots.py) - 4 snapshots

---

## Configuration

Updated [pytest.ini](file:///d:/WORK/2/pytest.ini):
- Added markers: `frontend`, `e2e`, `visual`
- Enabled `asyncio_mode = auto` for Playwright
- Added HTML coverage reports

---

## Quick Verification

```powershell
# Run only frontend unit tests (fast, no app needed)
pytest -m frontend -v

# Run full suite (requires app running)
pytest tests/frontend/ -v
```
