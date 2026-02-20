import os
from typing import List, Tuple
from models import Rule

# Try importing dependencies, handle missing libs gracefully
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False
    print("Warning: sentence-transformers not found. Retrieval disabled.")


class VectorStore:
    """
    Vector retrieval system with cosine similarity.
    Implements CRAG-style similarity validation.
    """

    def __init__(self):
        self.rules: List[Rule] = []
        self.rule_embeddings = None
        self.model = None

        if VECTOR_SEARCH_AVAILABLE:
            try:
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                print(f"Error loading embedding model: {e}")
                self.model = None

    # -----------------------------------
    # Index Initialization
    # -----------------------------------

    def init_index(self, rules: List[Rule]):
        """
        Precompute normalized embeddings for rule descriptions.
        """

        if not VECTOR_SEARCH_AVAILABLE or not self.model:
            return

        self.rules = rules

        descriptions = [
            rule.human_description for rule in rules
            if rule.human_description
        ]

        if not descriptions:
            self.rule_embeddings = None
            return

        embeddings = self.model.encode(
            descriptions,
            normalize_embeddings=True
        )

        self.rule_embeddings = np.array(embeddings)

    # -----------------------------------
    # Search with CRAG Threshold
    # -----------------------------------

    def search(
        self,
        query: str,
        k: int = 3,
        similarity_threshold: float = 0.60
    ) -> Tuple[List[str], float]:
        """
        Returns:
        - relevant rule descriptions
        - maximum cosine similarity score
        """

        if (
            not VECTOR_SEARCH_AVAILABLE
            or not self.model
            or self.rule_embeddings is None
            or len(self.rule_embeddings) == 0
        ):
            return [], 0.0

        # Encode query
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )

        # Cosine similarity via dot product
        similarities = (
            self.rule_embeddings @ query_embedding.T
        ).flatten()

        # Get top-k indices
        top_indices = similarities.argsort()[-k:][::-1]

        max_similarity = float(similarities[top_indices[0]])

        results = []

        if max_similarity >= similarity_threshold:
            for idx in top_indices:
                if idx < len(self.rules):
                    results.append(self.rules[idx].human_description)

        return results, max_similarity


# Singleton instance
vector_store = VectorStore()