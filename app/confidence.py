# D:\AMD V2\app\confidence.py
import numpy as np
from sentence_transformers import SentenceTransformer, util
from app.config import get_settings

settings = get_settings()

class ConfidenceScorer:
    def __init__(self):
        self.model = None

    def load(self):
        if self.model is None:
            self.model = SentenceTransformer(settings.embedding_model)

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return embeddings for a list of texts."""
        if self.model is None:
            self.load()
        return self.model.encode(texts, convert_to_numpy=True)

    def score(self, answer1: str, answer2: str) -> float:
        """Semantic similarity confidence score between two answers."""
        if not answer1 or not answer2:
            return 0.0
        emb1 = self.model.encode(answer1, convert_to_tensor=True)
        emb2 = self.model.encode(answer2, convert_to_tensor=True)
        cos_sim = util.cos_sim(emb1, emb2).item()
        # Scale cosine similarity to 0-1 range (cos_sim usually 0.5-1.0)
        score = max(0.0, min(1.0, (cos_sim - 0.5) * 2.0))
        return round(score, 4)

    def confidence(self, responses: list[str]) -> float:
        """Compute confidence from multiple responses (self-consistency)."""
        if len(responses) < 2:
            return 0.0
        scores = []
        for i in range(len(responses)):
            for j in range(i+1, len(responses)):
                scores.append(self.score(responses[i], responses[j]))
        return round(sum(scores) / len(scores), 4) if scores else 0.0

    def reflection_confidence(self, answer: str, query: str) -> float:
        """Optional reflection score (dummy implementation)."""
        # Simple fallback based on answer length
        return 0.9 if len(answer) > 10 else 0.7