#!/usr/bin/env python3
"""
Individual test script for GET /api/v1/documents and GET /api/v1/libraries/{library_id}/documents
Tests retrieving documents and validates response format.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_DOCUMENT_PAYLOAD, EXPECTED_DOCUMENT_SCHEMA, get_test_library_payload


def test_list_all_documents_empty():
    """Test listing all documents when database might be empty."""
    result = TestResult("list_documents_empty", "List all documents (may be empty)")
    tester = APITester(BASE_URL)
    
    try:
        status_code, response_data, response_time = tester.make_request('GET', '/documents')
        
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


def test_list_all_documents_with_data():
    """Test listing all documents after creating test data."""
    result = TestResult("list_documents_data", "List all documents with test data")
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
        doc_status, doc_data, _ = tester.make_request('POST', '/documents', document_payload)
        
        if doc_status != 201:
            result.mark_failed(f"Failed to create test document: status {doc_status}")
            return result
            
        # Now list all documents
        status_code, response_data, response_time = tester.make_request('GET', '/documents')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not isinstance(response_data, list):
            result.mark_failed(f"Expected list response, got {type(response_data).__name__}")
            return result
            
        if len(response_data) == 0:
            result.mark_failed("Expected at least one document in response")
            return result
            
        # Validate schema of first document
        first_document = response_data[0]
        schema_errors = tester.validate_schema(first_document, EXPECTED_DOCUMENT_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_list_documents_by_library():
    """Test listing documents by library ID."""
    result = TestResult("list_documents_by_lib", "List documents by library ID")
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
        doc_status, doc_data, _ = tester.make_request('POST', '/documents', document_payload)
        
        if doc_status != 201:
            result.mark_failed(f"Failed to create test document: status {doc_status}")
            return result
            
        # Now list documents by library
        status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{library_id}/documents')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not isinstance(response_data, list):
            result.mark_failed(f"Expected list response, got {type(response_data).__name__}")
            return result
            
        if len(response_data) == 0:
            result.mark_failed("Expected at least one document in library")
            return result
            
        # Validate that all documents belong to the library
        for doc in response_data:
            if doc['library_id'] != library_id:
                result.mark_failed(f"Document {doc['id']} doesn't belong to library {library_id}")
                return result
                
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_list_documents_nonexistent_library():
    """Test listing documents for non-existent library."""
    result = TestResult("list_docs_no_lib", "List documents for non-existent library")
    tester = APITester(BASE_URL)
    
    try:
        fake_library_id = "550e8400-e29b-41d4-a716-446655440999"
        
        status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{fake_library_id}/documents')
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_list_documents_invalid_library_uuid():
    """Test listing documents with invalid library UUID."""
    result = TestResult("list_docs_bad_uuid", "List documents with invalid library UUID")
    tester = APITester(BASE_URL)
    
    try:
        invalid_library_id = "invalid-uuid-format"
        
        status_code, response_data, response_time = tester.make_request('GET', f'/libraries/{invalid_library_id}/documents')
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_list_documents_performance():
    """Test that list documents responds within acceptable time."""
    result = TestResult("list_documents_perf", "List documents performance test")
    tester = APITester(BASE_URL)
    
    try:
        status_code, response_data, response_time = tester.make_request('GET', '/documents')
        
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
    """Run all list documents tests."""
    print_test_header("LIST DOCUMENTS TESTS")
    
    tests = [
        test_list_all_documents_empty,
        test_list_all_documents_with_data,
        test_list_documents_by_library,
        test_list_documents_nonexistent_library,
        test_list_documents_invalid_library_uuid,
        test_list_documents_performance
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