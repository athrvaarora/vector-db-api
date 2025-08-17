#!/usr/bin/env python3
"""
Individual test script for POST /api/v1/libraries/{library_id}/search (Search Library)
Tests vector search functionality with various parameters and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import (
    BASE_URL, TEST_SCENARIOS, ERROR_TEST_CASES, EXPECTED_SEARCH_RESPONSE_SCHEMA,
    EXPECTED_SEARCH_RESULT_SCHEMA, SAMPLE_SEARCH_EMBEDDING,
    get_test_library_payload, get_test_document_payload, get_test_chunk_payload
)


def test_search_library_basic():
    """Test basic search in library."""
    result = TestResult("search_library_basic", "Basic search in library")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_id = create_test_library_with_indexed_chunks(tester)
        if not library_id:
            result.mark_failed("Failed to create test dependencies")
            return result
        
        # Perform basic search
        payload = {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 5
        }
        
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{library_id}/search', payload
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate response schema
        schema_errors = tester.validate_schema(response_data, EXPECTED_SEARCH_RESPONSE_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        # Validate search results (response should be a list directly)
        if not isinstance(response_data, list):
            result.mark_failed("Expected response to be a list of search results")
            return result
            
        # Validate individual results if present
        for search_result in response_data:
            schema_errors = tester.validate_schema(search_result, EXPECTED_SEARCH_RESULT_SCHEMA)
            if schema_errors:
                result.mark_failed(f"Search result schema validation failed: {', '.join(schema_errors)}")
                return result
                
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_search_library_with_threshold():
    """Test search with similarity threshold."""
    result = TestResult("search_library_threshold", "Search with similarity threshold")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_id = create_test_library_with_indexed_chunks(tester)
        if not library_id:
            result.mark_failed("Failed to create test dependencies")
            return result
        
        # Search with similarity threshold
        payload = {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 10,
            "similarity_threshold": 0.5
        }
        
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{library_id}/search', payload
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Validate that all results meet the threshold
        for search_result in response_data:
            similarity = search_result.get('similarity_score', 0)
            if similarity < 0.5:
                result.mark_failed(f"Result similarity {similarity} below threshold 0.5")
                return result
                
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_search_library_with_filters():
    """Test search with metadata filters."""
    result = TestResult("search_library_filters", "Search with metadata filters")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_id = create_test_library_with_indexed_chunks(tester)
        if not library_id:
            result.mark_failed("Failed to create test dependencies")
            return result
        
        # Search with metadata filters
        payload = {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 5,
            "metadata_filters": {
                "language": "en"
            }
        }
        
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{library_id}/search', payload
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Validate that results match filters (if any results)
        for search_result in response_data:
            chunk_metadata = search_result.get('chunk', {}).get('metadata', {})
            if chunk_metadata.get('language') != 'en':
                result.mark_failed("Result doesn't match language filter")
                return result
                
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_search_nonexistent_library():
    """Test search in non-existent library."""
    result = TestResult("search_library_404", "Search non-existent library")
    tester = APITester(BASE_URL)
    
    try:
        fake_library_id = "550e8400-e29b-41d4-a716-446655440999"
        payload = {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 5
        }
        
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{fake_library_id}/search', payload
        )
        
        if status_code != 404:
            result.mark_failed(f"Expected status 404, got {status_code}", status_code, 404)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_search_invalid_library_uuid():
    """Test search with invalid library UUID."""
    result = TestResult("search_library_invalid", "Search with invalid library UUID")
    tester = APITester(BASE_URL)
    
    try:
        invalid_library_id = "invalid-uuid-format"
        payload = {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 5
        }
        
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{invalid_library_id}/search', payload
        )
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_search_missing_embedding():
    """Test search with missing embedding."""
    result = TestResult("search_missing_embedding", "Search with missing embedding")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_id = create_test_library_with_indexed_chunks(tester)
        if not library_id:
            result.mark_failed("Failed to create test dependencies")
            return result
        
        # Search without embedding
        payload = {
            "k": 5
        }
        
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{library_id}/search', payload
        )
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_search_invalid_k_value():
    """Test search with invalid k value."""
    result = TestResult("search_invalid_k", "Search with invalid k value")
    tester = APITester(BASE_URL)
    
    try:
        # Create test dependencies
        library_id = create_test_library_with_indexed_chunks(tester)
        if not library_id:
            result.mark_failed("Failed to create test dependencies")
            return result
        
        # Search with k=0
        payload = {
            "embedding": SAMPLE_SEARCH_EMBEDDING,
            "k": 0
        }
        
        status_code, response_data, response_time = tester.make_request(
            'POST', f'/libraries/{library_id}/search', payload
        )
        
        if status_code != 422:
            result.mark_failed(f"Expected status 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def create_test_library_with_indexed_chunks(tester):
    """Helper to create an indexed library with chunks for search tests."""
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
        
        # Create multiple chunks with different content
        for i in range(5):
            chunk_payload = get_test_chunk_payload(document_id, f" variant {i+1}")
            chunk_status, chunk_data, _ = tester.make_request('POST', '/chunks', chunk_payload)
            
            if chunk_status != 201:
                return None
        
        # Index the library (required for search to work)
        index_status, index_data, _ = tester.make_request('POST', f'/libraries/{library_id}/index?index_type=flat')
        
        # Indexing is required for search to work
        if index_status != 200:
            return None
        
        return library_id
        
    except Exception:
        return None


def run_all_tests():
    """Run all search library tests."""
    print_test_header("SEARCH LIBRARY TESTS")
    
    tests = [
        test_search_library_basic,
        test_search_library_with_threshold,
        test_search_library_with_filters,
        test_search_nonexistent_library,
        test_search_invalid_library_uuid,
        test_search_missing_embedding,
        test_search_invalid_k_value
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