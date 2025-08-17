"""
Test data for indexing endpoint tests.
Contains predefined test data for vector indexing operations.
"""

from typing import Dict, Any
from datetime import datetime
import uuid

# Base URL for API endpoints
BASE_URL = "http://localhost:8000/api/v1"

# Test scenarios for indexing
TEST_SCENARIOS = {
    "index_library_flat": {
        "description": "Index library with Flat algorithm",
        "payload": {"algorithm": "flat"},
        "expected_status": 200,
        "validation_fields": ["message", "algorithm", "indexed_chunks"]
    },
    "index_library_lsh": {
        "description": "Index library with LSH algorithm", 
        "payload": {"algorithm": "lsh"},
        "expected_status": 200,
        "validation_fields": ["message", "algorithm", "indexed_chunks"]
    },
    "index_library_hierarchical": {
        "description": "Index library with Hierarchical algorithm",
        "payload": {"algorithm": "hierarchical"},
        "expected_status": 200,
        "validation_fields": ["message", "algorithm", "indexed_chunks"]
    },
    "index_library_default": {
        "description": "Index library with default algorithm",
        "payload": {},
        "expected_status": 200,
        "validation_fields": ["message", "algorithm", "indexed_chunks"]
    }
}

# Error test cases for indexing
ERROR_TEST_CASES = {
    "invalid_library_id": {
        "library_id": "invalid-uuid",
        "payload": {"algorithm": "flat"},
        "expected_status": 422,
        "description": "Invalid library UUID format"
    },
    "nonexistent_library": {
        "library_id": "550e8400-e29b-41d4-a716-446655440999",
        "payload": {"algorithm": "flat"},
        "expected_status": 404,
        "description": "Library not found"
    },
    "invalid_algorithm": {
        "payload": {"algorithm": "invalid_algorithm"},
        "expected_status": 422,
        "description": "Invalid algorithm type"
    },
    "empty_library": {
        "payload": {"algorithm": "flat"},
        "expected_status": 400,
        "description": "Library with no chunks to index"
    }
}

# Expected response schema for indexing
EXPECTED_INDEX_RESPONSE_SCHEMA = {
    "message": str
}

# Helper functions for test dependencies
def get_test_library_payload():
    """Get a test library payload for creating dependencies."""
    return {
        "metadata": {
            "name": "Test Library for Indexing",
            "description": "A test library for vector indexing tests",
            "tags": ["test", "indexing"],
            "is_public": True,
            "owner": "test_user"
        }
    }

def get_test_document_payload(library_id: str):
    """Get a test document payload for creating dependencies."""
    return {
        "metadata": {
            "title": "Test Document for Indexing",
            "description": "A test document for indexing tests",
            "author": "Test Author",
            "tags": ["test", "indexing"],
            "category": "testing",
            "file_type": "text"
        },
        "library_id": library_id
    }

def get_test_chunk_payload(document_id: str):
    """Get a test chunk payload for creating dependencies."""
    return {
        "text": "This is a test chunk for indexing operations. It contains sample text to validate vector indexing functionality.",
        "embedding": [0.1] * 384,  # 384-dimensional embedding
        "metadata": {
            "source": "Test Document for Indexing",
            "author": "Test Author",
            "tags": ["test", "indexing"],
            "language": "en",
            "char_count": 118
        },
        "document_id": document_id
    }