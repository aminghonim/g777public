# Knowledge Item: Scrapling Engine Integration Patterns

> **Purpose:** Document the definitive patterns for integrating ScraplingEngine into G777 components. Required by GEMINI.md Rule #14.

## Metadata

- **KI-ID:** `KI-SCRAPLING-001`
- **Component:** Backend (Python Scrapling Integration)
- **Date Added:** 2026-03-15
- **Associated Skill:** `backend/scrapling_engine.py`

---

## Architecture Overview

ScraplingEngine serves as the unified adapter layer for web scraping in G777, providing:
- Config-driven scraping via `config.yaml`
- Stealth capabilities via `StealthyFetcher`
- Automatic retry with exponential backoff
- Graceful fallback when Scrapling is unavailable

---

## Pattern 1: Engine as Default (W-09)

### The Pattern
Make ScraplingEngine the ONLY engine by removing engine selection parameters.

### Implementation
```python
class DataGrabber:
    def __init__(
        self,
        headless: bool = False,
        config_path: str = "config.yaml",  # No engine parameter
    ):
        # Initialize ScraplingEngine exclusively
        GrabberScraper.__init__(self, config_path=config_path, driver=None)
```

### Key Points
- Remove `engine: str = "scrapling"` parameter from `__init__`
- Delete legacy bridge methods (`_run_enhanced_strategy`, `_enhanced_extraction_strategy`)
- All extraction goes through `ScraplingEngine` exclusively

---

## Pattern 2: Session Injector (W-10)

### The Pattern
Implement persistent session management for stateful scraping operations.

### Implementation
```python
class GroupFinder:
    def __init__(
        self,
        config_path: str = "config.yaml",
        sessions_dir: str = ".antigravity/sessions",
    ):
        self.sessions_dir = Path(sessions_dir)
        # Initialize ScraplingEngine for session config
        self.scrapling_engine = ScraplingEngine(config_path)
        
    def _get_session_kwargs(self, session_name: Optional[str] = None) -> Dict[str, Any]:
        """Delegate to ScraplingEngine for centralized session logic."""
        if self.scrapling_engine:
            return self.scrapling_engine._inject_session(session_name)
        return {}
        
    def save_session(self, session_name: str, session_data: Dict[str, Any]) -> bool:
        """Save to .antigravity/sessions/{session_name}.json"""
        session_file = self.sessions_dir / f"{session_name}.json"
        # ... implementation
        
    def load_session(self, session_name: str) -> Optional[Dict[str, Any]]:
        """Load from .antigravity/sessions/{session_name}.json"""
        # ... implementation
        
    def search_with_session_injection(
        self, session_name: str, keywords: List[str], ...
    ) -> List[str]:
        """Enhanced search with persistent state."""
        session_data = self.load_session(session_name) or {}
        existing_links = set(session_data.get("found_links", []))
        self.found_links.update(existing_links)
        # Perform search and update session
        new_links = self.find_groups(keywords, country, max_links)
        self.save_session(session_name, updated_session)
        return new_links
```

### Key Points
- Sessions stored in `.antigravity/sessions/` as JSON files
- Session Injector integrates with ScraplingEngine's config
- Enables resumable scraping across browser restarts

---

## Pattern 3: CNS Compliance (Logging)

### The Pattern
Replace all `print()` statements with `logging` module per CNS Squad standards.

### Anti-Pattern (What NOT to Do)
```python
# WRONG - Violates CNS Squad Rule 8
print("[Hunter] Launching browser...")
print(f"🎯 Found {count} links!")
```

### Correct Pattern
```python
# CORRECT - CNS Squad Compliant
self.logger.info("[Hunter] Launching browser...")
self.logger.info("Found %d links", count)
```

---

## Configuration (config.yaml)

```yaml
scraper_settings:
  engine: "scrapling"
  headless: true
  stealth_mode: true
  adaptive: true
  timeout: 45
  max_concurrency: 5
  
  identity:
    session_vault: "local"
    session_path: ".antigravity/sessions/"
    auto_inject: true
```

---

## Integration Checklist

- [ ] ScraplingEngine initialized in component `__init__`
- [ ] No `print()` statements - only `logger`
- [ ] Config loaded from `config.yaml` (zero hardcoding)
- [ ] Session directory created if not exists
- [ ] Graceful fallback when Scrapling unavailable
- [ ] Type hints on all public methods
- [ ] Docstrings for all public methods

---

## References

- `backend/scrapling_engine.py` - Core engine implementation
- `backend/grabber/main.py` - W-09 implementation reference
- `backend/group_finder.py` - W-10 implementation reference
- `config.yaml` - Configuration specification
