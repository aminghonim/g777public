import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.agents.skills.concise_writer import ConciseWriter


def test_refine_verbose_message():
    verbose = "I have added the ability to log in with Google."
    clean = ConciseWriter.refine_commit_message(verbose)
    # Heuristic might add "feat:"
    assert clean.startswith("feat:")
    assert "I have " not in clean


def test_refine_maintain_type():
    msg = "fix: resolve null pointer exception"
    clean = ConciseWriter.refine_commit_message(msg)
    assert clean == "fix: resolve null pointer exception"
