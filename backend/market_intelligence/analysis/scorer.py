from typing import List
from ..sources.base import Opportunity

class TrendScorer:
    """
    Evaluates and ranks market opportunities.
    """
    def __init__(self, weights: dict):
        self.weights = weights
        # Default weights if missing
        self.w_freq = weights.get("frequency", 0.4)
        self.w_growth = weights.get("growth", 0.3)
        self.w_rel = weights.get("relevance", 0.3)

    def score_opportunities(self, opportunities: List[Opportunity], config) -> List[Opportunity]:
        """
        Assigns a score (0-100) to each opportunity.
        Filters out low-confidence items.
        """
        scored_list = []
        
        for op in opportunities:
            base_score = 0.0
            
            # 1. Relevance Check (Simple Keyword Matching)
            # If the keyword matches user interest, give it a boost.
            is_relevant = any(k.lower() in op.keyword.lower() for k in config.keywords)
            
            if is_relevant:
                base_score += 50 * self.w_rel
            elif config.niche == "general":
                base_score += 20 * self.w_rel
            
            # 2. Growth/Viral Potential (Mock Logic - depends on source metadata)
            growth = op.metadata.get("growth_factor", 0) # 0 to 1
            base_score += (growth * 100) * self.w_growth
            
            # 3. Frequency (Mock Logic - assumes dedup handling happens before or via count)
            # For now, we take raw base score.
            
            # Final Score normalization
            final_score = min(max(base_score, 0), 100)
            op.score = int(final_score)
            
            # Filter Noise
            if op.score > 20: 
                scored_list.append(op)
                
        # Sort by score info desc
        scored_list.sort(key=lambda x: x.score, reverse=True)
        return scored_list
