#!/usr/bin/env python3
"""
Individual test script for PUT /api/v1/libraries/{library_id} (Update Library)
Tests updating library data and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_LIBRARY_PAYLOAD, UPDATE_LIBRARY_PAYLOAD, EXPECTED_LIBRARY_SCHEMA


def test_update_library_valid():
    """Test updating a library with valid data."""
    result = TestResult("update_library_valid", "Update library with valid data")
    tester = APITester(BASE_URL)
    
    try:
        # First create a test library
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Now update the library
        status_code, response_data, response_time = tester.make_request(
            'PUT', f'/libraries/{library_id}', UPDATE_LIBRARY_PAYLOAD
        )
        
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
            
        # Validate the ID remains the same
        if response_data['id'] != library_id:
            result.mark_failed(f"Library ID changed: expected {library_id}, got {response_data['id']}")
            return result
            
        # Validate the data was actually updated
        if response_data['metadata']['name'] != UPDATE_LIBRARY_PAYLOAD['metadata']['name']:
            result.mark_failed("Library name was not updated")
            return result
            
        if response_data['metadata']['description'] != UPDATE_LIBRARY_PAYLOAD['metadata']['description']:
            result.mark_failed("Library description was not updated")
            return result
            
        # Validate updated_at timestamp changed (it's in metadata)
        if response_data['metadata']['updated_at'] == create_data['metadata']['updated_at']:
            result.mark_failed("updated_at timestamp was not changed")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_update_library_nonexistent():
    """Test updating a non-existent library."""
    result = TestResult("update_library_404", "Update non-existent library")
    tester = APITester(BASE_URL)
    
    try:
        fake_id = "550e8400-e29b-41d4-a716-446655440999"
        
        status_code, response_data, response_time = tester.make_request(
            'PUT', f'/libraries/{fake_id}', UPDATE_LIBRARY_PAYLOAD
        )
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_update_library_invalid_uuid():
    """Test updating a library with invalid UUID."""
    result = TestResult("update_library_invalid", "Update library with invalid UUID")
    tester = APITester(BASE_URL)
    
    try:
        invalid_id = "invalid-uuid-format"
        
        status_code, response_data, response_time = tester.make_request(
            'PUT', f'/libraries/{invalid_id}', UPDATE_LIBRARY_PAYLOAD
        )
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_update_library_invalid_payload():
    """Test updating a library with invalid payload."""
    result = TestResult("update_library_bad_data", "Update library with invalid payload")
    tester = APITester(BASE_URL)
    
    try:
        # Create a library first
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Try to update with invalid payload
        invalid_payload = {"invalid": "structure"}
        
        status_code, response_data, response_time = tester.make_request(
            'PUT', f'/libraries/{library_id}', invalid_payload
        )
        
        if status_code not in [400, 422]:
            result.mark_failed(f"Expected status 400 or 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_update_library_partial():
    """Test updating a library with partial data."""
    result = TestResult("update_library_partial", "Update library with partial data")
    tester = APITester(BASE_URL)
    
    try:
        # Create a library first
        create_status, create_data, _ = tester.make_request('POST', '/libraries', CREATE_LIBRARY_PAYLOAD)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test library: status {create_status}")
            return result
            
        library_id = create_data['id']
        
        # Update with partial data (only name)
        partial_payload = {
            "metadata": {
                "name": "Partially Updated Library",
                "description": create_data['metadata']['description'],
                "tags": create_data['metadata']['tags'],
                "is_public": create_data['metadata']['is_public'],
                "owner": create_data['metadata']['owner']
            }
        }
        
        status_code, response_data, response_time = tester.make_request(
            'PUT', f'/libraries/{library_id}', partial_payload
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate the name was updated
        if response_data['metadata']['name'] != "Partially Updated Library":
            result.mark_failed("Library name was not updated")
            return result
            
        # Validate other fields remained the same
        if response_data['metadata']['description'] != create_data['metadata']['description']:
            result.mark_failed("Library description was unexpectedly changed")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all update library tests."""
    print_test_header("UPDATE LIBRARY TESTS")
    
    tests = [
        test_update_library_valid,
        test_update_library_nonexistent,
        test_update_library_invalid_uuid,
        test_update_library_invalid_payload,
        test_update_library_partial
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