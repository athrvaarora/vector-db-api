#!/usr/bin/env python3
"""
Individual test script for GET /api/v1/libraries/{library_id}/stats (Get Library Stats)
Tests retrieving library statistics and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_LIBRARY_PAYLOAD, EXPECTED_LIBRARY_STATS_SCHEMA


def test_get_library_stats_valid():
    """Test getting library stats with valid ID."""
    result = TestResult("get_stats_valid", "Get library stats with valid ID")
    tester = APITester(BASE_URL)
    
    try:
        # First create a test library
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Now get the library stats
        status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{library_id}/stats')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate response schema
        schema_errors = tester.validate_schema(response_data, EXPECTED_LIBRARY_STATS_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        # Validate expected initial values for a new library
        if response_data['total_documents'] != 0:
            result.mark_failed(f"Expected 0 documents for new library, got {response_data['total_documents']}")
            return result
            
        if response_data['total_chunks'] != 0:
            result.mark_failed(f"Expected 0 chunks for new library, got {response_data['total_chunks']}")
            return result
            
        # Check that optional fields are present
        if 'embedding_dimension' not in response_data:
            result.mark_failed("Missing embedding_dimension field")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_library_stats_nonexistent():
    """Test getting stats for a non-existent library."""
    result = TestResult("get_stats_404", "Get stats for non-existent library")
    tester = APITester(BASE_URL)
    
    try:
        fake_id = "550e8400-e29b-41d4-a716-446655440999"
        
        status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{fake_id}/stats')
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_library_stats_invalid_uuid():
    """Test getting stats with invalid UUID format."""
    result = TestResult("get_stats_invalid", "Get stats with invalid UUID")
    tester = APITester(BASE_URL)
    
    try:
        invalid_id = "invalid-uuid-format"
        
        status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{invalid_id}/stats')
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_library_stats_consistency():
    """Test that library stats are consistent across multiple calls."""
    result = TestResult("get_stats_consistency", "Get stats consistency check")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Get stats multiple times and ensure consistency
        stats_responses = []
        for i in range(3):
            status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{library_id}/stats')
            if status_code != 200:
                result.mark_failed(f"Stats request {i+1} failed with status {status_code}")
                return result
            stats_responses.append(response_data)
            
        # Check that all responses are identical
        for i, response in enumerate(stats_responses[1:], 1):
            if response != stats_responses[0]:
                result.mark_failed(f"Stats response {i+1} differs from first response")
                return result
                
        result.mark_passed(200, response_time, stats_responses[0])
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_library_stats_after_deletion():
    """Test that stats endpoint returns 404 after library deletion."""
    result = TestResult("get_stats_after_delete", "Get stats after library deletion")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Verify stats work before deletion
        stats_status, _, _ = tester.make_request('GET', f'/libraries/{library_id}/stats')
        if stats_status != 200:
            result.mark_failed(f"Stats failed before deletion: status {stats_status}")
            return result
            
        # Delete the library
        delete_status, _, _ = tester.make_request('DELETE', f'/libraries/{library_id}')
        if delete_status != 204:
            result.mark_failed(f"Failed to delete library: status {delete_status}")
            return result
            
        # Now try to get stats - should return 404
        status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{library_id}/stats')
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404 after deletion, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_library_stats_data_types():
    """Test that stats response contains correct data types."""
    result = TestResult("get_stats_types", "Validate stats data types")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Get the library stats
        status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{library_id}/stats')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Detailed type checking
        if not isinstance(response_data['total_documents'], int):
            result.mark_failed(f"total_documents should be int, got {type(response_data['total_documents'])}")
            return result
            
        if not isinstance(response_data['total_chunks'], int):
            result.mark_failed(f"total_chunks should be int, got {type(response_data['total_chunks'])}")
            return result
            
        # last_indexed can be null or string
        if response_data['last_indexed'] is not None and not isinstance(response_data['last_indexed'], str):
            result.mark_failed(f"last_indexed should be str or null, got {type(response_data['last_indexed'])}")
            return result
            
        # embedding_dimension and index_type can be null
        if response_data['embedding_dimension'] is not None and not isinstance(response_data['embedding_dimension'], int):
            result.mark_failed(f"embedding_dimension should be int or null, got {type(response_data['embedding_dimension'])}")
            return result
            
        if response_data['index_type'] is not None and not isinstance(response_data['index_type'], str):
            result.mark_failed(f"index_type should be str or null, got {type(response_data['index_type'])}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all get library stats tests."""
    print_test_header("GET LIBRARY STATS TESTS")
    
    tests = [
        test_get_library_stats_valid,
        test_get_library_stats_nonexistent,
        test_get_library_stats_invalid_uuid,
        test_get_library_stats_consistency,
        test_get_library_stats_after_deletion,
        test_get_library_stats_data_types
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