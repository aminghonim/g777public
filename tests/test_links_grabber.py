import pytest
from unittest.mock import patch, MagicMock

import backend.grabber.links_grabber as lg


def test_find_group_links_using_googlesearch(monkeypatch):
    mock_urls = [
        "https://example.com/page?ref=https://chat.whatsapp.com/ABC123",
        "https://chat.whatsapp.com/DEF456",
    ]
    # Inject a fake googlesearch module into sys.modules so the function's import succeeds
    import types, sys

    mod = types.ModuleType("googlesearch")
    mod.search = lambda q, num_results=10: mock_urls
    monkeypatch.setitem(sys.modules, "googlesearch", mod)

    res = lg.find_group_links("Football Fans", limit=10)
    assert any("chat.whatsapp.com/DEF456" in u for u in res)


def test_find_group_links_fallback_duckduckgo(monkeypatch):
    html_text = "Here is a link https://chat.whatsapp.com/ZZZ999 and some text"

    class MockResp:
        def __init__(self, text):
            self.text = text

    monkeypatch.setattr(lg, "gsearch", None, raising=False)
    monkeypatch.setattr("requests.get", lambda *a, **k: MockResp(html_text))

    res = lg.find_group_links("Any", limit=5)
    assert any("chat.whatsapp.com/ZZZ999" in u for u in res)
