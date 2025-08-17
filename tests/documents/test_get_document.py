#!/usr/bin/env python3
"""
Individual test script for GET /api/v1/documents/{document_id} (Get Document)
Tests retrieving a specific document by ID and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_DOCUMENT_PAYLOAD, EXPECTED_DOCUMENT_SCHEMA, get_test_library_payload


def test_get_document_valid():
    """Test getting a document with valid ID."""
    result = TestResult("get_document_valid", "Get document with valid ID")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library first
        library_payload = get_test_library_payload()
        lib_status, lib_data, _ = tester.make_request('POST', '/libraries', library_payload)
        
        if lib_status != 201 or not lib_data:
            result.mark_failed(f"Failed to create test library: status {lib_status}")
            return result
            
        library_id = lib_data['id']
        
        # Create a test document
        document_payload = CREATE_DOCUMENT_PAYLOAD.copy()
        document_payload['library_id'] = library_id
        create_status, create_data, _ = tester.make_request('POST', '/documents', document_payload)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test document: status {create_status}")
            return result
            
        document_id = create_data['id']
        
        # Now get the document
        status_code, response_data, response_time = tester.make_request('GET', f'/documents/{document_id}')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate response schema
        schema_errors = tester.validate_schema(response_data, EXPECTED_DOCUMENT_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        # Validate the ID matches
        if response_data['id'] != document_id:
            result.mark_failed(f"Document ID mismatch: expected {document_id}, got {response_data['id']}")
            return result
            
        # Validate the data matches what we created
        if response_data['metadata']['title'] != document_payload['metadata']['title']:
            result.mark_failed("Document data doesn't match created document")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_document_nonexistent():
    """Test getting a document with non-existent ID."""
    result = TestResult("get_document_404", "Get non-existent document")
    tester = APITester(BASE_URL)
    
    try:
        fake_id = "550e8400-e29b-41d4-a716-446655440999"
        
        status_code, response_data, response_time = tester.make_request('GET', f'/documents/{fake_id}')
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_document_invalid_uuid():
    """Test getting a document with invalid UUID format."""
    result = TestResult("get_document_invalid", "Get document with invalid UUID")
    tester = APITester(BASE_URL)
    
    try:
        invalid_id = "invalid-uuid-format"
        
        status_code, response_data, response_time = tester.make_request('GET', f'/documents/{invalid_id}')
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_get_document_consistency():
    """Test that getting a document returns consistent data."""
    result = TestResult("get_document_consistency", "Get document data consistency")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library first
        library_payload = get_test_library_payload()
        lib_status, lib_data, _ = tester.make_request('POST', '/libraries', library_payload)
        
        if lib_status != 201 or not lib_data:
            result.mark_failed(f"Failed to create test library: status {lib_status}")
            return result
            
        library_id = lib_data['id']
        
        # Create a test document
        document_payload = CREATE_DOCUMENT_PAYLOAD.copy()
        document_payload['library_id'] = library_id
        create_status, create_data, _ = tester.make_request('POST', '/documents', document_payload)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test document: status {create_status}")
            return result
            
        document_id = create_data['id']
        
        # Get the document multiple times and ensure consistency
        responses = []
        for i in range(3):
            status_code, response_data, response_time = tester.make_request('GET', f'/documents/{document_id}')
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
    """Run all get document tests."""
    print_test_header("GET DOCUMENT TESTS")
    
    tests = [
        test_get_document_valid,
        test_get_document_nonexistent,
        test_get_document_invalid_uuid,
        test_get_document_consistency
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