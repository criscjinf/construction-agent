"""Vector similarity calculation utilities."""

import math


class VectorSimilarity:
    """Utilities for calculating vector similarities."""

    @staticmethod
    def cosine(vec1: list[float], vec2: list[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score between 0 and 1

        Raises:
            ValueError: If vectors have different dimensions
        """
        if len(vec1) != len(vec2):
            raise ValueError(f"Vector dimensions don't match: {len(vec1)} vs {len(vec2)}")

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)
