# Vector Database API - Library Endpoints Test Suite

Comprehensive unit tests for all library-related API endpoints following industry standards.

## 📋 Test Coverage

### Endpoints Tested

| Endpoint | Method | Test Script | Coverage |
|----------|--------|------------|----------|
| `/api/v1/libraries` | GET | `test_list_libraries.py` | ✅ Complete |
| `/api/v1/libraries` | POST | `test_create_library.py` | ✅ Complete |
| `/api/v1/libraries/{id}` | GET | `test_get_library.py` | ✅ Complete |
| `/api/v1/libraries/{id}` | PUT | `test_update_library.py` | ✅ Complete |
| `/api/v1/libraries/{id}` | DELETE | `test_delete_library.py` | ✅ Complete |
| `/api/v1/libraries/{id}/stats` | GET | `test_get_library_stats.py` | ✅ Complete |

### Test Categories

- ✅ **Happy Path Tests** - Valid requests with expected responses
- ✅ **Error Handling** - Invalid UUIDs, missing data, non-existent resources
- ✅ **Data Validation** - Schema validation, type checking, field validation
- ✅ **Edge Cases** - Empty responses, duplicate operations, cascade effects
- ✅ **Performance** - Response time validation
- ✅ **Consistency** - Multiple calls return same results

## 🚀 Quick Start

### 1. Setup Test Environment
```bash
# Install test dependencies
python3 tests/libraries/setup_tests.py
```

### 2. Run All Tests
```bash
# Comprehensive test suite (starts backend automatically)
python3 tests/libraries/run_all_tests.py
```

### 3. Run Individual Tests
```bash
# Test specific endpoint
python3 tests/libraries/test_create_library.py
python3 tests/libraries/test_list_libraries.py
python3 tests/libraries/test_get_library.py
python3 tests/libraries/test_update_library.py
python3 tests/libraries/test_delete_library.py
python3 tests/libraries/test_get_library_stats.py
```

## 📊 Test Output

### Table Format
```
================================================================================
TEST SUMMARY
================================================================================
Test Name                 Status   Status Code  Response Time  Description
------------------------- -------- ------------ -------------- --------------------
create_library_valid      PASS     201          0.045s         Create library with valid data
list_libraries_empty       PASS     200          0.023s         List libraries (may be empty)
get_library_valid          PASS     200          0.032s         Get library with valid ID
update_library_valid       PASS     200          0.041s         Update library with valid data
delete_library_valid       PASS     204          0.028s         Delete library with valid ID
get_stats_valid            PASS     200          0.034s         Get library stats with valid ID

Total Tests: 25
Passed: 25
Failed: 0
🎉 All tests passed!
```

### Detailed Results
Each test provides:
- ✅/❌ **Status** - Pass/Fail indicator
- 🕒 **Response Time** - API response time in seconds
- 📊 **Status Code** - HTTP status code validation
- 🔍 **Schema Validation** - Response structure validation
- 📝 **Error Details** - Detailed failure information when tests fail

## 📁 File Structure

```
tests/libraries/
├── README.md                    # This documentation
├── setup_tests.py              # Test environment setup
├── run_all_tests.py            # Comprehensive test runner
├── test_data.py                # Test data and expected responses
├── test_utils.py               # Utility functions and test framework
├── test_create_library.py      # POST /libraries tests
├── test_list_libraries.py      # GET /libraries tests
├── test_get_library.py         # GET /libraries/{id} tests
├── test_update_library.py      # PUT /libraries/{id} tests
├── test_delete_library.py      # DELETE /libraries/{id} tests
└── test_get_library_stats.py   # GET /libraries/{id}/stats tests
```

## 🧪 Test Framework Features

### Industry Standard Practices
- **Isolated Tests** - Each test is independent and can run standalone
- **Proper Setup/Teardown** - Clean environment for each test
- **Comprehensive Assertions** - Schema validation, data verification
- **Error Handling** - Graceful handling of API and network errors
- **Performance Monitoring** - Response time tracking and validation

### Backend Management
- **Automatic Startup** - Test runner starts backend automatically
- **Health Checks** - Waits for backend to be ready before testing
- **Graceful Shutdown** - Proper cleanup after test completion
- **Process Management** - Handles backend lifecycle reliably

### Reporting
- **Colored Output** - Easy-to-read success/failure indicators
- **Detailed Logs** - Comprehensive error messages and debugging info
- **Summary Tables** - Overview of all test results
- **Performance Stats** - Response time analysis
- **Exit Codes** - Proper exit codes for CI/CD integration

## 🔧 Configuration

### Test Data (`test_data.py`)
- **Predefined Payloads** - Consistent test data across all tests
- **Expected Schemas** - Response validation structures
- **Error Test Cases** - Invalid data for error testing
- **Configurable URLs** - Easy environment switching

### Utilities (`test_utils.py`)
- **HTTP Client** - Robust request handling with timeouts
- **Schema Validation** - Recursive validation of response structures
- **Result Formatting** - Professional test output formatting
- **Backend Management** - Server lifecycle management

## 🎯 Usage Examples

### Running Specific Test Categories
```bash
# Test only creation functionality
python3 tests/libraries/test_create_library.py

# Test only error handling
python3 tests/libraries/test_get_library.py  # Includes 404, invalid UUID tests
```

### Integration with CI/CD
```bash
# Run tests and get exit code for CI
python3 tests/libraries/run_all_tests.py
echo "Exit code: $?"
```

### Custom Test Data
Modify `test_data.py` to use your own test scenarios:
```python
CREATE_LIBRARY_PAYLOAD = {
    "metadata": {
        "name": "Your Custom Library",
        "description": "Custom test library",
        # ... other fields
    }
}
```

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill existing processes
pkill -f uvicorn
```

### Tests Fail with Connection Errors
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check test setup
python3 tests/libraries/setup_tests.py
```

### Import Errors
```bash
# Install missing dependencies
pip install -r tests/requirements.txt

# Verify Python path
export PYTHONPATH=/path/to/your/project:$PYTHONPATH
```

## 📈 Future Enhancements

- **Load Testing** - Performance tests with multiple concurrent requests
- **Integration Tests** - Cross-endpoint workflow testing
- **Mock Data Generation** - Dynamic test data generation
- **Test Reports** - HTML/XML test reports for CI/CD
- **Database Tests** - Persistence and data integrity tests

## 🤝 Contributing

When adding new tests:
1. Follow the existing naming convention: `test_{endpoint}_{scenario}.py`
2. Use the provided `TestResult` and `APITester` classes
3. Include both positive and negative test cases
4. Add comprehensive documentation
5. Update this README with new test coverage

---

**Ready to test!** 🚀 Start with `python3 tests/libraries/setup_tests.py` then run `python3 tests/libraries/run_all_tests.py`