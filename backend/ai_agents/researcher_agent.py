from google import adk
import logging
from typing import List

logger = logging.getLogger("ADKResearcher")


class ResearcherAgent(adk.Agent):
    """
    ADK-compliant Researcher Agent.
    Specializes in specialized data acquisition and technical synthesis.
    """

    def __init__(self):
        super().__init__(
            name="Hunter-Explorer",
            instructions="""
            ROLE: Specialist Researcher & Data Acquisition Hunter.
            TASK: Search the web, extract technical insights, and synthesize reports.
            
            GUIDELINES:
            1. Always verify sources from whitelisted domains (github, pypi, docs).
            2. Present findings in clear Markdown format.
            3. Use 'search_web' and 'read_url_content' tools for information retrieval.
            4. If no information is found, report the negative result clearly.
            """,
        )
        self.domain_whitelist = [
            "google.github.io",
            "github.com",
            "pypi.org",
            "docs.python.org",
        ]

    def validate_url(self, url: str) -> bool:
        from urllib.parse import urlparse

        domain = urlparse(url).netloc
        return any(whitelisted in domain for whitelisted in self.domain_whitelist)
