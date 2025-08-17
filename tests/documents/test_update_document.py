#!/usr/bin/env python3
"""
Individual test script for PUT /api/v1/documents/{document_id} (Update Document)
Tests updating document data and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_DOCUMENT_PAYLOAD, UPDATE_DOCUMENT_PAYLOAD, EXPECTED_DOCUMENT_SCHEMA, get_test_library_payload


def test_update_document_valid():
    """Test updating a document with valid data."""
    result = TestResult("update_document_valid", "Update document with valid data")
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
        
        # Now update the document
        status_code, response_data, response_time = tester.make_request(
            'PUT', f'/documents/{document_id}', UPDATE_DOCUMENT_PAYLOAD
        )
        
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
            
        # Validate the ID remains the same
        if response_data['id'] != document_id:
            result.mark_failed(f"Document ID changed: expected {document_id}, got {response_data['id']}")
            return result
            
        # Validate the data was actually updated
        if response_data['metadata']['title'] != UPDATE_DOCUMENT_PAYLOAD['metadata']['title']:
            result.mark_failed("Document title was not updated")
            return result
            
        if response_data['metadata']['description'] != UPDATE_DOCUMENT_PAYLOAD['metadata']['description']:
            result.mark_failed("Document description was not updated")
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


def test_update_document_nonexistent():
    """Test updating a non-existent document."""
    result = TestResult("update_document_404", "Update non-existent document")
    tester = APITester(BASE_URL)
    
    try:
        fake_id = "550e8400-e29b-41d4-a716-446655440999"
        
        status_code, response_data, response_time = tester.make_request(
            'PUT', f'/documents/{fake_id}', UPDATE_DOCUMENT_PAYLOAD
        )
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_update_document_invalid_uuid():
    """Test updating a document with invalid UUID."""
    result = TestResult("update_document_invalid", "Update document with invalid UUID")
    tester = APITester(BASE_URL)
    
    try:
        invalid_id = "invalid-uuid-format"
        
        status_code, response_data, response_time = tester.make_request(
            'PUT', f'/documents/{invalid_id}', UPDATE_DOCUMENT_PAYLOAD
        )
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_update_document_invalid_payload():
    """Test updating a document with invalid payload."""
    result = TestResult("update_document_bad_data", "Update document with invalid payload")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library and document first
        library_payload = get_test_library_payload()
        lib_status, lib_data, _ = tester.make_request('POST', '/libraries', library_payload)
        
        if lib_status != 201 or not lib_data:
            result.mark_failed(f"Failed to create test library: status {lib_status}")
            return result
            
        library_id = lib_data['id']
        
        document_payload = CREATE_DOCUMENT_PAYLOAD.copy()
        document_payload['library_id'] = library_id
        create_status, create_data, _ = tester.make_request('POST', '/documents', document_payload)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test document: status {create_status}")
            return result
            
        document_id = create_data['id']
        
        # Try to update with invalid payload
        invalid_payload = {"invalid": "structure"}
        
        status_code, response_data, response_time = tester.make_request(
            'PUT', f'/documents/{document_id}', invalid_payload
        )
        
        if status_code not in [400, 422]:
            result.mark_failed(f"Expected status 400 or 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_update_document_partial():
    """Test updating a document with partial data."""
    result = TestResult("update_document_partial", "Update document with partial data")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library and document first
        library_payload = get_test_library_payload()
        lib_status, lib_data, _ = tester.make_request('POST', '/libraries', library_payload)
        
        if lib_status != 201 or not lib_data:
            result.mark_failed(f"Failed to create test library: status {lib_status}")
            return result
            
        library_id = lib_data['id']
        
        document_payload = CREATE_DOCUMENT_PAYLOAD.copy()
        document_payload['library_id'] = library_id
        create_status, create_data, _ = tester.make_request('POST', '/documents', document_payload)
        
        if create_status != 201 or not create_data:
            result.mark_failed(f"Failed to create test document: status {create_status}")
            return result
            
        document_id = create_data['id']
        
        # Update with partial data (only title and description)
        partial_payload = {
            "metadata": {
                "title": "Partially Updated Document",
                "description": create_data['metadata']['description'],
                "author": create_data['metadata']['author'],
                "tags": create_data['metadata']['tags'],
                "category": create_data['metadata']['category'],
                "file_type": create_data['metadata']['file_type']
            }
        }
        
        status_code, response_data, response_time = tester.make_request(
            'PUT', f'/documents/{document_id}', partial_payload
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate the title was updated
        if response_data['metadata']['title'] != "Partially Updated Document":
            result.mark_failed("Document title was not updated")
            return result
            
        # Validate other fields remained the same
        if response_data['metadata']['description'] != create_data['metadata']['description']:
            result.mark_failed("Document description was unexpectedly changed")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all update document tests."""
    print_test_header("UPDATE DOCUMENT TESTS")
    
    tests = [
        test_update_document_valid,
        test_update_document_nonexistent,
        test_update_document_invalid_uuid,
        test_update_document_invalid_payload,
        test_update_document_partial
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