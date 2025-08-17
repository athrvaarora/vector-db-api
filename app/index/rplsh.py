"""
Random Projection Locality Sensitive Hashing (RP-LSH) index implementation.

Time Complexity:
- Add: O(h*d) where h is number of hash functions, d is dimension
- Remove: O(h + bucket_size)
- Search: O(h*d + bucket_size)

Space Complexity: O(n*d + h*d) where n is number of vectors

Why chosen: Good for high-dimensional data, sub-linear search time,
approximate but fast results. Works well with cosine similarity.
"""
import hashlib
from typing import Dict, List, Set, Tuple
from uuid import UUID

import numpy as np

from .base import VectorIndex


class RPLSHIndex(VectorIndex):
    """
    Random Projection LSH index for approximate nearest neighbor search.
    
    Uses random hyperplanes to hash vectors into buckets. Vectors in the
    same bucket are likely to be similar (with high probability).
    
    Advantages:
    - Sub-linear search time
    - Works well with high-dimensional data
    - Memory efficient for large datasets
    
    Disadvantages:
    - Approximate results
    - Requires tuning of hash functions and projection bits
    """
    
    def __init__(self, dimension: int, num_hashes: int = 16, num_bits: int = 8) -> None:
        super().__init__(dimension)
        self.num_hashes = num_hashes
        self.num_bits = num_bits
        
        # Generate random projection matrices
        self._projections = []
        for _ in range(num_hashes):
            # Random hyperplanes for projection
            projection = np.random.randn(num_bits, dimension).astype(np.float32)
            # Normalize to unit vectors
            projection = projection / np.linalg.norm(projection, axis=1, keepdims=True)
            self._projections.append(projection)
        
        # Hash tables: hash -> set of chunk_ids
        self._hash_tables: List[Dict[str, Set[UUID]]] = [
            {} for _ in range(num_hashes)
        ]
        
        # Store actual vectors for final ranking
        self._vector_store: Dict[UUID, np.ndarray] = {}
    
    def add_vector(self, vector: List[float], chunk_id: UUID) -> None:
        """Add a vector to the LSH index."""
        validated_vector = self._validate_vector(vector)
        
        # Remove old vector if exists
        if chunk_id in self._vector_store:
            self.remove_vector(chunk_id)
        
        # Store the actual vector
        self._vector_store[chunk_id] = validated_vector
        
        # Hash vector and add to buckets
        for i, projection in enumerate(self._projections):
            hash_value = self._hash_vector(validated_vector, projection)
            
            if hash_value not in self._hash_tables[i]:
                self._hash_tables[i][hash_value] = set()
            
            self._hash_tables[i][hash_value].add(chunk_id)
    
    def remove_vector(self, chunk_id: UUID) -> bool:
        """Remove a vector from the LSH index."""
        if chunk_id not in self._vector_store:
            return False
        
        vector = self._vector_store[chunk_id]
        
        # Remove from all hash tables
        for i, projection in enumerate(self._projections):
            hash_value = self._hash_vector(vector, projection)
            
            if hash_value in self._hash_tables[i]:
                self._hash_tables[i][hash_value].discard(chunk_id)
                
                # Clean up empty buckets
                if not self._hash_tables[i][hash_value]:
                    del self._hash_tables[i][hash_value]
        
        # Remove from vector store
        del self._vector_store[chunk_id]
        return True
    
    def search(self, query_vector: List[float], k: int) -> List[Tuple[UUID, float]]:
        """
        Perform approximate k-NN search using LSH.
        
        Returns candidates from hash buckets, then ranks by exact similarity.
        """
        if not self._vector_store:
            return []
        
        query_array = self._validate_vector(query_vector)
        candidates = set()
        
        # Collect candidates from all hash tables
        for i, projection in enumerate(self._projections):
            hash_value = self._hash_vector(query_array, projection)
            
            if hash_value in self._hash_tables[i]:
                candidates.update(self._hash_tables[i][hash_value])
        
        # If no candidates found, fall back to random sampling
        if not candidates:
            candidates = set(list(self._vector_store.keys())[:min(k*2, len(self._vector_store))])
        
        # Rank candidates by exact similarity
        similarities = []
        for chunk_id in candidates:
            vector = self._vector_store[chunk_id]
            similarity = self._cosine_similarity(query_array, vector)
            similarities.append((chunk_id, similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def get_stats(self) -> dict:
        """Get LSH index statistics."""
        total_buckets = sum(len(table) for table in self._hash_tables)
        avg_bucket_size = (
            sum(len(bucket) for table in self._hash_tables for bucket in table.values()) / 
            max(total_buckets, 1)
        )
        
        return {
            "type": "rp_lsh",
            "size": len(self._vector_store),
            "dimension": self.dimension,
            "num_hashes": self.num_hashes,
            "num_bits": self.num_bits,
            "total_buckets": total_buckets,
            "avg_bucket_size": avg_bucket_size,
            "memory_usage_bytes": self._estimate_memory_usage(),
            "search_complexity": "O(h*d + bucket_size)",
            "add_complexity": "O(h*d)",
            "remove_complexity": "O(h + bucket_size)"
        }
    
    def _hash_vector(self, vector: np.ndarray, projection: np.ndarray) -> str:
        """Hash a vector using random projection."""
        # Project vector onto random hyperplanes
        projected = np.dot(projection, vector)
        
        # Convert to binary hash
        binary_hash = (projected > 0).astype(int)
        
        # Convert binary to string for hashing
        hash_string = ''.join(map(str, binary_hash))
        
        # Use MD5 for consistent hashing
        return hashlib.md5(hash_string.encode()).hexdigest()[:8]
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes."""
        # Vector storage
        vector_bytes = len(self._vector_store) * self.dimension * 4
        
        # Projection matrices
        projection_bytes = self.num_hashes * self.num_bits * self.dimension * 4
        
        # Hash tables (rough estimate)
        hash_table_bytes = sum(
            len(table) * 50 + sum(len(bucket) * 16 for bucket in table.values())
            for table in self._hash_tables
        )
        
        return vector_bytes + projection_bytes + hash_table_bytes