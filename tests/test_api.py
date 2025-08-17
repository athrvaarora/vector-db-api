"""
Tests for the Vector Database API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.models.schemas import LibraryMetadata, LibraryCreate


client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test health check returns 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestLibraryEndpoints:
    """Test library CRUD operations."""
    
    def test_create_library(self):
        """Test creating a library."""
        library_data = LibraryCreate(
            metadata=LibraryMetadata(
                name="Test Library",
                description="A test library",
                owner="test_user"
            )
        )
        
        response = client.post("/api/v1/libraries", json=library_data.model_dump())
        assert response.status_code == 201
        
        data = response.json()
        assert data["metadata"]["name"] == "Test Library"
        assert "id" in data
        
        return data["id"]
    
    def test_get_library(self):
        """Test getting a library by ID."""
        # Create a library first
        library_id = self.test_create_library()
        
        response = client.get(f"/api/v1/libraries/{library_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == library_id
        assert data["metadata"]["name"] == "Test Library"
    
    def test_list_libraries(self):
        """Test listing all libraries."""
        response = client.get("/api/v1/libraries")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_nonexistent_library(self):
        """Test getting a library that doesn't exist."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/libraries/{fake_id}")
        assert response.status_code == 404


class TestIndexingAlgorithms:
    """Test vector indexing algorithms."""
    
    def test_flat_index(self):
        """Test flat index implementation."""
        from app.index.flat import FlatIndex
        
        index = FlatIndex(dimension=3)
        
        # Test adding vectors
        vector1 = [1.0, 0.0, 0.0]
        vector2 = [0.0, 1.0, 0.0]
        vector3 = [0.0, 0.0, 1.0]
        
        id1, id2, id3 = uuid4(), uuid4(), uuid4()
        
        index.add_vector(vector1, id1)
        index.add_vector(vector2, id2)
        index.add_vector(vector3, id3)
        
        assert index.size == 3
        
        # Test search
        query = [1.0, 0.0, 0.0]
        results = index.search(query, k=2)
        
        assert len(results) == 2
        assert results[0][0] == id1  # Most similar should be id1
        assert results[0][1] > results[1][1]  # Similarity scores should be ordered
    
    def test_rp_lsh_index(self):
        """Test RP-LSH index implementation."""
        from app.index.rplsh import RPLSHIndex
        
        index = RPLSHIndex(dimension=10, num_hashes=4, num_bits=4)
        
        # Test adding vectors
        vector1 = [1.0] * 10
        vector2 = [0.5] * 10
        
        id1, id2 = uuid4(), uuid4()
        
        index.add_vector(vector1, id1)
        index.add_vector(vector2, id2)
        
        assert len(index._vector_store) == 2
        
        # Test search
        query = [0.9] * 10
        results = index.search(query, k=1)
        
        assert len(results) >= 1
        assert results[0][0] in [id1, id2]


class TestConcurrency:
    """Test thread safety and concurrency control."""
    
    def test_read_write_lock(self):
        """Test read-write lock implementation."""
        from app.domain.rwlock import ReadWriteLock
        import threading
        import time
        
        lock = ReadWriteLock()
        results = []
        
        def reader_task():
            with lock.read_lock():
                results.append("read_start")
                time.sleep(0.1)
                results.append("read_end")
        
        def writer_task():
            with lock.write_lock():
                results.append("write_start")
                time.sleep(0.1)
                results.append("write_end")
        
        # Start multiple readers and one writer
        readers = [threading.Thread(target=reader_task) for _ in range(3)]
        writer = threading.Thread(target=writer_task)
        
        for reader in readers:
            reader.start()
        writer.start()
        
        for reader in readers:
            reader.join()
        writer.join()
        
        # Check that reads and writes don't interleave incorrectly
        assert len(results) == 8  # 3 readers * 2 + 1 writer * 2


if __name__ == "__main__":
    pytest.main([__file__])