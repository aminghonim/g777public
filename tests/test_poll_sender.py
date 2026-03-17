import pytest
from unittest.mock import patch

from backend.senders.poll_sender import send_poll


class DummyResp:
    def __init__(self, status_code=200, json_data=None, text="ok"):
        self.status_code = status_code
        self._json = json_data or {"sent": True}
        self.text = text

    def json(self):
        return self._json


def test_send_poll_success(monkeypatch):
    def fake_post(url, json, headers, timeout):
        return DummyResp(200, {"sent": True, "endpoint": url})

    monkeypatch.setattr("requests.post", fake_post)
    res = send_poll(
        "12345@g.us", "Q?", ["A", "B"], api_url="https://evo.test", api_key="K"
    )
    assert res["ok"] is True
    assert "endpoint" in res["response"] or res["response"].get("sent")


def test_send_poll_missing_url():
    import os

    # Ensure env var not present for this test
    os.environ.pop("EVOLUTION_API_URL", None)
    res = send_poll("jid", "Q", ["A"], api_url=None, api_key=None)
    assert res["ok"] is False
    assert res["response"] == "missing_api_url"
