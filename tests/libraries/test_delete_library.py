#!/usr/bin/env python3
"""
Individual test script for DELETE /api/v1/libraries/{library_id} (Delete Library)
Tests deleting libraries and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_LIBRARY_PAYLOAD


def test_delete_library_valid():
    """Test deleting a library with valid ID."""
    result = TestResult("delete_library_valid", "Delete library with valid ID")
    tester = APITester(BASE_URL)
    
    try:
        # First create a test library
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Now delete the library
        status_code, response_data, response_time = tester.make_request('DELETE', f'/libraries/{library_id}')
        
        if status_code != 204:
            result.mark_failed(f"Expected status 204, got {status_code}", status_code, 204)
            return result
            
        # Verify the library is actually deleted by trying to get it
        get_status, get_data, _ = tester.make_request('GET', f'/libraries/{library_id}')
        
        if get_status != 404:
            result.mark_failed(f"Library still exists after deletion: GET returned {get_status}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_delete_library_nonexistent():
    """Test deleting a non-existent library."""
    result = TestResult("delete_library_404", "Delete non-existent library")
    tester = APITester(BASE_URL)
    
    try:
        fake_id = "550e8400-e29b-41d4-a716-446655440999"
        
        status_code, response_data, response_time = tester.make_request('DELETE', f'/libraries/{fake_id}')
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_delete_library_invalid_uuid():
    """Test deleting a library with invalid UUID."""
    result = TestResult("delete_library_invalid", "Delete library with invalid UUID")
    tester = APITester(BASE_URL)
    
    try:
        invalid_id = "invalid-uuid-format"
        
        status_code, response_data, response_time = tester.make_request('DELETE', f'/libraries/{invalid_id}')
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_delete_library_twice():
    """Test deleting the same library twice."""
    result = TestResult("delete_library_twice", "Delete library twice")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Delete the library first time
        first_delete_status, _, _ = tester.make_request('DELETE', f'/libraries/{library_id}')
        
        if first_delete_status != 204:
            result.mark_failed(f"First delete failed with status {first_delete_status}")
            return result
            
        # Try to delete the same library again
        status_code, response_data, response_time = tester.make_request('DELETE', f'/libraries/{library_id}')
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404 for second delete, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_delete_library_cascade():
    """Test that deleting a library handles related data properly."""
    result = TestResult("delete_library_cascade", "Delete library with related data")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Check stats before deletion
        stats_status, stats_data, _ = tester.make_request('GET', f'/libraries/{library_id}/stats')
        
        if stats_status != 200:
            result.mark_failed(f"Failed to get library stats: status {stats_status}")
            return result
            
        # Delete the library
        status_code, response_data, response_time = tester.make_request('DELETE', f'/libraries/{library_id}')
        
        if status_code != 204:
            result.mark_failed(f"Expected status 204, got {status_code}", status_code, 204)
            return result
            
        # Verify stats endpoint also returns 404
        post_delete_stats_status, _, _ = tester.make_request('GET', f'/libraries/{library_id}/stats')
        
        if post_delete_stats_status != 404:
            result.mark_failed(f"Stats endpoint should return 404 after library deletion, got {post_delete_stats_status}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_delete_library_idempotent():
    """Test that delete operations are properly idempotent."""
    result = TestResult("delete_library_idempotent", "Delete library idempotency")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Delete the library
        delete_status, _, _ = tester.make_request('DELETE', f'/libraries/{library_id}')
        
        if delete_status != 204:
            result.mark_failed(f"Delete failed with status {delete_status}")
            return result
            
        # Multiple subsequent delete attempts should be consistent
        for i in range(3):
            status_code, response_data, response_time = tester.make_request('DELETE', f'/libraries/{library_id}')
            
            if status_code != 404:
                result.mark_failed(f"Delete attempt {i+1} returned {status_code}, expected 404")
                return result
                
        result.mark_passed(404, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all delete library tests."""
    print_test_header("DELETE LIBRARY TESTS")
    
    tests = [
        test_delete_library_valid,
        test_delete_library_nonexistent,
        test_delete_library_invalid_uuid,
        test_delete_library_twice,
        test_delete_library_cascade,
        test_delete_library_idempotent
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