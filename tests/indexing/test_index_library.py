#!/usr/bin/env python3
"""
Individual test script for POST /api/v1/libraries/{library_id}/index (Index Library)
Tests vector indexing with different algorithms and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import (
    BASE_URL, TEST_SCENARIOS, ERROR_TEST_CASES, EXPECTED_INDEX_RESPONSE_SCHEMA,
    get_test_library_payload, get_test_document_payload, get_test_chunk_payload
)


def test_index_library_flat():
    """Test indexing library with Flat algorithm."""
    result = TestResult("index_library_flat", "Index library with Flat algorithm")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_id = create_test_library_with_chunks(tester)
        if not library_id:
            result.mark_failed("Failed to create test dependencies")
            return result
        
        # Index the library with Flat algorithm
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{library_id}/index?index_type=flat'
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate response schema
        schema_errors = tester.validate_schema(response_data, EXPECTED_INDEX_RESPONSE_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        # Validate message contains algorithm info
        message = response_data.get('message', '')
        if 'flat' not in message.lower():
            result.mark_failed(f"Expected message to mention 'flat' algorithm, got: {message}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_index_library_lsh():
    """Test indexing library with LSH algorithm."""
    result = TestResult("index_library_lsh", "Index library with LSH algorithm")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_id = create_test_library_with_chunks(tester)
        if not library_id:
            result.mark_failed("Failed to create test dependencies")
            return result
        
        # Index the library with LSH algorithm  
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{library_id}/index?index_type=rp_lsh'
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Validate message contains algorithm info
        message = response_data.get('message', '')
        if 'rp_lsh' not in message.lower():
            result.mark_failed(f"Expected message to mention 'rp_lsh' algorithm, got: {message}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_index_library_hierarchical():
    """Test indexing library with Hierarchical algorithm."""
    result = TestResult("index_library_hierarchical", "Index library with Hierarchical algorithm")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_id = create_test_library_with_chunks(tester)
        if not library_id:
            result.mark_failed("Failed to create test dependencies")
            return result
        
        # Index the library with Hierarchical algorithm
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{library_id}/index?index_type=hierarchical'
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Validate message contains algorithm info
        message = response_data.get('message', '')
        if 'hierarchical' not in message.lower():
            result.mark_failed(f"Expected message to mention 'hierarchical' algorithm, got: {message}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_index_library_default():
    """Test indexing library with default algorithm."""
    result = TestResult("index_library_default", "Index library with default algorithm")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_id = create_test_library_with_chunks(tester)
        if not library_id:
            result.mark_failed("Failed to create test dependencies")
            return result
        
        # Index the library with no algorithm specified (should use default)
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{library_id}/index'
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Should use a default algorithm (flat)
        message = response_data.get('message', '')
        if 'flat' not in message.lower():
            result.mark_failed(f"Expected default algorithm 'flat' in message, got: {message}")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_index_nonexistent_library():
    """Test indexing non-existent library."""
    result = TestResult("index_library_404", "Index non-existent library")
    tester = APITester(BASE_URL)
    
    try:
        fake_library_id = "550e8400-e29b-41d4-a716-446655440999"
        
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{fake_library_id}/index?index_type=flat'
        )
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_index_invalid_library_uuid():
    """Test indexing with invalid library UUID."""
    result = TestResult("index_library_invalid", "Index library with invalid UUID")
    tester = APITester(BASE_URL)
    
    try:
        invalid_library_id = "invalid-uuid-format"
        
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{invalid_library_id}/index?index_type=flat'
        )
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_index_invalid_algorithm():
    """Test indexing with invalid algorithm."""
    result = TestResult("index_library_bad_algo", "Index library with invalid algorithm")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_id = create_test_library_with_chunks(tester)
        if not library_id:
            result.mark_failed("Failed to create test dependencies")
            return result
        
        # Try with invalid algorithm
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{library_id}/index?index_type=invalid_algorithm'
        )
        
        if status_code not in [400, 422]:
            result.mark_failed(f"Expected status 400 or 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def create_test_library_with_chunks(tester):
    """Helper to create a library with documents and chunks for indexing tests."""
    try:
        # Create library
        library_payload = get_test_library_payload()
        lib_status, lib_data, _ = tester.make_request('POST', '/libraries', library_payload)
        
        if lib_status != 201 or not lib_data:
            return None
            
        library_id = lib_data['id']
        
        # Create document
        document_payload = get_test_document_payload(library_id)
        doc_status, doc_data, _ = tester.make_request('POST', '/documents', document_payload)
        
        if doc_status != 201 or not doc_data:
            return None
            
        document_id = doc_data['id']
        
        # Create multiple chunks for better indexing test
        for i in range(3):
            chunk_payload = get_test_chunk_payload(document_id)
            chunk_payload['text'] = f"Test chunk {i+1} for indexing operations with sample content."
            chunk_status, chunk_data, _ = tester.make_request('POST', '/chunks', chunk_payload)
            
            if chunk_status != 201:
                return None
                
        return library_id
        
    except Exception:
        return None


def run_all_tests():
    """Run all index library tests."""
    print_test_header("INDEX LIBRARY TESTS")
    
    tests = [
        test_index_library_flat,
        test_index_library_lsh,
        test_index_library_hierarchical,
        test_index_library_default,
        test_index_nonexistent_library,
        test_index_invalid_library_uuid,
        test_index_invalid_algorithm
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