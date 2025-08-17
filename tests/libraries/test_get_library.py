#!/usr/bin/env python3
"""
Individual test script for GET /api/v1/libraries/{library_id} (Get Library)
Tests retrieving a specific library by ID and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_LIBRARY_PAYLOAD, EXPECTED_LIBRARY_SCHEMA


def test_get_library_valid():
    """Test getting a library with valid ID."""
    result = TestResult("get_library_valid", "Get library with valid ID")
    tester = APITester(BASE_URL)
    
    try:
        # First create a test library
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data or 'id' not in create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Now get the library
        status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{library_id}')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate response schema
        schema_errors = tester.validate_schema(response_data, EXPECTED_LIBRARY_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        # Validate the ID matches
        if response_data['id'] != library_id:
            result.mark_failed(f"Library ID mismatch: expected {library_id}, got {response_data['id']}")
            return result
            
        # Validate the data matches what we created
        if response_data['metadata']['name'] != CREATE_LIBRARY_PAYLOAD['metadata']['name']:
            result.mark_failed("Library data doesn't match created library")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_library_nonexistent():
    """Test getting a library with non-existent ID."""
    result = TestResult("get_library_404", "Get non-existent library")
    tester = APITester(BASE_URL)
    
    try:
        # Use a valid UUID format but non-existent ID
        fake_id = "550e8400-e29b-41d4-a716-446655440999"
        
        status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{fake_id}')
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_library_invalid_uuid():
    """Test getting a library with invalid UUID format."""
    result = TestResult("get_library_invalid", "Get library with invalid UUID")
    tester = APITester(BASE_URL)
    
    try:
        invalid_id = "invalid-uuid-format"
        
        status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{invalid_id}')
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_library_empty_id():
    """Test getting a library with empty ID."""
    result = TestResult("get_library_empty", "Get library with empty ID")
    tester = APITester(BASE_URL)
    
    try:
        # This should hit the list endpoint instead, or return 404
        status_code, response_data, response_time = tester.make_request('GET', '/libraries/')
        
        # Could be 404 (not found) or 200 (redirected to list)
        if status_code not in [200, 404, 405]:
            result.mark_failed(f"Expected status 200, 404, or 405, got {status_code}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_library_consistency():
    """Test that getting a library returns consistent data."""
    result = TestResult("get_library_consistency", "Get library data consistency")
    tester = APITester(BASE_URL)
    
    try:
        # Create a library
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Get the library multiple times and ensure consistency
        responses = []
        for i in range(3):
            status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{library_id}')
            if status_code != 200:
                result.mark_failed(f"Request {i+1} failed with status {status_code}")
                return result
            responses.append(response_data)
            
        # Check that all responses are identical
        for i, response in enumerate(responses[1:], 1):
            if response != responses[0]:
                result.mark_failed(f"Response {i+1} differs from first response")
                return result
                
        result.mark_passed(200, response_time, responses[0])
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all get library tests."""
    print_test_header("GET LIBRARY TESTS")
    
    tests = [
        test_get_library_valid,
        test_get_library_nonexistent,
        test_get_library_invalid_uuid,
        test_get_library_empty_id,
        test_get_library_consistency
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