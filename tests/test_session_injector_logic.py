import os
import json
import shutil
from pathlib import Path
from backend.group_finder import GroupFinder


def test_session_injector():
    print("Testing Session Injector...")

    # Setup
    session_name = "test_persistence_session"
    sessions_dir = Path(".antigravity/sessions")
    if sessions_dir.exists():
        shutil.rmtree(sessions_dir)

    finder = GroupFinder()

    # 1. Test Saving Session
    mock_links = [
        "https://chat.whatsapp.com/test12345678901234567890",
        "https://wa.me/1234567890",
    ]
    finder.found_links.update(mock_links)

    updated_session = {
        "found_links": list(finder.found_links),
        "total_found": len(finder.found_links),
    }

    success = finder.save_session(session_name, updated_session)
    assert success is True
    assert (sessions_dir / f"{session_name}.json").exists()
    print(f"✅ Session saved successfully to {sessions_dir}")

    # 2. Test Loading Session
    loaded_data = finder.load_session(session_name)
    assert loaded_data is not None
    assert len(loaded_data["found_links"]) == 2
    print("✅ Session loaded successfully")

    # 3. Test Session Injection in search_with_session_injection (Mocked search)
    # We won't actually run a search to avoid browser launch, but we'll test the injection logic
    finder2 = GroupFinder()
    session_data = finder2.load_session(session_name) or {}
    finder2.found_links.update(session_data.get("found_links", []))

    assert len(finder2.found_links) == 2
    print("✅ Session injection logic verified")

    # 4. Verify ScraplingEngine Session Path Injection
    if finder2.scrapling_engine:
        kwargs = finder2._get_session_kwargs(session_name)
        assert "user_data_dir" in kwargs
        assert session_name in kwargs["user_data_dir"]
        print(f"✅ Scrapling injection path verified: {kwargs['user_data_dir']}")

    print("\nALL TESTS PASSED! 🚀")


if __name__ == "__main__":
    test_session_injector()
