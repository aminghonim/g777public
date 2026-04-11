"""
Agent Identity Enforcement Module.
Ensures every AI response follows the [AGENT-NAME] protocol.
"""

import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def verify_agent_enforcement(response_text: str, expected_agent: str) -> Tuple[bool, str]:
    """
    Validates that the AI response starts with the correct [AGENT-NAME] header.
    
    Returns:
        (True, "Protocol compliant")
        (False, "Missing agent identity header")
        (False, "Agent mismatch: expected X, got Y")
    """
    if not response_text:
        return False, "Empty response"

    # Pattern: Strict but whitespace-tolerant [AGENT-NAME] at the start
    # Supports A-Z, 0-9, hyphens, and underscores per Architect Review.
    response_text = response_text.lstrip()
    pattern = r"^\[(?P<agent_name>[A-Z0-9\-\_]+)\]"
    match = re.search(pattern, response_text)

    if not match:
        logger.warning("Agent Enforcement Failed: Identity Header Missing or Spaced Maliciously.")
        return False, "Missing agent identity header"

    extracted_agent = match.group("agent_name")
    
    if extracted_agent.upper() != expected_agent.upper():
        logger.error("Agent Enforcement Failed: Expected %s, got %s", expected_agent.upper(), extracted_agent.upper())
        return False, f"Agent mismatch: expected {expected_agent.upper()}, got {extracted_agent.upper()}"

    return True, "Protocol compliant"
