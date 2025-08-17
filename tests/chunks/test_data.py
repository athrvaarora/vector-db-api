"""
Test data for chunk endpoint tests.
Contains predefined test data with expected responses for consistent testing.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid

# Base URL for API endpoints
BASE_URL = "http://localhost:8000/api/v1"

# Sample embedding vector for testing (384 dimensions as commonly used)
SAMPLE_EMBEDDING = [0.1] * 384

# Test chunk data
TEST_CHUNKS = {
    "chunk_1": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "text": "Machine learning is a subset of artificial intelligence that focuses on the use of data and algorithms.",
        "embedding": SAMPLE_EMBEDDING,
        "metadata": {
            "source": "Introduction to ML",
            "author": "Dr. Jane Smith",
            "tags": ["machine-learning", "ai"],
            "language": "en",
            "char_count": 95
        },
        "document_id": "550e8400-e29b-41d4-a716-446655440100"
    },
    "chunk_2": {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "text": "Python is a high-level programming language known for its simplicity and readability.",
        "embedding": SAMPLE_EMBEDDING,
        "metadata": {
            "source": "Python Basics",
            "author": "John Doe",
            "tags": ["python", "programming"],
            "language": "en",
            "char_count": 85
        },
        "document_id": "550e8400-e29b-41d4-a716-446655440100"
    }
}

# Create payloads for POST requests
CREATE_CHUNK_PAYLOAD = {
    "text": "This is a test chunk for API testing purposes. It contains some sample text to validate the chunk creation functionality.",
    "embedding": SAMPLE_EMBEDDING,
    "metadata": {
        "source": "Test Document",
        "author": "Test Author",
        "tags": ["test", "api", "chunk"],
        "language": "en",
        "char_count": 127
    },
    "document_id": "550e8400-e29b-41d4-a716-446655440100"
}

UPDATE_CHUNK_PAYLOAD = {
    "text": "This is an updated test chunk for API testing purposes. It contains modified sample text to validate the chunk update functionality.",
    "embedding": [0.2] * 384,  # Updated embedding
    "metadata": {
        "source": "Updated Test Document",
        "author": "Updated Test Author",
        "tags": ["test", "api", "chunk", "updated"],
        "language": "en",
        "char_count": 142
    }
}

# Expected response structure for validation
EXPECTED_CHUNK_SCHEMA = {
    "id": str,
    "text": str,
    "embedding": list,
    "metadata": {
        "source": str,
        "created_at": str,
        "updated_at": str,
        "author": (str, type(None)),
        "tags": list,
        "language": str,
        "char_count": int
    },
    "document_id": str
}

# Test scenarios
TEST_SCENARIOS = {
    "create_chunk": {
        "description": "Create a new chunk with valid data",
        "payload": CREATE_CHUNK_PAYLOAD,
        "expected_status": 201,
        "validation_fields": ["id", "text", "embedding", "metadata", "document_id"]
    },
    "list_chunks_by_document": {
        "description": "Retrieve chunks by document ID",
        "expected_status": 200,
        "expected_min_count": 0
    },
    "get_chunk": {
        "description": "Retrieve a specific chunk by ID",
        "expected_status": 200,
        "validation_fields": ["id", "text", "embedding", "metadata", "document_id"]
    },
    "update_chunk": {
        "description": "Update an existing chunk",
        "payload": UPDATE_CHUNK_PAYLOAD,
        "expected_status": 200,
        "validation_fields": ["id", "text", "embedding", "metadata", "document_id"]
    },
    "delete_chunk": {
        "description": "Delete an existing chunk",
        "expected_status": 204
    }
}

# Error test cases
ERROR_TEST_CASES = {
    "invalid_chunk_id": {
        "chunk_id": "invalid-uuid",
        "expected_status": 422,
        "description": "Invalid UUID format"
    },
    "nonexistent_chunk": {
        "chunk_id": "550e8400-e29b-41d4-a716-446655440999",
        "expected_status": 404,
        "description": "Chunk not found"
    },
    "invalid_document_id": {
        "document_id": "invalid-uuid",
        "expected_status": 422,
        "description": "Invalid document UUID format"
    },
    "nonexistent_document": {
        "document_id": "550e8400-e29b-41d4-a716-446655440999",
        "expected_status": 404,
        "description": "Document not found"
    },
    "missing_required_fields": {
        "payload": {"text": ""},
        "expected_status": 422,
        "description": "Missing required fields"
    },
    "invalid_embedding": {
        "payload": {
            "text": "Test text",
            "embedding": [],  # Empty embedding
            "metadata": {
                "source": "test",
                "language": "en",
                "char_count": 9
            },
            "document_id": "550e8400-e29b-41d4-a716-446655440100"
        },
        "expected_status": 422,
        "description": "Invalid embedding (empty)"
    }
}

# Helper functions to create test dependencies
def get_test_library_payload():
    """Get a test library payload for creating dependencies."""
    return {
        "metadata": {
            "name": "Test Library for Chunks",
            "description": "A test library to hold documents and chunks for testing",
            "tags": ["test", "chunks"],
            "is_public": True,
            "owner": "test_user"
        }
    }

def get_test_document_payload(library_id: str):
    """Get a test document payload for creating dependencies."""
    return {
        "metadata": {
            "title": "Test Document for Chunks",
            "description": "A test document to hold chunks for testing",
            "author": "Test Author",
            "tags": ["test", "chunks"],
            "category": "testing",
            "file_type": "text"
        },
        "library_id": library_id
    }