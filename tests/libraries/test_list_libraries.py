#!/usr/bin/env python3
"""
Individual test script for GET /api/v1/libraries (List Libraries)
Tests retrieving all libraries and validates response format.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, EXPECTED_LIBRARY_SCHEMA


def test_list_libraries_empty():
    """Test listing libraries when database might be empty."""
    result = TestResult("list_libraries_empty", "List libraries (may be empty)")
    tester = APITester(BASE_URL)
    
    try:
        status_code, response_data, response_time = tester.make_request('GET', '/libraries')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not isinstance(response_data, list):
            result.mark_failed(f"Expected list response, got {type(response_data).__name__}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_list_libraries_with_data():
    """Test listing libraries after creating test data."""
    result = TestResult("list_libraries_data", "List libraries with test data")
    tester = APITester(BASE_URL)
    
    try:
        # First create a test library
        from test_data import CREATE_LIBRARY_PAYLOAD
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        # Now list libraries
        status_code, response_data, response_time = tester.make_request('GET', '/libraries')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not isinstance(response_data, list):
            result.mark_failed(f"Expected list response, got {type(response_data).__name__}")
            return result
            
        if len(response_data) == 0:
            result.mark_failed("Expected at least one library in response")
            return result
            
        # Validate schema of first library
        first_library = response_data[0]
        schema_errors = tester.validate_schema(first_library, EXPECTED_LIBRARY_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_list_libraries_pagination():
    """Test that list endpoint returns properly formatted data."""
    result = TestResult("list_libraries_format", "Validate list response format")
    tester = APITester(BASE_URL)
    
    try:
        status_code, response_data, response_time = tester.make_request('GET', '/libraries')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Validate it's a list
        if not isinstance(response_data, list):
            result.mark_failed(f"Expected list response, got {type(response_data).__name__}")
            return result
            
        # If there are items, validate their structure
        if response_data:
            for i, library in enumerate(response_data):
                schema_errors = tester.validate_schema(library, EXPECTED_LIBRARY_SCHEMA)
                if schema_errors:
                    result.mark_failed(f"Library {i} schema validation failed: {', '.join(schema_errors)}")
                    return result
                    
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_list_libraries_response_time():
    """Test that list libraries responds within acceptable time."""
    result = TestResult("list_libraries_perf", "List libraries performance test")
    tester = APITester(BASE_URL)
    
    try:
        status_code, response_data, response_time = tester.make_request('GET', '/libraries')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Check response time (should be under 5 seconds for local testing)
        if response_time > 5.0:
            result.mark_failed(f"Response time too slow: {response_time:.3f}s (expected < 5s)")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all list libraries tests."""
    print_test_header("LIST LIBRARIES TESTS")
    
    tests = [
        test_list_libraries_empty,
        test_list_libraries_with_data,
        test_list_libraries_pagination,
        test_list_libraries_response_time
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