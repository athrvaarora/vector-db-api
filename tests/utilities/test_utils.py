"""
Utility functions for library endpoint testing.
Provides common functionality for HTTP requests, validation, and result formatting.
"""

import json
import time
import requests
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

class TestResult:
    """Container for test results with formatting capabilities."""
    
    def __init__(self, test_name: str, description: str):
        self.test_name = test_name
        self.description = description
        self.passed = False
        self.status_code = None
        self.expected_status = None
        self.response_time = None
        self.error_message = None
        self.response_data = None
        
    def mark_passed(self, status_code: int, response_time: float, response_data: Any = None):
        self.passed = True
        self.status_code = status_code
        self.response_time = response_time
        self.response_data = response_data
        
    def mark_failed(self, error_message: str, status_code: int = None, expected_status: int = None):
        self.passed = False
        self.error_message = error_message
        self.status_code = status_code
        self.expected_status = expected_status

class APITester:
    """Main class for API testing with HTTP client and validation."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def make_request(self, method: str, endpoint: str, payload: Dict = None, 
                    params: Dict = None) -> Tuple[int, Any, float]:
        """Make HTTP request and return status code, response data, and response time."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=payload, timeout=self.timeout)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=payload, timeout=self.timeout)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response_time = time.time() - start_time
            
            # Try to parse JSON, fall back to text if not JSON
            try:
                response_data = response.json() if response.content else None
            except json.JSONDecodeError:
                response_data = response.text if response.content else None
                
            return response.status_code, response_data, response_time
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return None, str(e), response_time

    def validate_schema(self, data: Dict, expected_schema: Dict) -> List[str]:
        """Validate response data against expected schema."""
        errors = []
        
        def validate_field(obj, schema, path=""):
            if isinstance(schema, dict):
                if not isinstance(obj, dict):
                    errors.append(f"Expected object at {path}, got {type(obj).__name__}")
                    return
                for key, expected_type in schema.items():
                    field_path = f"{path}.{key}" if path else key
                    if key not in obj:
                        errors.append(f"Missing required field: {field_path}")
                    else:
                        validate_field(obj[key], expected_type, field_path)
            elif isinstance(schema, tuple):
                # Multiple allowed types
                if not any(isinstance(obj, t) for t in schema):
                    type_names = [t.__name__ for t in schema]
                    errors.append(f"Expected one of {type_names} at {path}, got {type(obj).__name__}")
            elif isinstance(schema, type):
                if not isinstance(obj, schema):
                    errors.append(f"Expected {schema.__name__} at {path}, got {type(obj).__name__}")
        
        validate_field(data, expected_schema)
        return errors

def print_test_header(title: str):
    """Print formatted test section header."""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{title:^60}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

def print_test_result(result: TestResult):
    """Print formatted individual test result."""
    status_icon = f"{Fore.GREEN}✓" if result.passed else f"{Fore.RED}✗"
    status_text = f"{Fore.GREEN}PASS" if result.passed else f"{Fore.RED}FAIL"
    
    print(f"{status_icon} {result.test_name:<25} {status_text}")
    print(f"  Description: {result.description}")
    
    if result.response_time:
        print(f"  Response Time: {result.response_time:.3f}s")
        
    if result.status_code:
        color = Fore.GREEN if result.passed else Fore.RED
        print(f"  Status Code: {color}{result.status_code}")
        
    if result.expected_status and result.status_code != result.expected_status:
        print(f"  Expected: {Fore.YELLOW}{result.expected_status}")
        
    if not result.passed and result.error_message:
        print(f"  Error: {Fore.RED}{result.error_message}")
        
    print()

def print_summary_table(results: List[TestResult]):
    """Print formatted summary table of all test results."""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}TEST SUMMARY")
    print(f"{Fore.CYAN}{'='*80}")
    
    # Table header
    print(f"{'Test Name':<25} {'Status':<8} {'Status Code':<12} {'Response Time':<14} {'Description'}")
    print(f"{'-'*25} {'-'*8} {'-'*12} {'-'*14} {'-'*20}")
    
    passed_count = 0
    failed_count = 0
    
    for result in results:
        status_text = f"{Fore.GREEN}PASS" if result.passed else f"{Fore.RED}FAIL"
        status_code = str(result.status_code) if result.status_code else "N/A"
        response_time = f"{result.response_time:.3f}s" if result.response_time else "N/A"
        
        print(f"{result.test_name:<25} {status_text:<8} {status_code:<12} {response_time:<14} {result.description[:30]}")
        
        if result.passed:
            passed_count += 1
        else:
            failed_count += 1
    
    print(f"\n{Fore.CYAN}Total Tests: {len(results)}")
    print(f"{Fore.GREEN}Passed: {passed_count}")
    print(f"{Fore.RED}Failed: {failed_count}")
    
    if failed_count == 0:
        print(f"{Fore.GREEN}🎉 All tests passed!")
    else:
        print(f"{Fore.YELLOW}⚠️  {failed_count} test(s) failed")
    
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

def wait_for_backend(base_url: str, max_attempts: int = 30, delay: float = 1.0) -> bool:
    """Wait for backend to be ready."""
    print(f"{Fore.YELLOW}Waiting for backend to be ready...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"{Fore.GREEN}✓ Backend is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
            
        if attempt < max_attempts - 1:
            print(f"{Fore.YELLOW}Attempt {attempt + 1}/{max_attempts} failed, retrying in {delay}s...")
            time.sleep(delay)
    
    print(f"{Fore.RED}✗ Backend failed to start after {max_attempts} attempts")
    return False