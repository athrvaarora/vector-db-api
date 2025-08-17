#!/usr/bin/env python3
"""
Individual test script for GET /api/v1/health (Health Check)
Tests system health monitoring functionality.
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_utils import APITester, TestResult, print_test_header, print_test_result, print_summary_table
from test_data import (
    BASE_URL, EXPECTED_HEALTH_RESPONSE_SCHEMA, EXPECTED_HEALTH_STATUSES,
    TEST_SCENARIOS, PERFORMANCE_THRESHOLDS
)


def test_health_check_basic():
    """Test basic health check functionality."""
    result = TestResult("health_check_basic", "Basic health check")
    tester = APITester(BASE_URL)
    
    try:
        status_code, response_data, response_time = tester.make_request('GET', '/health')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        if not response_data:
            result.mark_failed("No response data received")
            return result
            
        # Validate response schema
        schema_errors = tester.validate_schema(response_data, EXPECTED_HEALTH_RESPONSE_SCHEMA)
        if schema_errors:
            result.mark_failed(f"Schema validation failed: {', '.join(schema_errors)}")
            return result
            
        # Validate health status
        status = response_data.get('status', '').lower()
        if status not in EXPECTED_HEALTH_STATUSES:
            result.mark_failed(f"Unexpected health status: {status}")
            return result
            
        # Validate service field if present
        service = response_data.get('service')
        if service and not isinstance(service, str):
            result.mark_failed("Service field should be a string")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_health_check_performance():
    """Test health check performance."""
    result = TestResult("health_check_perf", "Health check performance test")
    tester = APITester(BASE_URL)
    
    try:
        status_code, response_data, response_time = tester.make_request('GET', '/health')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Health checks should be fast
        max_time = PERFORMANCE_THRESHOLDS['max_response_time']
        if response_time > max_time:
            result.mark_failed(f"Health check too slow: {response_time:.3f}s (expected < {max_time}s)")
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_health_check_consistency():
    """Test health check consistency across multiple calls."""
    result = TestResult("health_check_consistency", "Health check consistency test")
    tester = APITester(BASE_URL)
    
    try:
        responses = []
        
        # Make multiple health check requests
        for i in range(3):
            status_code, response_data, response_time = tester.make_request('GET', '/health')
            
            if status_code != 200:
                result.mark_failed(f"Request {i+1} failed with status {status_code}")
                return result
                
            responses.append(response_data)
            
        # Validate consistency
        first_response = responses[0]
        for i, response in enumerate(responses[1:], 1):
            # Status should be consistent
            if response.get('status') != first_response.get('status'):
                result.mark_failed(f"Status inconsistent in response {i+1}")
                return result
                
            # Version should be consistent (if present)
            if (response.get('version') and first_response.get('version') and 
                response.get('version') != first_response.get('version')):
                result.mark_failed(f"Version inconsistent in response {i+1}")
                return result
                
        result.mark_passed(200, response_time, first_response)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_health_check_version():
    """Test health check version information."""
    result = TestResult("health_check_version", "Health check version validation")
    tester = APITester(BASE_URL)
    
    try:
        status_code, response_data, response_time = tester.make_request('GET', '/health')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Check version if present
        version = response_data.get('version')
        if version is not None:
            if not isinstance(version, str):
                result.mark_failed(f"Version should be a string, got {type(version)}")
                return result
                
            if len(version.strip()) == 0:
                result.mark_failed("Version should not be empty")
                return result
                
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_health_check_service():
    """Test health check service information."""
    result = TestResult("health_check_service", "Health check service validation")
    tester = APITester(BASE_URL)
    
    try:
        status_code, response_data, response_time = tester.make_request('GET', '/health')
        
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        # Check service if present
        service = response_data.get('service')
        if service is not None:
            if not isinstance(service, str):
                result.mark_failed(f"Service should be a string, got {type(service)}")
                return result
                
            if len(service.strip()) == 0:
                result.mark_failed("Service should not be empty")
                return result
                
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def test_health_check_no_auth_required():
    """Test that health check doesn't require authentication."""
    result = TestResult("health_check_no_auth", "Health check requires no authentication")
    tester = APITester(BASE_URL)
    
    try:
        # Health endpoint should work without any authentication
        status_code, response_data, response_time = tester.make_request('GET', '/health')
        
        if status_code == 401:
            result.mark_failed("Health check should not require authentication")
            return result
            
        if status_code != 200:
            result.mark_failed(f"Expected status 200, got {status_code}", status_code, 200)
            return result
            
        result.mark_passed(status_code, response_time, response_data)
        return result
        
    except Exception as e:
        result.mark_failed(f"Exception occurred: {str(e)}")
        return result


def run_all_tests():
    """Run all health check tests."""
    print_test_header("HEALTH CHECK TESTS")
    
    tests = [
        test_health_check_basic,
        test_health_check_performance,
        test_health_check_consistency,
        test_health_check_version,
        test_health_check_service,
        test_health_check_no_auth_required
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