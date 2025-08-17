#!/usr/bin/env python3
"""
Individual test script for DELETE /api/v1/documents/{document_id} (Delete Document)
Tests deleting documents and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_DOCUMENT_PAYLOAD, get_test_library_payload


def test_delete_document_valid():
    """Test deleting a document with valid ID."""
    result = TestResult("delete_document_valid", "Delete document with valid ID")
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
        
        # Now delete the document
        status_code, response_data, response_time = tester.make_request('DELETE', f'/documents/{document_id}')
        
        if status_code != 204:
            result.mark_failed(f"Expected status 204, got {status_code}", status_code, 204)
            return result
            
        # Verify the document is actually deleted by trying to get it
        get_status, get_data, _ = tester.make_request('GET', f'/documents/{document_id}')
        
        if get_status != 404:
            result.mark_failed(f"Document still exists after deletion: GET returned {get_status}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_delete_document_nonexistent():
    """Test deleting a non-existent document."""
    result = TestResult("delete_document_404", "Delete non-existent document")
    tester = APITester(BASE_URL)
    
    try:
        fake_id = "550e8400-e29b-41d4-a716-446655440999"
        
        status_code, response_data, response_time = tester.make_request('DELETE', f'/documents/{fake_id}')
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_delete_document_invalid_uuid():
    """Test deleting a document with invalid UUID."""
    result = TestResult("delete_document_invalid", "Delete document with invalid UUID")
    tester = APITester(BASE_URL)
    
    try:
        invalid_id = "invalid-uuid-format"
        
        status_code, response_data, response_time = tester.make_request('DELETE', f'/documents/{invalid_id}')
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_delete_document_twice():
    """Test deleting the same document twice."""
    result = TestResult("delete_document_twice", "Delete document twice")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library and document
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
        
        # Delete the document first time
        first_delete_status, _, _ = tester.make_request('DELETE', f'/documents/{document_id}')
        
        if first_delete_status != 204:
            result.mark_failed(f"First delete failed with status {first_delete_status}")
            return result
            
        # Try to delete the same document again
        status_code, response_data, response_time = tester.make_request('DELETE', f'/documents/{document_id}')
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404 for second delete, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_delete_document_cascade():
    """Test that deleting a document handles related data properly."""
    result = TestResult("delete_document_cascade", "Delete document with related data")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library and document
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
        
        # Check that the document exists in the library's documents list
        lib_docs_status, lib_docs_data, _ = tester.make_request('GET', f'/libraries/{library_id}/documents')
        
        if lib_docs_status != 200:
            result.mark_failed(f"Failed to get library documents: status {lib_docs_status}")
            return result
            
        # Delete the document
        status_code, response_data, response_time = tester.make_request('DELETE', f'/documents/{document_id}')
        
        if status_code != 204:
            result.mark_failed(f"Expected status 204, got {status_code}", status_code, 204)
            return result
            
        # Verify the document is removed from the library's documents list
        post_delete_docs_status, post_delete_docs_data, _ = tester.make_request('GET', f'/libraries/{library_id}/documents')
        
        if post_delete_docs_status != 200:
            result.mark_failed(f"Failed to get library documents after deletion: status {post_delete_docs_status}")
            return result
            
        # Check that the deleted document is not in the list
        for doc in post_delete_docs_data:
            if doc['id'] == document_id:
                result.mark_failed("Document still appears in library documents list after deletion")
                return result
                
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_delete_document_idempotent():
    """Test that delete operations are properly idempotent."""
    result = TestResult("delete_document_idempotent", "Delete document idempotency")
    tester = APITester(BASE_URL)
    
    try:
        # Create a test library and document
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
        
        # Delete the document
        delete_status, _, _ = tester.make_request('DELETE', f'/documents/{document_id}')
        
        if delete_status != 204:
            result.mark_failed(f"Delete failed with status {delete_status}")
            return result
            
        # Multiple subsequent delete attempts should be consistent
        for i in range(3):
            status_code, response_data, response_time = tester.make_request('DELETE', f'/documents/{document_id}')
            
            if status_code != 404:
                result.mark_failed(f"Delete attempt {i+1} returned {status_code}, expected 404")
                return result
                
        result.mark_passed(404, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all delete document tests."""
    print_test_header("DELETE DOCUMENT TESTS")
    
    tests = [
        test_delete_document_valid,
        test_delete_document_nonexistent,
        test_delete_document_invalid_uuid,
        test_delete_document_twice,
        test_delete_document_cascade,
        test_delete_document_idempotent
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