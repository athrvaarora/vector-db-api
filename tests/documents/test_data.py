"""
Test data for document endpoint tests.
Contains predefined test data with expected responses for consistent testing.
"""

from typing import Dict, Any
from datetime import datetime, timezone
import uuid

# Base URL for API endpoints
BASE_URL = "http://localhost:8000/api/v1"

# Test document data
TEST_DOCUMENTS = {
    "document_1": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "metadata": {
            "title": "Introduction to Machine Learning",
            "description": "A comprehensive guide to machine learning fundamentals",
            "author": "Dr. Jane Smith",
            "tags": ["machine-learning", "ai", "tutorial"],
            "category": "education",
            "file_type": "text"
        },
        "library_id": "550e8400-e29b-41d4-a716-446655440100"
    },
    "document_2": {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "metadata": {
            "title": "Python Programming Best Practices",
            "description": "Guidelines for writing clean and efficient Python code",
            "author": "John Doe",
            "tags": ["python", "programming", "best-practices"],
            "category": "technical",
            "file_type": "text"
        },
        "library_id": "550e8400-e29b-41d4-a716-446655440100"
    }
}

# Create payloads for POST requests
CREATE_DOCUMENT_PAYLOAD = {
    "metadata": {
        "title": "Test Document",
        "description": "A test document for API testing",
        "author": "Test Author",
        "tags": ["test", "api", "document"],
        "category": "testing",
        "file_type": "text"
    },
    "library_id": "550e8400-e29b-41d4-a716-446655440100"
}

UPDATE_DOCUMENT_PAYLOAD = {
    "metadata": {
        "title": "Updated Test Document",
        "description": "An updated test document for API testing",
        "author": "Updated Test Author",
        "tags": ["test", "api", "document", "updated"],
        "category": "testing",
        "file_type": "text"
    }
}

# Expected response structure for validation
EXPECTED_DOCUMENT_SCHEMA = {
    "id": str,
    "metadata": {
        "title": str,
        "description": (str, type(None)),
        "created_at": str,
        "updated_at": str,
        "author": (str, type(None)),
        "tags": list,
        "category": (str, type(None)),
        "file_type": str
    },
    "library_id": str,
    "chunk_ids": list
}

# Test scenarios
TEST_SCENARIOS = {
    "create_document": {
        "description": "Create a new document with valid data",
        "payload": CREATE_DOCUMENT_PAYLOAD,
        "expected_status": 201,
        "validation_fields": ["id", "metadata", "library_id", "chunk_ids"]
    },
    "list_documents": {
        "description": "Retrieve all documents",
        "expected_status": 200,
        "expected_min_count": 0
    },
    "list_documents_by_library": {
        "description": "Retrieve documents by library ID",
        "expected_status": 200,
        "expected_min_count": 0
    },
    "get_document": {
        "description": "Retrieve a specific document by ID",
        "expected_status": 200,
        "validation_fields": ["id", "metadata", "library_id", "chunk_ids"]
    },
    "update_document": {
        "description": "Update an existing document",
        "payload": UPDATE_DOCUMENT_PAYLOAD,
        "expected_status": 200,
        "validation_fields": ["id", "metadata", "library_id", "chunk_ids"]
    },
    "delete_document": {
        "description": "Delete an existing document",
        "expected_status": 204
    }
}

# Error test cases
ERROR_TEST_CASES = {
    "invalid_document_id": {
        "document_id": "invalid-uuid",
        "expected_status": 422,
        "description": "Invalid UUID format"
    },
    "nonexistent_document": {
        "document_id": "550e8400-e29b-41d4-a716-446655440999",
        "expected_status": 404,
        "description": "Document not found"
    },
    "invalid_library_id": {
        "library_id": "invalid-uuid",
        "expected_status": 422,
        "description": "Invalid library UUID format"
    },
    "nonexistent_library": {
        "library_id": "550e8400-e29b-41d4-a716-446655440999",
        "expected_status": 404,
        "description": "Library not found"
    },
    "missing_required_fields": {
        "payload": {"metadata": {"title": ""}},
        "expected_status": 422,
        "description": "Missing required fields"
    }
}

# Helper function to create a test library for document tests
def get_test_library_payload():
    """Get a test library payload for creating dependencies."""
    return {
        "metadata": {
            "name": "Test Library for Documents",
            "description": "A test library to hold documents for testing",
            "tags": ["test", "documents"],
            "is_public": True,
            "owner": "test_user"
        }
    }