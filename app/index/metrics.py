"""
Hierarchical Navigable Small World (HNSW-inspired) index implementation.

Time Complexity:
- Add: O(log n * d)
- Remove: O(log n + connections)
- Search: O(log n * d)

Space Complexity: O(n*d + n*connections)

Why chosen: Excellent search performance, scales well with dataset size,
good recall-efficiency tradeoff. Inspired by HNSW but simplified.
"""
import random
from typing import Dict, List, Set, Tuple
from uuid import UUID

import numpy as np

from .base import VectorIndex


class HierarchicalIndex(VectorIndex):
    """
    Hierarchical index inspired by HNSW (Hierarchical Navigable Small World).
    
    Uses a multi-layer graph structure where higher layers have fewer nodes
    but longer connections, enabling logarithmic search time.
    
    Advantages:
    - Logarithmic search time
    - Good recall and precision
    - Scales well with dataset size
    
    Disadvantages:
    - Complex implementation
    - Memory overhead for graph structure
    - Requires parameter tuning
    """
    
    def __init__(self, dimension: int, max_connections: int = 16, max_layers: int = 5) -> None:
        super().__init__(dimension)
        self.max_connections = max_connections
        self.max_layers = max_layers
        self.level_multiplier = 1 / np.log(2.0)
        
        # Graph structure: layer -> node_id -> set of connected node_ids
        self._graph: List[Dict[UUID, Set[UUID]]] = [
            {} for _ in range(max_layers)
        ]
        
        # Store vectors and their layers
        self._vector_store: Dict[UUID, np.ndarray] = {}
        self._node_layers: Dict[UUID, int] = {}
        
        # Entry point for search
        self._entry_point: UUID = None
    
    def add_vector(self, vector: List[float], chunk_id: UUID) -> None:
        """Add a vector to the hierarchical index."""
        validated_vector = self._validate_vector(vector)
        
        # Remove existing vector if present
        if chunk_id in self._vector_store:
            self.remove_vector(chunk_id)
        
        # Store vector
        self._vector_store[chunk_id] = validated_vector
        
        # Determine layer for this node (higher probability for lower layers)
        layer = min(int(-np.log(random.random()) * self.level_multiplier), self.max_layers - 1)
        self._node_layers[chunk_id] = layer
        
        # If this is the first node or highest layer node, make it entry point
        if (self._entry_point is None or 
            layer > self._node_layers.get(self._entry_point, 0)):
            self._entry_point = chunk_id
        
        # Add to all layers from 0 to node's layer
        for lev in range(layer + 1):
            self._graph[lev][chunk_id] = set()
            
            # Find neighbors and create connections
            neighbors = self._find_neighbors(validated_vector, lev, chunk_id)
            
            for neighbor_id in neighbors:
                # Add bidirectional connection
                self._graph[lev][chunk_id].add(neighbor_id)
                self._graph[lev][neighbor_id].add(chunk_id)
                
                # Prune connections if exceeded max
                self._prune_connections(neighbor_id, lev)
            
            self._prune_connections(chunk_id, lev)
    
    def remove_vector(self, chunk_id: UUID) -> bool:
        """Remove a vector from the hierarchical index."""
        if chunk_id not in self._vector_store:
            return False
        
        layer = self._node_layers[chunk_id]
        
        # Remove from all layers
        for lev in range(layer + 1):
            if chunk_id in self._graph[lev]:
                # Remove connections to this node
                for neighbor_id in self._graph[lev][chunk_id]:
                    self._graph[lev][neighbor_id].discard(chunk_id)
                
                # Remove the node itself
                del self._graph[lev][chunk_id]
        
        # Clean up storage
        del self._vector_store[chunk_id]
        del self._node_layers[chunk_id]
        
        # Update entry point if necessary
        if self._entry_point == chunk_id:
            self._entry_point = self._find_new_entry_point()
        
        return True
    
    def search(self, query_vector: List[float], k: int) -> List[Tuple[UUID, float]]:
        """
        Perform hierarchical search from top layer to bottom.
        
        Uses greedy search at each layer, getting closer to query at each step.
        """
        if not self._vector_store or self._entry_point is None:
            return []
        
        query_array = self._validate_vector(query_vector)
        current_best = {self._entry_point}
        
        # Search from top layer to layer 1
        for lev in range(self.max_layers - 1, 0, -1):
            if lev <= self._node_layers.get(self._entry_point, 0):
                current_best = self._search_layer(query_array, current_best, 1, lev)
        
        # Search layer 0 with desired k
        candidates = self._search_layer(query_array, current_best, k, 0)
        
        # Calculate final similarities and sort
        similarities = []
        for chunk_id in candidates:
            if chunk_id in self._vector_store:
                vector = self._vector_store[chunk_id]
                similarity = self._cosine_similarity(query_array, vector)
                similarities.append((chunk_id, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def get_stats(self) -> dict:
        """Get hierarchical index statistics."""
        layer_stats = []
        for lev in range(self.max_layers):
            nodes = len(self._graph[lev])
            connections = sum(len(neighbors) for neighbors in self._graph[lev].values())
            layer_stats.append({"nodes": nodes, "connections": connections})
        
        return {
            "type": "hierarchical",
            "size": len(self._vector_store),
            "dimension": self.dimension,
            "max_layers": self.max_layers,
            "max_connections": self.max_connections,
            "layer_stats": layer_stats,
            "entry_point": str(self._entry_point) if self._entry_point else None,
            "memory_usage_bytes": self._estimate_memory_usage(),
            "search_complexity": "O(log n * d)",
            "add_complexity": "O(log n * d)",
            "remove_complexity": "O(log n + connections)"
        }
    
    def _find_neighbors(self, vector: np.ndarray, layer: int, exclude_id: UUID) -> List[UUID]:
        """Find best neighbors for a vector at a given layer."""
        if not self._graph[layer]:
            return []
        
        # Calculate similarities to all nodes in layer
        candidates = []
        for node_id in self._graph[layer]:
            if node_id != exclude_id and node_id in self._vector_store:
                node_vector = self._vector_store[node_id]
                similarity = self._cosine_similarity(vector, node_vector)
                candidates.append((node_id, similarity))
        
        # Sort by similarity and return top candidates
        candidates.sort(key=lambda x: x[1], reverse=True)
        max_neighbors = min(self.max_connections, len(candidates))
        return [node_id for node_id, _ in candidates[:max_neighbors]]
    
    def _search_layer(self, query: np.ndarray, entry_points: Set[UUID], 
                     num_closest: int, layer: int) -> Set[UUID]:
        """Search a single layer for closest nodes."""
        visited = set()
        candidates = []
        dynamic_candidates = []
        
        # Initialize with entry points
        for point in entry_points:
            if point in self._graph[layer] and point in self._vector_store:
                similarity = self._cosine_similarity(query, self._vector_store[point])
                candidates.append((similarity, point))
                dynamic_candidates.append((similarity, point))
                visited.add(point)
        
        candidates.sort(reverse=True)
        dynamic_candidates.sort()
        
        while dynamic_candidates:
            current_dist, current = dynamic_candidates.pop(0)
            
            # If current distance is worse than k-th best, stop
            if len(candidates) >= num_closest and current_dist < candidates[num_closest - 1][0]:
                break
            
            # Check neighbors
            if current in self._graph[layer]:
                for neighbor in self._graph[layer][current]:
                    if neighbor not in visited and neighbor in self._vector_store:
                        visited.add(neighbor)
                        similarity = self._cosine_similarity(query, self._vector_store[neighbor])
                        
                        if (len(candidates) < num_closest or 
                            similarity > candidates[num_closest - 1][0]):
                            candidates.append((similarity, neighbor))
                            dynamic_candidates.append((similarity, neighbor))
                            
                            candidates.sort(reverse=True)
                            dynamic_candidates.sort()
                            
                            if len(candidates) > num_closest:
                                candidates = candidates[:num_closest]
        
        return {point for _, point in candidates}
    
    def _prune_connections(self, node_id: UUID, layer: int) -> None:
        """Prune connections if they exceed maximum."""
        if node_id not in self._graph[layer]:
            return
        
        connections = self._graph[layer][node_id]
        if len(connections) <= self.max_connections:
            return
        
        # Calculate similarities and keep best connections
        if node_id not in self._vector_store:
            return
        
        node_vector = self._vector_store[node_id]
        similarities = []
        
        for neighbor_id in connections:
            if neighbor_id in self._vector_store:
                neighbor_vector = self._vector_store[neighbor_id]
                similarity = self._cosine_similarity(node_vector, neighbor_vector)
                similarities.append((similarity, neighbor_id))
        
        # Sort by similarity and keep top connections
        similarities.sort(reverse=True)
        new_connections = {neighbor_id for _, neighbor_id in similarities[:self.max_connections]}
        
        # Remove pruned connections
        for neighbor_id in connections - new_connections:
            self._graph[layer][neighbor_id].discard(node_id)
        
        self._graph[layer][node_id] = new_connections
    
    def _find_new_entry_point(self) -> UUID:
        """Find new entry point after current one is removed."""
        best_layer = -1
        best_node = None
        
        for node_id, layer in self._node_layers.items():
            if layer > best_layer:
                best_layer = layer
                best_node = node_id
        
        return best_node
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes."""
        # Vector storage
        vector_bytes = len(self._vector_store) * self.dimension * 4
        
        # Graph structure
        graph_bytes = 0
        for layer in self._graph:
            for connections in layer.values():
                graph_bytes += len(connections) * 16  # UUID storage
        
        # Metadata
        metadata_bytes = len(self._node_layers) * 20  # rough estimate
        
        return vector_bytes + graph_bytes + metadata_bytes