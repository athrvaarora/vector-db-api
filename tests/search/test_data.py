"""
Test data for search endpoint tests.
Contains predefined test data for vector search operations.
"""

from typing import Dict, Any, List
from datetime import datetime
import uuid

# Base URL for API endpoints
BASE_URL = "http://localhost:8000/api/v1"

# Sample embedding for search queries (384 dimensions)
SAMPLE_SEARCH_EMBEDDING = [0.2] * 384

# Test scenarios for search
TEST_SCENARIOS = {
    "search_library_basic": {
        "description": "Basic search in library",
        "payload": {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 5
        },
        "expected_status": 200,
        "validation_fields": ["results", "total_results", "query_time"]
    },
    "search_library_with_threshold": {
        "description": "Search with similarity threshold",
        "payload": {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 10,
            "similarity_threshold": 0.7
        },
        "expected_status": 200,
        "validation_fields": ["results", "total_results", "query_time"]
    },
    "search_library_with_filters": {
        "description": "Search with metadata filters",
        "payload": {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 5,
            "metadata_filters": {
                "tags": ["test"],
                "language": "en"
            }
        },
        "expected_status": 200,
        "validation_fields": ["results", "total_results", "query_time"]
    },
    "search_library_large_k": {
        "description": "Search with large k value",
        "payload": {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 100
        },
        "expected_status": 200,
        "validation_fields": ["results", "total_results", "query_time"]
    }
}

# Error test cases for search
ERROR_TEST_CASES = {
    "invalid_library_id": {
        "library_id": "invalid-uuid",
        "payload": {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 5
        },
        "expected_status": 422,
        "description": "Invalid library UUID format"
    },
    "nonexistent_library": {
        "library_id": "550e8400-e29b-41d4-a716-446655440999",
        "payload": {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 5
        },
        "expected_status": 404,
        "description": "Library not found"
    },
    "missing_embedding": {
        "payload": {
            "k": 5
        },
        "expected_status": 422,
        "description": "Missing embedding in search query"
    },
    "empty_embedding": {
        "payload": {
            "embedding": [],
            "k": 5
        },
        "expected_status": 422,
        "description": "Empty embedding vector"
    },
    "invalid_k_value": {
        "payload": {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 0
        },
        "expected_status": 422,
        "description": "Invalid k value (must be > 0)"
    },
    "invalid_threshold": {
        "payload": {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 5,
            "similarity_threshold": 1.5
        },
        "expected_status": 422,
        "description": "Invalid similarity threshold (must be <= 1.0)"
    }
}

# Expected response schema for search (returns list directly)
EXPECTED_SEARCH_RESPONSE_SCHEMA = list

# Expected schema for individual search result
EXPECTED_SEARCH_RESULT_SCHEMA = {
    "chunk": dict,
    "similarity_score": (float, int),
    "document": dict
}

# Helper functions for test dependencies
def get_test_library_payload():
    """Get a test library payload for creating dependencies."""
    return {
        "metadata": {
            "name": "Test Library for Search",
            "description": "A test library for vector search tests",
            "tags": ["test", "search"],
            "is_public": True,
            "owner": "test_user"
        }
    }

def get_test_document_payload(library_id: str):
    """Get a test document payload for creating dependencies."""
    return {
        "metadata": {
            "title": "Test Document for Search",
            "description": "A test document for search tests",
            "author": "Test Author",
            "tags": ["test", "search"],
            "category": "testing",
            "file_type": "text"
        },
        "library_id": library_id
    }

def get_test_chunk_payload(document_id: str, text_suffix: str = ""):
    """Get a test chunk payload for creating dependencies."""
    return {
        "text": f"This is a test chunk for search operations{text_suffix}. It contains sample content for semantic similarity testing.",
        "embedding": [0.1 + (len(text_suffix) * 0.01)] * 384,  # Slightly different embeddings
        "metadata": {
            "source": "Test Document for Search",
            "author": "Test Author",
            "tags": ["test", "search"],
            "language": "en",
            "char_count": 120 + len(text_suffix)
        },
        "document_id": document_id
    }