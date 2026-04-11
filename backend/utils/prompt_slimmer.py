import numpy as np
import logging
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class SemanticPromptSlimmer:
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        # TF-IDF (Term Frequency-Inverse Document Frequency)
        # unigrams + bigrams for more semantic richness
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_df=0.85
        )

    def compress(self, context_chunks: List[str], query: str) -> str:
        """
        Maintains semantic context by selecting chunks that are mathematically 
        similar to the query using Cosine Similarity over TF-IDF vectors.
        Implemented by AGENCY-BACKEND-ARCHITECT as per System Architect specs.
        """
        if not context_chunks:
            return ""
            
        # 1. Prepare entire text pool for vectorization (query is at index 0)
        all_texts = [query] + context_chunks
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        except ValueError as e:
            # fit_transform might fail if texts are only stop words
            logger.warning(f"TF-IDF failed: {e}. Falling back to original content.")
            return "\n\n".join(context_chunks[:5])

        # 2. Extract Query vector and Context vectors
        query_vec = tfidf_matrix[0:1]
        context_vecs = tfidf_matrix[1:]
        
        # 3. Calculate similarity scores
        temp_sim = cosine_similarity(query_vec, context_vecs).flatten()
        similarities = temp_sim if temp_sim.size > 0 else np.zeros(len(context_chunks))
        
        # 4. Rank and select chunks based on token budget
        selected: List[Tuple[int, str]] = []
        current_tokens = 0
        
        # Get indices sorted by similarity (descending)
        ranked_indices = np.argsort(similarities)[::-1]
        
        for idx in ranked_indices:
            if similarities[idx] <= 0:
                continue
                
            chunk = context_chunks[int(idx)]
            # Simple approximation for tokens (1 word ~ 1.3 tokens)
            chunk_tokens = len(chunk.split()) * 1.3
            
            if current_tokens + chunk_tokens <= self.max_tokens:
                selected.append((int(idx), chunk))
                current_tokens += int(chunk_tokens)
            else:
                break
        
        # 5. Restore original order to preserve narrative flow (Chronological context)
        selected.sort(key=lambda x: x[0])
        
        return "\n\n".join([chunk for _, chunk in selected])

# Singleton helper
slimmer = SemanticPromptSlimmer()
