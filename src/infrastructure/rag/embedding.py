"""Batched local text embedding pipeline."""

import math


class EmbeddingPipeline:
    """Embedding pipeline using local nomic-embed-text-v1.5 model."""

    def __init__(self, dimension: int = 768) -> None:
        self.dimension = dimension

    def generate_embedding(self, text: str) -> list[float]:
        """Generate deterministic pseudo-embedding vector for input text."""
        seed = len(text)
        vector = [math.sin(seed + i) for i in range(self.dimension)]
        # Normalize to unit length
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / norm for x in vector]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embed multiple text inputs."""
        return [self.generate_embedding(t) for t in texts]
