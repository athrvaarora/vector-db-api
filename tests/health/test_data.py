"""
Test data for health endpoint tests.
Contains predefined test data for health check operations.
"""

from typing import Dict, Any
from datetime import datetime

# Base URL for API endpoints
BASE_URL = "http://localhost:8000/api/v1"

# Expected response schema for health check
EXPECTED_HEALTH_RESPONSE_SCHEMA = {
    "status": str,
    "service": (str, type(None)),
    "version": (str, type(None))
}

# Expected health status values
EXPECTED_HEALTH_STATUSES = ["healthy", "ok", "up", "running"]

# Test scenarios for health check
TEST_SCENARIOS = {
    "health_check_basic": {
        "description": "Basic health check",
        "expected_status": 200,
        "validation_fields": ["status", "service", "version"]
    },
    "health_check_performance": {
        "description": "Health check performance test",
        "expected_status": 200,
        "max_response_time": 2.0  # Health checks should be fast
    },
    "health_check_consistency": {
        "description": "Health check consistency test",
        "expected_status": 200,
        "validation_fields": ["status", "service", "version"]
    }
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "max_response_time": 2.0,  # 2 seconds max for health check
    "min_uptime": 0.0,  # Uptime should be non-negative
    "timestamp_format": "%Y-%m-%dT%H:%M:%S"  # Expected timestamp format (ISO-like)
}