import pytest
from unittest.mock import patch, MagicMock

from backend.groups.auto_joiner import AutoJoiner


class DummyResp:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}

    def json(self):
        return self._json


def test_join_groups_success_and_failure(monkeypatch):
    aj = AutoJoiner(api_url="https://evo.test", api_key="KEY")

    calls = []

    def fake_post(url, json, headers, timeout):
        calls.append((url, json))
        if "GOOD" in json.get("invite_link"):
            return DummyResp(200, {"ok": True})
        return DummyResp(400, {"error": "Bad Link"})

    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setattr("time.sleep", lambda s: None)

    links = ["https://chat.whatsapp.com/GOOD1", "https://chat.whatsapp.com/BAD2"]
    summary = aj.join_groups(
        links, delay=30, stop_after_consecutive_failures=10, dry_run=False
    )

    assert len(summary["successes"]) == 1
    assert len(summary["failures"]) == 1
    assert any("Bad Link" in str(f[1]) for f in summary["failures"]) or any(
        "http_400" in str(f[1]) for f in summary["failures"]
    )


def test_join_groups_dry_run(monkeypatch):
    """Verify that in dry_run mode, everything is a success without network calls."""
    aj = AutoJoiner(api_url="https://evo.test", api_key="KEY")

    def fake_post_should_not_be_called(url, json, headers, timeout):
        pytest.fail("Network call should not be made during dry_run")

    monkeypatch.setattr("requests.post", fake_post_should_not_be_called)
    monkeypatch.setattr("time.sleep", lambda s: None)

    links = ["https://chat.whatsapp.com/ANYTHING", "https://chat.whatsapp.com/INVALID"]
    # Even invalid format links (if they pass the regex) should be 'success' in dry_run if we skip validation?
    # Wait, AutoJoiner still validates format before dry_run check.

    summary = aj.join_groups(links, dry_run=True)

    # Note: 'INVALID' will fail regex validation even in dry_run
    # Valid regex link: https://chat.whatsapp.com/ABC123
    links = [
        "https://chat.whatsapp.com/ABC123_valid",
        "https://chat.whatsapp.com/XYZ789_valid",
    ]
    summary = aj.join_groups(links, dry_run=True)

    assert len(summary["successes"]) == 2
    assert len(summary["failures"]) == 0
