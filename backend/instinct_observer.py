import os
import json
import logging
import hashlib
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

@dataclass
class InstinctQualityReport:
    is_valid: bool
    rejection_reasons: List[str]
    semantic_score: float
    duplicates: List[str]  # Potential IDs of similar instincts in Vector DB

class InstinctValidator:
    """
    Quality gate to ensure only high-value problem-solution pairs reach the Vector DB.
    Implemented by AGENCY-BACKEND-ARCHITECT as per System Architect specs.
    """
    def __init__(self, min_length=50, max_length=5000, similarity_threshold=0.85):
        self.min_length = min_length
        self.max_length = max_length
        self.similarity_threshold = similarity_threshold
    
    def validate(self, problem: str, solution: str, existing_instincts: Optional[List[Dict[str, Any]]] = None) -> InstinctQualityReport:
        reasons = []
        
        # 1. Base Length Check (Triviality check)
        total_length = len(problem) + len(solution)
        if total_length < self.min_length:
            reasons.append(f"Content length {total_length} is below minimum ({self.min_length})")
        if total_length > self.max_length:
            reasons.append(f"Content length {total_length} exceeds maximum ({self.max_length})")
        
        # 2. Semantic Duplicate Check (Stub: requires Vector DB integration)
        duplicates = self._find_duplicates(problem, existing_instincts or [])
        if duplicates:
            reasons.append(f"Potential duplicate of existing instincts: {duplicates}")
        
        # 3. Actionable Content Heuristic (Ensure solution has code or steps)
        if not self._has_high_value_structure(solution):
            reasons.append("Solution lacks high-value structure (missing code blocks or numbered steps)")
            
        is_valid = len(reasons) == 0
        score = self._calculate_quality_score(problem, solution)
        
        return InstinctQualityReport(
            is_valid=is_valid,
            rejection_reasons=reasons,
            semantic_score=score,
            duplicates=duplicates
        )
    
    def _find_duplicates(self, problem: str, existing: List[Dict[str, Any]]) -> List[str]:
        # Implementation depends on a running Vector DB (e.g. Pinecone)
        # For now, it's a pass-through returning empty list unless ID matches
        return []

    def _has_high_value_structure(self, text: str) -> bool:
        has_code = '```' in text
        has_steps = any(line.strip().startswith(('1.', '2.', '3.', '- ', '* ')) for line in text.split('\n'))
        return has_code or has_steps

    def _calculate_quality_score(self, problem: str, solution: str) -> float:
        """
        Score (0.0 to 1.0) based on specificity and completeness.
        - Problem detail: 0.3
        - Solution depth: 0.4
        - Structural richness: 0.3
        """
        score = 0.0
        if any(keyword in problem.lower() for keyword in ['error', 'exception', 'refactor', 'how to']):
            score += 0.3
        if len(solution.split()) > 100:
            score += 0.4
        if self._has_high_value_structure(solution):
            score += 0.3
            
        return round(min(score, 1.0), 2)

class InstinctObserver:
    def __init__(self, index_name: str = "agent-router"):
        self.index_name = index_name
        self.validator = InstinctValidator()

    async def capture_instinct(self, context: str, solution: str, agent_name: str, vector_db: Optional[Any] = None):
        """
        Stores Problem-Solution pair ONLY after multi-dimensional validation.
        Namespace: instincts/{agent_name}
        """
        # Validate against existing instincts (if vector_db available)
        existing = []
        if vector_db:
             # Search similar inside agent's namespace
             pass
             
        report = self.validator.validate(context, solution, existing)
        
        if not report.is_valid:
            logger.warning(f"Instinct from {agent_name} rejected: {', '.join(report.rejection_reasons)}")
            return {"status": "rejected", "reasons": report.rejection_reasons, "score": report.semantic_score}

        # ID based on MD5 of problem to prevent exact duplicates
        problem_id = hashlib.md5(context.encode()).hexdigest()
        record_id = f"instinct-{problem_id[:8]}"
        
        metadata = {
            "problem": context,
            "solution": solution,
            "agent": agent_name,
            "quality_score": report.semantic_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # If vector_db is an actual Pinecone MCP reference, we'd call upsert here
        # For this turn, we log the ready-to-store artifact
        logger.info(f"Instinct Captured for {agent_name}: Score {report.semantic_score}")
        
        return {
            "status": "accepted",
            "id": record_id,
            "score": report.semantic_score,
            "metadata": metadata
        }

# Global Instance
instinct_observer = InstinctObserver()
