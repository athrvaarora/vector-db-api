#!/usr/bin/env python3
"""
Individual test script for GET /api/v1/documents/{document_id}/chunks (List Chunks)
Tests retrieving chunks by document ID and validates response format.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_CHUNK_PAYLOAD, EXPECTED_CHUNK_SCHEMA, get_test_library_payload, get_test_document_payload


def test_list_chunks_empty():
    """Test listing chunks for a document with no chunks."""
    result = TestResult("list_chunks_empty", "List chunks (may be empty)")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_payload = get_test_library_payload()
        lib_status, lib_data, _ = tester.make_request('POST', '/libraries', library_payload)
        
        if lib_status != 201 or not lib_data:
            result.mark_failed(f"Failed to create test library: status {lib_status}")
            return result
            
        library_id = lib_data['id']
        
        document_payload = get_test_document_payload(library_id)
        doc_status, doc_data, _ = tester.make_request('POST', '/documents', document_payload)
        
        if doc_status != 201 or not doc_data:
            result.mark_failed(f"Failed to create test document: status {doc_status}")
            return result
            
        document_id = doc_data['id']
        
        # List chunks for empty document
        status_code, response_data, response_time = tester.make_request('GET', f'/documents/{document_id}/chunks')
        
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


def test_list_chunks_with_data():
    """Test listing chunks after creating test data."""
    result = TestResult("list_chunks_data", "List chunks with test data")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_payload = get_test_library_payload()
        lib_status, lib_data, _ = tester.make_request('POST', '/libraries', library_payload)
        
        if lib_status != 201 or not lib_data:
            result.mark_failed(f"Failed to create test library: status {lib_status}")
            return result
            
        library_id = lib_data['id']
        
        document_payload = get_test_document_payload(library_id)
        doc_status, doc_data, _ = tester.make_request('POST', '/documents', document_payload)
        
        if doc_status != 201 or not doc_data:
            result.mark_failed(f"Failed to create test document: status {doc_status}")
            return result
            
        document_id = doc_data['id']
        
        # Create a test chunk
        chunk_payload = CREATE_CHUNK_PAYLOAD.copy()
        chunk_payload['document_id'] = document_id
        chunk_status, chunk_data, _ = tester.make_request('POST', '/chunks', chunk_payload)
        
        if chunk_status != 201:
            result.mark_failed(f"Failed to create test chunk: status {chunk_status}")
            return result
            
        # Now list chunks
        status_code, response_data, response_time = tester.make_request('GET', f'/documents/{document_id}/chunks')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not isinstance(response_data, list):
            result.mark_failed(f"Expected list response, got {type(response_data).__name__}")
            return result
            
        if len(response_data) == 0:
            result.mark_failed("Expected at least one chunk in response")
            return result
            
        # Validate schema of first chunk
        first_chunk = response_data[0]
        schema_errors = tester.validate_schema(first_chunk, EXPECTED_CHUNK_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        # Validate all chunks belong to the document
        for chunk in response_data:
            if chunk['document_id'] != document_id:
                result.mark_failed(f"Chunk {chunk['id']} doesn't belong to document {document_id}")
                return result
                
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_list_chunks_nonexistent_document():
    """Test listing chunks for non-existent document."""
    result = TestResult("list_chunks_no_doc", "List chunks for non-existent document")
    tester = APITester(BASE_URL)
    
    try:
        fake_document_id = "550e8400-e29b-41d4-a716-446655440999"
        
        status_code, response_data, response_time = tester.make_request('GET', f'/documents/{fake_document_id}/chunks')
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all list chunks tests."""
    print_test_header("LIST CHUNKS TESTS")
    
    tests = [
        test_list_chunks_empty,
        test_list_chunks_with_data,
        test_list_chunks_nonexistent_document
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