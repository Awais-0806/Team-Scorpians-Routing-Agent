import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from app.config import get_settings
from app.logger import log

settings = get_settings()


class ConfidenceScorer:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        log.info(f"ConfidenceScorer initialized with model on {self.device}")

    def load(self):
        """Load the embedding model (called at startup)."""
        self.model = SentenceTransformer(settings.embedding_model)
        log.info(f"Embedding model {settings.embedding_model} loaded")

    def embed(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )

    def confidence(self, responses: list[str]) -> float:
        """
        Calculate confidence score based on semantic similarity between responses.
        Higher similarity = higher confidence.
        """
        if len(responses) < 2:
            return 1.0

        embeddings = self.embed(responses)
        n = len(embeddings)
        sims = []

        for i in range(n):
            for j in range(i + 1, n):
                dot = np.dot(embeddings[i], embeddings[j])
                norm = np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                sims.append(dot / (norm + 1e-8))

        return float(np.mean(sims))

    def reflection_confidence(self, answer: str, query: str) -> float:
        """
        Calculate confidence using reflection (asking model to rate its own answer).
        Returns a float between 0 and 1.
        """
        # Simple fallback: use embedding similarity between query and answer
        query_emb = self.embed([query])[0]
        answer_emb = self.embed([answer])[0]
        dot = np.dot(query_emb, answer_emb)
        norm = np.linalg.norm(query_emb) * np.linalg.norm(answer_emb)
        return float(dot / (norm + 1e-8))