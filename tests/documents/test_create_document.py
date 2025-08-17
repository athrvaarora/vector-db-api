#!/usr/bin/env python3
"""
Individual test script for POST /api/v1/documents (Create Document)
Tests document creation with valid data and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_DOCUMENT_PAYLOAD, EXPECTED_DOCUMENT_SCHEMA, get_test_library_payload


def test_create_document_valid():
    """Test creating a document with valid data."""
    result = TestResult("create_document_valid", "Create document with valid data")
    tester = APITester(BASE_URL)
    
    try:
        # First create a test library
        library_payload = get_test_library_payload()
        lib_status, lib_data, _ = tester.make_request('POST', '/libraries', library_payload)
        
        if lib_status != 201 or not lib_data:
            result.mark_failed(f"Failed to create test library: status {lib_status}")
            return result
            
        library_id = lib_data['id']
        
        # Update the payload with the actual library ID
        document_payload = CREATE_DOCUMENT_PAYLOAD.copy()
        document_payload['library_id'] = library_id
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/documents', document_payload
        )
        
        if status_code != 201:
            result.mark_failed(f"Expected status 201, got {status_code}", status_code, 201)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate response schema
        schema_errors = tester.validate_schema(response_data, EXPECTED_DOCUMENT_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        # Validate specific fields
        if response_data['metadata']['title'] != document_payload['metadata']['title']:
            result.mark_failed("Document title doesn't match payload")
            return result
            
        if response_data['library_id'] != library_id:
            result.mark_failed("Document library_id doesn't match payload")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_create_document_missing_fields():
    """Test creating a document with missing required fields."""
    result = TestResult("create_document_missing", "Create document with missing fields")
    tester = APITester(BASE_URL)
    
    try:
        invalid_payload = {"metadata": {"title": ""}}  # Missing library_id and other fields
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/documents', invalid_payload
        )
        
        if status_code not in [400, 422]:
            result.mark_failed(f"Expected status 400 or 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_create_document_nonexistent_library():
    """Test creating a document with non-existent library."""
    result = TestResult("create_document_no_lib", "Create document with non-existent library")
    tester = APITester(BASE_URL)
    
    try:
        document_payload = CREATE_DOCUMENT_PAYLOAD.copy()
        document_payload['library_id'] = "550e8400-e29b-41d4-a716-446655440999"  # Non-existent
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/documents', document_payload
        )
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_create_document_invalid_library_uuid():
    """Test creating a document with invalid library UUID."""
    result = TestResult("create_document_bad_uuid", "Create document with invalid library UUID")
    tester = APITester(BASE_URL)
    
    try:
        document_payload = CREATE_DOCUMENT_PAYLOAD.copy()
        document_payload['library_id'] = "invalid-uuid-format"
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/documents', document_payload
        )
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all create document tests."""
    print_test_header("CREATE DOCUMENT TESTS")
    
    tests = [
        test_create_document_valid,
        test_create_document_missing_fields,
        test_create_document_nonexistent_library,
        test_create_document_invalid_library_uuid
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