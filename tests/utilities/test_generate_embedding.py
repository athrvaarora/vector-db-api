#!/usr/bin/env python3
"""
Individual test script for POST /api/v1/embeddings (Generate Embedding)
Tests embedding generation functionality and error cases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import (
    BASE_URL, TEST_SCENARIOS, ERROR_TEST_CASES, EXPECTED_EMBEDDING_RESPONSE_SCHEMA,
    PERFORMANCE_TEST_CASES
)


def test_generate_embedding_simple():
    """Test generating embedding for simple text."""
    result = TestResult("generate_embedding_simple", "Generate embedding for simple text")
    tester = APITester(BASE_URL)
    
    try:
        payload = {"text": "Hello world"}
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/embeddings', payload
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate response schema
        schema_errors = tester.validate_schema(response_data, EXPECTED_EMBEDDING_RESPONSE_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        # Validate embedding properties
        embedding = response_data.get('embedding')
        if not isinstance(embedding, list):
            result.mark_failed("Embedding should be a list")
            return result
            
        if len(embedding) == 0:
            result.mark_failed("Embedding should not be empty")
            return result
            
        # Check that all values are numbers
        for i, val in enumerate(embedding):
            if not isinstance(val, (int, float)):
                result.mark_failed(f"Embedding value at index {i} is not a number: {type(val)}")
                return result
                
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_generate_embedding_long_text():
    """Test generating embedding for longer text."""
    result = TestResult("generate_embedding_long", "Generate embedding for longer text")
    tester = APITester(BASE_URL)
    
    try:
        payload = {
            "text": "This is a longer piece of text to test the embedding generation functionality with multiple words and sentences."
        }
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/embeddings', payload
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Validate embedding
        embedding = response_data.get('embedding')
        if not embedding or len(embedding) == 0:
            result.mark_failed("Expected non-empty embedding")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_generate_embedding_special_chars():
    """Test generating embedding for text with special characters."""
    result = TestResult("generate_embedding_special", "Generate embedding for text with special characters")
    tester = APITester(BASE_URL)
    
    try:
        payload = {
            "text": "Hello! How are you? I'm fine, thanks. Let's test @#$%^&*() characters."
        }
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/embeddings', payload
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Validate embedding exists
        embedding = response_data.get('embedding')
        if not embedding:
            result.mark_failed("Expected embedding in response")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_generate_embedding_missing_text():
    """Test generating embedding with missing text field."""
    result = TestResult("generate_embedding_missing", "Generate embedding with missing text")
    tester = APITester(BASE_URL)
    
    try:
        payload = {}  # Missing text field
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/embeddings', payload
        )
        
        if status_code not in [400, 422]:
            result.mark_failed(f"Expected status 400 or 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_generate_embedding_empty_text():
    """Test generating embedding with empty text."""
    result = TestResult("generate_embedding_empty", "Generate embedding with empty text")
    tester = APITester(BASE_URL)
    
    try:
        payload = {"text": ""}
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/embeddings', payload
        )
        
        if status_code not in [400, 422]:
            result.mark_failed(f"Expected status 400 or 422, got {status_code}", status_code, 422)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_generate_embedding_performance():
    """Test embedding generation performance."""
    result = TestResult("generate_embedding_perf", "Generate embedding performance test")
    tester = APITester(BASE_URL)
    
    try:
        payload = {"text": "Performance test text for embedding generation"}
        
        status_code, response_data, response_time = tester.make_request(
            'POST', '/embeddings', payload
        )
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Check response time (should be reasonable for local testing)
        max_time = 30.0  # 30 seconds max for embedding generation
        if response_time > max_time:
            result.mark_failed(f"Response time too slow: {response_time:.3f}s (expected < {max_time}s)")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_generate_embedding_consistency():
    """Test that same text produces consistent embeddings."""
    result = TestResult("generate_embedding_consistency", "Generate embedding consistency test")
    tester = APITester(BASE_URL)
    
    try:
        payload = {"text": "Consistency test text"}
        
        # Generate embedding twice
        status1, response1, time1 = tester.make_request('POST', '/embeddings', payload)
        status2, response2, time2 = tester.make_request('POST', '/embeddings', payload)
        
        if status1 != 200 or status2 != 200:
            result.mark_failed(f"One of the requests failed: {status1}, {status2}")
            return result
            
        embedding1 = response1.get('embedding', [])
        embedding2 = response2.get('embedding', [])
        
        if len(embedding1) != len(embedding2):
            result.mark_failed("Embeddings have different lengths")
            return result
            
        # Check if embeddings are similar (allowing for small floating point differences)
        if len(embedding1) > 0:
            differences = [abs(a - b) for a, b in zip(embedding1, embedding2)]
            max_diff = max(differences) if differences else 0
            
            # Allow for small floating point differences
            if max_diff > 0.001:
                result.mark_failed(f"Embeddings differ too much: max difference {max_diff}")
                return result
                
        result.mark_passed(status1, time1, response1)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all generate embedding tests."""
    print_test_header("GENERATE EMBEDDING TESTS")
    
    tests = [
        test_generate_embedding_simple,
        test_generate_embedding_long_text,
        test_generate_embedding_special_chars,
        test_generate_embedding_missing_text,
        test_generate_embedding_empty_text,
        test_generate_embedding_performance,
        test_generate_embedding_consistency
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