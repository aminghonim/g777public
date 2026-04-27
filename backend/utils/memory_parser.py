"""
Memory Parser for Antigravity.
Transforms Markdown MEMORY.md into structured data objects.
"""

import re
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class MemoryCategory(Enum):
    ERROR = "error"
    SUCCESS = "success"
    DECISION = "decision"
    REFACTORING = "refactoring"

@dataclass
class MemoryEntry:
    timestamp: datetime
    agent_involved: str
    category: MemoryCategory
    context: str
    outcome: Optional[str] = None

def parse_memory_md(file_path: str) -> List[MemoryEntry]:
    """
    Parses the MEMORY.md file into a list of MemoryEntry objects.
    Expects format: ## [YYYY-MM-DD HH:MM:SS] - Category
    """
    entries: List[MemoryEntry] = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if not lines:
            return []
            
        # 1. Schema Versioning Check (Architect Review Fix)
        first_line = lines[0]
        version = "unknown"
        v_match = re.search(r"Schema-Version:\s*(?P<ver>[\d\.]+)", first_line)
        if v_match:
            version = v_match.group("ver")
            logger.info("Parsing Memory with Schema-Version: %s", version)
        
        content = "".join(lines)
            
        # 2. Split by level 2 headers
        sections = re.split(r"##\s*\[", content)
        
        for section in sections:
            if not section.strip():
                continue
                
            # Full pattern: [2026-03-23 20:00:00] - Category
            # We reconstruct the split parts
            match = re.search(r"(?P<ts>.*?)\]\s*-\s*(?P<cat>\w+)\n(?P<body>.*)", section, re.DOTALL)
            if not match:
                continue
                
            ts_str = match.group("ts")
            cat_str = match.group("cat").lower()
            body = match.group("body").strip()
            
            # Extract Agent and Outcome from body lines
            agent = "Unknown"
            agent_match = re.search(r"- Agent:\s*(?P<agent>.*)", body)
            if agent_match:
                agent = agent_match.group("agent").strip()
                
            outcome = None
            outcome_match = re.search(r"- Outcome:\s*(?P<outcome>.*)", body)
            if outcome_match:
                outcome = outcome_match.group("outcome").strip()
                
            try:
                # Tentative category mapping
                category = MemoryCategory(cat_str)
            except ValueError:
                category = MemoryCategory.DECISION # Default fallback

            try:
                # Normalization to UTC (Architect Review Fix)
                ts = datetime.fromisoformat(ts_str) if ts_str else datetime.now(timezone.utc)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                else:
                    ts = ts.astimezone(timezone.utc)
            except (ValueError, TypeError):
                ts = datetime.now(timezone.utc)

            entries.append(MemoryEntry(
                timestamp=ts,
                agent_involved=agent,
                category=category,
                context=body,
                outcome=outcome
            ))
            
    except FileNotFoundError:
        return []
        
    return entries
