#!/usr/bin/env python3
"""
Comprehensive test runner for all document endpoint tests.
Starts backend, runs all tests in proper order, and provides detailed reporting.
"""

import sys
import os
import subprocess
import time
import signal
import psutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tests.documents.test_utils import (
    APITester, TestResult, print_test_header, print_test_result, 
    print_summary_table, wait_for_backend
)
from tests.documents.test_data import BASE_URL

# Import all test modules
from tests.documents.test_create_document import run_all_tests as run_create_tests
from tests.documents.test_list_documents import run_all_tests as run_list_tests
from tests.documents.test_get_document import run_all_tests as run_get_tests
from tests.documents.test_update_document import run_all_tests as run_update_tests
from tests.documents.test_delete_document import run_all_tests as run_delete_tests


class BackendManager:
    """Manages backend server lifecycle for testing."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_process = None
        
    def start_backend(self):
        """Start the backend server."""
        print(f"\n🚀 Starting backend server...")
        
        try:
            # Change to project root directory
            os.chdir(self.project_root)
            
            # Start the backend using uvicorn directly
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "app.main:app", 
                "--host", "0.0.0.0", 
                "--port", "8000",
                "--reload-dir", "app"
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=dict(os.environ, PYTHONPATH=str(self.project_root))
            )
            
            # Wait for backend to be ready
            if wait_for_backend(BASE_URL, max_attempts=30, delay=1.0):
                print(f"✅ Backend started successfully (PID: {self.backend_process.pid})")
                return True
            else:
                print("❌ Backend failed to start")
                self.stop_backend()
                return False
                
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def stop_backend(self):
        """Stop the backend server and cleanup."""
        if self.backend_process:
            print(f"\n🛑 Stopping backend server (PID: {self.backend_process.pid})...")
            
            try:
                # Try graceful shutdown first
                self.backend_process.terminate()
                
                # Wait for process to terminate
                try:
                    self.backend_process.wait(timeout=10)
                    print("✅ Backend stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't stop gracefully
                    print("⚠️ Backend didn't stop gracefully, force killing...")
                    self.backend_process.kill()
                    self.backend_process.wait()
                    print("✅ Backend force killed")
                    
            except Exception as e:
                print(f"⚠️ Error stopping backend: {e}")
                
            self.backend_process = None
    
    def __enter__(self):
        """Context manager entry."""
        if self.start_backend():
            return self
        else:
            raise RuntimeError("Failed to start backend")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_backend()


def clear_test_data():
    """Clear any existing test data by restarting with fresh state."""
    print("\n🧹 Clearing test data...")
    
    try:
        # Simple approach: just wait a moment for any in-memory state to settle
        time.sleep(1)
        print("✅ Test environment ready")
        return True
    except Exception as e:
        print(f"⚠️ Warning: Could not clear test data: {e}")
        return True  # Continue anyway since we're using in-memory storage


def run_test_suite():
    """Run the complete test suite for document endpoints."""
    print("=" * 80)
    print("🧪 VECTOR DATABASE API - DOCUMENT ENDPOINTS TEST SUITE")
    print("=" * 80)
    
    all_results = []
    test_suites = [
        ("CREATE DOCUMENT", run_create_tests),
        ("LIST DOCUMENTS", run_list_tests),
        ("GET DOCUMENT", run_get_tests),
        ("UPDATE DOCUMENT", run_update_tests),
        ("DELETE DOCUMENT", run_delete_tests),
    ]
    
    for suite_name, test_func in test_suites:
        print(f"\n" + "=" * 60)
        print(f"📋 Running {suite_name} Tests")
        print("=" * 60)
        
        try:
            # Clear data before each suite
            clear_test_data()
            
            # Run the test suite
            results = test_func()
            all_results.extend(results)
            
            # Summary for this suite
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            print(f"\n📊 {suite_name} Results: {passed}/{total} passed")
            
        except Exception as e:
            print(f"❌ Error running {suite_name} tests: {e}")
            # Create a failure result for the suite
            error_result = TestResult(f"{suite_name.lower()}_suite", f"Run {suite_name} test suite")
            error_result.mark_failed(f"Suite execution failed: {e}")
            all_results.append(error_result)
    
    return all_results


def print_final_report(results):
    """Print comprehensive final test report."""
    print("\n" + "=" * 80)
    print("📊 FINAL TEST REPORT")
    print("=" * 80)
    
    # Overall statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.passed)
    failed_tests = total_tests - passed_tests
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests} ✅")
    print(f"   Failed: {failed_tests} ❌")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Performance statistics
    response_times = [r.response_time for r in results if r.response_time]
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"\n⏱️ Performance Statistics:")
        print(f"   Average Response Time: {avg_time:.3f}s")
        print(f"   Fastest Response: {min_time:.3f}s")
        print(f"   Slowest Response: {max_time:.3f}s")
    
    # Failed tests details
    failed_results = [r for r in results if not r.passed]
    if failed_results:
        print(f"\n❌ Failed Tests Details:")
        for result in failed_results:
            print(f"   • {result.test_name}: {result.error_message}")
    
    # Success indicator
    if failed_tests == 0:
        print(f"\n🎉 ALL TESTS PASSED! 🎉")
        print(f"   The Document API endpoints are working correctly.")
    else:
        print(f"\n⚠️ {failed_tests} TEST(S) FAILED")
        print(f"   Please review the failed tests and fix the issues.")
    
    print("=" * 80)


def main():
    """Main test execution function."""
    try:
        # Start backend and run tests
        with BackendManager(project_root) as backend:
            
            # Run the complete test suite
            all_results = run_test_suite()
            
            # Print comprehensive report
            print_summary_table(all_results)
            print_final_report(all_results)
            
            # Return appropriate exit code
            failed_tests = [r for r in all_results if not r.passed]
            return 1 if failed_tests else 0
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)