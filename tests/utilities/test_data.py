"""
Test data for utilities endpoint tests.
Contains predefined test data for utility function tests.
"""

from typing import Dict, Any
from datetime import datetime

# Base URL for API endpoints
BASE_URL = "http://localhost:8000/api/v1"

# Test scenarios for embeddings generation
TEST_SCENARIOS = {
    "generate_embedding_simple": {
        "description": "Generate embedding for simple text",
        "payload": {"text": "Hello world"},
        "expected_status": 200,
        "validation_fields": ["embedding"]
    },
    "generate_embedding_long": {
        "description": "Generate embedding for longer text",
        "payload": {
            "text": "This is a longer piece of text to test the embedding generation functionality with multiple words and sentences."
        },
        "expected_status": 200,
        "validation_fields": ["embedding"]
    },
    "generate_embedding_technical": {
        "description": "Generate embedding for technical text",
        "payload": {
            "text": "Vector databases use mathematical representations called embeddings to store and search through high-dimensional data efficiently."
        },
        "expected_status": 200,
        "validation_fields": ["embedding"]
    },
    "generate_embedding_special_chars": {
        "description": "Generate embedding for text with special characters",
        "payload": {
            "text": "Hello! How are you? I'm fine, thanks. Let's test @#$%^&*() characters."
        },
        "expected_status": 200,
        "validation_fields": ["embedding"]
    }
}

# Error test cases for embeddings
ERROR_TEST_CASES = {
    "missing_text": {
        "payload": {},
        "expected_status": 422,
        "description": "Missing text field"
    },
    "empty_text": {
        "payload": {"text": ""},
        "expected_status": 400,
        "description": "Empty text string"
    },
    "null_text": {
        "payload": {"text": None},
        "expected_status": 422,
        "description": "Null text value"
    },
    "invalid_json": {
        "payload": "invalid json",
        "expected_status": 422,
        "description": "Invalid JSON format"
    }
}

# Expected response schema for embeddings
EXPECTED_EMBEDDING_RESPONSE_SCHEMA = {
    "embedding": list
}

# Performance test cases
PERFORMANCE_TEST_CASES = {
    "short_text": {
        "text": "Short text",
        "max_response_time": 5.0  # 5 seconds max for local testing
    },
    "medium_text": {
        "text": "This is a medium length text that should still process quickly for embedding generation testing purposes.",
        "max_response_time": 10.0  # 10 seconds max
    },
    "long_text": {
        "text": " ".join(["This is a very long text"] * 50),  # 250 words
        "max_response_time": 15.0  # 15 seconds max
    }
}