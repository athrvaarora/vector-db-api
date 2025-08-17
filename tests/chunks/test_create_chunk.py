#!/usr/bin/env python3
"""
Individual test script for POST /api/v1/chunks (Create Chunk)
Tests chunk creation with valid data and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import BASE_URL, CREATE_CHUNK_PAYLOAD, EXPECTED_CHUNK_SCHEMA, get_test_library_payload, get_test_document_payload


def test_create_chunk_valid():
    """Test creating a chunk with valid data."""
    result = TestResult("create_chunk_valid", "Create chunk with valid data")
    tester = APITester(BASE_URL)
    
    try:
        # Create test library first
        library_payload = get_test_library_payload()
        lib_status, lib_data, _ = tester.make_request('POST', '/libraries', library_payload)
        
        if lib_status != 201 or not lib_data:
            result.mark_failed(f"Failed to create test library: status {lib_status}")
            return result
            
        library_id = lib_data['id']
        
        # Create test document
        document_payload = get_test_document_payload(library_id)
        doc_status, doc_data, _ = tester.make_request('POST', '/documents', document_payload)
        
        if doc_status != 201 or not doc_data:
            result.mark_failed(f"Failed to create test document: status {doc_status}")
            return result
            
        document_id = doc_data['id']
        
        # Update the payload with the actual document ID
        chunk_payload = CREATE_CHUNK_PAYLOAD.copy()
        chunk_payload['document_id'] = document_id
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/chunks', chunk_payload
        )
        
        if status_code != 201:
            result.mark_failed(f"Expected status 201, got {status_code}", status_code, 201)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate response schema
        schema_errors = tester.validate_schema(response_data, EXPECTED_CHUNK_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        # Validate specific fields
        if response_data['text'] != chunk_payload['text']:
            result.mark_failed("Chunk text doesn't match payload")
            return result
            
        if response_data['document_id'] != document_id:
            result.mark_failed("Chunk document_id doesn't match payload")
            return result
            
        # Validate embedding
        if len(response_data['embedding']) != len(chunk_payload['embedding']):
            result.mark_failed("Chunk embedding length doesn't match payload")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_create_chunk_missing_fields():
    """Test creating a chunk with missing required fields."""
    result = TestResult("create_chunk_missing", "Create chunk with missing fields")
    tester = APITester(BASE_URL)
    
    try:
        invalid_payload = {"text": ""}  # Missing embedding, metadata, document_id
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/chunks', invalid_payload
        )
        
        if status_code not in [400, 422]:
            result.mark_failed(f"Expected status 400 or 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_create_chunk_nonexistent_document():
    """Test creating a chunk with non-existent document."""
    result = TestResult("create_chunk_no_doc", "Create chunk with non-existent document")
    tester = APITester(BASE_URL)
    
    try:
        chunk_payload = CREATE_CHUNK_PAYLOAD.copy()
        chunk_payload['document_id'] = "550e8400-e29b-41d4-a716-446655440999"  # Non-existent
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/chunks', chunk_payload
        )
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_create_chunk_invalid_embedding():
    """Test creating a chunk with invalid embedding."""
    result = TestResult("create_chunk_bad_embed", "Create chunk with invalid embedding")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies first
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
        
        # Create chunk with empty embedding
        chunk_payload = CREATE_CHUNK_PAYLOAD.copy()
        chunk_payload['document_id'] = document_id
        chunk_payload['embedding'] = []  # Invalid empty embedding
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/chunks', chunk_payload
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
    """Run all create chunk tests."""
    print_test_header("CREATE CHUNK TESTS")
    
    tests = [
        test_create_chunk_valid,
        test_create_chunk_missing_fields,
        test_create_chunk_nonexistent_document,
        test_create_chunk_invalid_embedding
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