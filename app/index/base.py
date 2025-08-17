"""
Base interface for vector indexes.
Following the Strategy pattern for pluggable indexing algorithms.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
from uuid import UUID

import numpy as np


class VectorIndex(ABC):
    """
    Abstract base class for vector indexing algorithms.
    
    Follows the Strategy pattern to allow different indexing implementations
    while maintaining a consistent interface.
    """
    
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self._vectors: List[np.ndarray] = []
        self._ids: List[UUID] = []
    
    @abstractmethod
    def add_vector(self, vector: List[float], chunk_id: UUID) -> None:
        """Add a vector to the index."""
        pass
    
    @abstractmethod
    def remove_vector(self, chunk_id: UUID) -> bool:
        """Remove a vector from the index. Returns True if found and removed."""
        pass
    
    @abstractmethod
    def search(self, query_vector: List[float], k: int) -> List[Tuple[UUID, float]]:
        """
        Search for k nearest neighbors.
        Returns list of (chunk_id, similarity_score) tuples.
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> dict:
        """Get index statistics and metadata."""
        pass
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _euclidean_distance(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate Euclidean distance between two vectors."""
        return np.linalg.norm(a - b)
    
    def _validate_vector(self, vector: List[float]) -> np.ndarray:
        """Validate and convert vector to numpy array."""
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension {len(vector)} doesn't match index dimension {self.dimension}")
        
        return np.array(vector, dtype=np.float32)
    
    @property
    def size(self) -> int:
        """Number of vectors in the index."""
        return len(self._vectors)