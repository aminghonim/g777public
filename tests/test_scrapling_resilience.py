import pytest
from unittest.mock import MagicMock, patch
from backend.scrapling_engine import ScraplingEngine


class TestScraplingResilience:
    """
    Failure-First Proof (CNS Rule 1.3)
    Testing how ScraplingEngine handles failures and retries.
    """

    @patch("backend.scrapling_engine.Fetcher.get")
    def test_fetch_retry_logic(self, mock_get):
        # Configure mock to fail twice then succeed
        mock_get.side_effect = [
            ConnectionError("Network Down"),
            ConnectionError("Still Down"),
            MagicMock(status=200),
        ]

        engine = ScraplingEngine()
        # Should succeed after 2 retries
        response = engine.fetch("https://test.com")

        assert mock_get.call_count == 3
        assert response.status == 200

    @patch("backend.scrapling_engine.SCRAPLING_AVAILABLE", False)
    def test_graceful_failure_when_not_installed(self):
        # Test detection of missing library
        engine = ScraplingEngine()
        with pytest.raises(RuntimeError) as excinfo:
            engine.fetch("https://test.com")
        assert "Scrapling engine is not available" in str(excinfo.value)

    def test_extract_invalid_page(self):
        # Test extraction from None or invalid object
        engine = ScraplingEngine()
        results = engine.extract(None, ".some-class")
        assert results == []
