#!/usr/bin/env python3
"""
Individual test script for POST /api/v1/libraries (Create Library)
Tests library creation with valid data and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_LIBRARY_PAYLOAD, EXPECTED_LIBRARY_SCHEMA, ERROR_TEST_CASES


def test_create_library_valid():
    """Test creating a library with valid data."""
    result = TestResult("create_library_valid", "Create library with valid data")
    tester = APITester(BASE_URL)
    
    try:
        status_code, response_data, response_time = tester.make_request(
            'POST', '/libraries', CREATE_LIBRARY_PAYLOAD
        )
        
        if status_code != 201:
            result.mark_failed(f"Expected status 201, got {status_code}", status_code, 201)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate response schema
        schema_errors = tester.validate_schema(response_data, EXPECTED_LIBRARY_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        # Validate specific fields
        if response_data['metadata']['name'] != CREATE_LIBRARY_PAYLOAD['metadata']['name']:
            result.mark_failed("Library name doesn't match payload")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_create_library_missing_fields():
    """Test creating a library with missing required fields."""
    result = TestResult("create_library_missing", "Create library with missing fields")
    tester = APITester(BASE_URL)
    
    try:
        invalid_payload = {"metadata": {"name": ""}}  # Missing required fields
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/libraries', invalid_payload
        )
        
        if status_code not in [400, 422]:
            result.mark_failed(f"Expected status 400 or 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_create_library_invalid_json():
    """Test creating a library with invalid JSON structure."""
    result = TestResult("create_library_invalid", "Create library with invalid JSON")
    tester = APITester(BASE_URL)
    
    try:
        # Test with completely invalid structure
        invalid_payload = {"invalid": "structure"}
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/libraries', invalid_payload
        )
        
        if status_code not in [400, 422]:
            result.mark_failed(f"Expected status 400 or 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all create library tests."""
    print_test_header("CREATE LIBRARY TESTS")
    
    tests = [
        test_create_library_valid,
        test_create_library_missing_fields,
        test_create_library_invalid_json
    ]
    
    results = []
    for test_func in tests:
        result = test_func()
        print_test_result(result)
        results.append(result)
    
    print_summary_table(results)
    return results


if __name__ == "__main__":
    results = run_all_tests()
    
    # Exit with non-zero code if any tests failed
    failed_tests = [r for r in results if not r.passed]
    if failed_tests:
        sys.exit(1)
    else:
        sys.exit(0)