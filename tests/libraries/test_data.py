"""
Test data for library endpoint tests.
Contains predefined test data with expected responses for consistent testing.
"""

from typing import Dict, Any
from datetime import datetime, timezone
import uuid

# Base URL for API endpoints
BASE_URL = "http://localhost:8000/api/v1"

# Test library data
TEST_LIBRARIES = {
    "library_1": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "metadata": {
            "name": "Test Tech Library",
            "description": "A comprehensive technology documentation library for testing",
            "tags": ["technology", "documentation", "testing"],
            "is_public": True,
            "owner": "test_user"
        }
    },
    "library_2": {
        "id": "550e8400-e29b-41d4-a716-446655440002", 
        "metadata": {
            "name": "Private Research Library",
            "description": "Private research collection for internal use",
            "tags": ["research", "private", "internal"],
            "is_public": False,
            "owner": "researcher"
        }
    },
    "library_3": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "metadata": {
            "name": "Science Knowledge Base",
            "description": "Scientific articles and research papers",
            "tags": ["science", "research", "articles"],
            "is_public": True,
            "owner": "scientist"
        }
    }
}

# Create payloads for POST requests
CREATE_LIBRARY_PAYLOAD = {
    "metadata": {
        "name": "Test Tech Library",
        "description": "A comprehensive technology documentation library for testing",
        "tags": ["technology", "documentation", "testing"],
        "is_public": True,
        "owner": "test_user"
    }
}

UPDATE_LIBRARY_PAYLOAD = {
    "metadata": {
        "name": "Updated Tech Library",
        "description": "An updated comprehensive technology documentation library",
        "tags": ["technology", "documentation", "testing", "updated"],
        "is_public": False,
        "owner": "test_user"
    }
}

# Expected response structure for validation
EXPECTED_LIBRARY_SCHEMA = {
    "id": str,
    "metadata": {
        "name": str,
        "description": (str, type(None)),
        "created_at": str,
        "updated_at": str,
        "owner": (str, type(None)),
        "tags": list,
        "is_public": bool
    },
    "document_ids": list,
    "is_indexed": bool
}

EXPECTED_LIBRARY_STATS_SCHEMA = {
    "total_documents": int,
    "total_chunks": int,
    "embedding_dimension": (int, type(None)),
    "index_type": (str, type(None)),
    "last_indexed": (str, type(None))
}

# Test scenarios
TEST_SCENARIOS = {
    "create_library": {
        "description": "Create a new library with valid data",
        "payload": CREATE_LIBRARY_PAYLOAD,
        "expected_status": 201,
        "validation_fields": ["id", "metadata", "document_ids", "is_indexed"]
    },
    "list_libraries": {
        "description": "Retrieve all libraries",
        "expected_status": 200,
        "expected_min_count": 0
    },
    "get_library": {
        "description": "Retrieve a specific library by ID",
        "expected_status": 200,
        "validation_fields": ["id", "metadata", "document_ids", "is_indexed"]
    },
    "update_library": {
        "description": "Update an existing library",
        "payload": UPDATE_LIBRARY_PAYLOAD,
        "expected_status": 200,
        "validation_fields": ["id", "metadata", "document_ids", "is_indexed"]
    },
    "delete_library": {
        "description": "Delete an existing library",
        "expected_status": 204
    },
    "get_library_stats": {
        "description": "Get statistics for a library",
        "expected_status": 200,
        "validation_fields": ["total_documents", "total_chunks", "embedding_dimension", "index_type", "last_indexed"]
    }
}

# Error test cases
ERROR_TEST_CASES = {
    "invalid_library_id": {
        "library_id": "invalid-uuid",
        "expected_status": 422,
        "description": "Invalid UUID format"
    },
    "nonexistent_library": {
        "library_id": "550e8400-e29b-41d4-a716-446655440999",
        "expected_status": 404,
        "description": "Library not found"
    },
    "missing_required_fields": {
        "payload": {"metadata": {"name": ""}},
        "expected_status": 422,
        "description": "Missing required fields"
    }
}