"""Simplified confidence scorer – no external models."""
import numpy as np

class ConfidenceScorer:
    def __init__(self):
        self.model = None

    def load(self):
        pass  # No model to load

    def embed(self, texts):
        # Return dummy embeddings
        return np.random.rand(len(texts), 384)

    def score(self, ans1, ans2):
        # Dummy: just return a random score between 0.5 and 0.99
        import random
        return round(random.uniform(0.6, 0.98), 3)

    def confidence(self, responses):
        if not responses:
            return 0.0
        return round(random.uniform(0.6, 0.98), 3)

    def reflection_confidence(self, answer, query):
        return round(random.uniform(0.6, 0.98), 3)