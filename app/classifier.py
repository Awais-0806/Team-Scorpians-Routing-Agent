"""Lightweight query classifier using sentence embeddings."""
import numpy as np
from app.confidence import ConfidenceScorer
from app.models import QueryCategory

CATEGORY_DESCRIPTIONS = {
    QueryCategory.coding: "programming code debug function algorithm software development",
    QueryCategory.math: "mathematics calculation arithmetic algebra geometry calculus equation",
    QueryCategory.reasoning: "logical reasoning argument analysis problem-solving deduction",
    QueryCategory.creative: "story writing poetry creative art imagination narrative",
    QueryCategory.general: "general knowledge question answer information trivia",
}


class QueryClassifier:
    def __init__(self, scorer: ConfidenceScorer):
        self.scorer = scorer
        self.category_embeddings = {}
        self._precompute()

    def _precompute(self):
        for cat, desc in CATEGORY_DESCRIPTIONS.items():
            self.category_embeddings[cat] = self.scorer.embed([desc])[0]

    def classify(self, query: str) -> QueryCategory:
        query_emb = self.scorer.embed([query])[0]
        best_cat = QueryCategory.general
        best_sim = -1.0
        for cat, emb in self.category_embeddings.items():
            sim = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb) + 1e-8)
            if sim > best_sim:
                best_sim = sim
                best_cat = cat
        return best_cat