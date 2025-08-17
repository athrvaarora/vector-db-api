"""
Flat (brute-force) vector index implementation.

Time Complexity:
- Add: O(1)
- Remove: O(n)
- Search: O(n*d) where n is number of vectors, d is dimension

Space Complexity: O(n*d)

Why chosen: Simple, exact results, good for small to medium datasets.
No approximation errors, easy to debug and understand.
"""
from typing import List, Tuple
from uuid import UUID

import numpy as np

from .base import VectorIndex


class FlatIndex(VectorIndex):
    """
    Flat index that performs exhaustive search over all vectors.
    
    Advantages:
    - Exact results (no approximation)
    - Simple implementation
    - Memory efficient for small datasets
    
    Disadvantages:
    - Linear search time O(n)
    - Doesn't scale well for large datasets
    """
    
    def __init__(self, dimension: int) -> None:
        super().__init__(dimension)
        self._id_to_index = {}
    
    def add_vector(self, vector: List[float], chunk_id: UUID) -> None:
        """Add a vector to the flat index."""
        validated_vector = self._validate_vector(vector)
        
        # If ID already exists, update it
        if chunk_id in self._id_to_index:
            index = self._id_to_index[chunk_id]
            self._vectors[index] = validated_vector
        else:
            # Add new vector
            self._vectors.append(validated_vector)
            self._ids.append(chunk_id)
            self._id_to_index[chunk_id] = len(self._vectors) - 1
    
    def remove_vector(self, chunk_id: UUID) -> bool:
        """Remove a vector from the flat index."""
        if chunk_id not in self._id_to_index:
            return False
        
        index = self._id_to_index[chunk_id]
        
        # Remove from all lists
        self._vectors.pop(index)
        self._ids.pop(index)
        del self._id_to_index[chunk_id]
        
        # Update indices for remaining items
        for i in range(index, len(self._ids)):
            self._id_to_index[self._ids[i]] = i
        
        return True
    
    def search(self, query_vector: List[float], k: int) -> List[Tuple[UUID, float]]:
        """
        Perform exhaustive k-NN search using cosine similarity.
        
        Returns results sorted by similarity (highest first).
        """
        if not self._vectors:
            return []
        
        query_array = self._validate_vector(query_vector)
        similarities = []
        
        # Calculate similarity with all vectors
        for i, vector in enumerate(self._vectors):
            similarity = self._cosine_similarity(query_array, vector)
            similarities.append((self._ids[i], similarity))
        
        # Sort by similarity (descending) and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def get_stats(self) -> dict:
        """Get flat index statistics."""
        return {
            "type": "flat",
            "size": self.size,
            "dimension": self.dimension,
            "memory_usage_bytes": self._estimate_memory_usage(),
            "search_complexity": "O(n*d)",
            "add_complexity": "O(1)",
            "remove_complexity": "O(n)"
        }
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes."""
        if not self._vectors:
            return 0
        
        # Vector storage (float32)
        vector_bytes = len(self._vectors) * self.dimension * 4
        
        # ID storage (UUID overhead)
        id_bytes = len(self._ids) * 16
        
        # Index mapping overhead
        mapping_bytes = len(self._id_to_index) * 24  # rough estimate
        
        return vector_bytes + id_bytes + mapping_bytes