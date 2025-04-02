# Test Suite for TF Code Analyzer Agent

This directory contains the test suite for the TF Code Analyzer Agent, including REST API tests and AGP Gateway tests.

## Prerequisites

1. Python 3.11 or higher
2. AGP API package (for AGP Gateway tests)
3. Test dependencies

## Setup

1. Install the package in development mode:
```bash
pip install -e .
```

2. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

3. Set up environment variables (optional, defaults provided):
```bash
export TF_CODE_ANALYZER_HOST=127.0.0.1
export TF_CODE_ANALYZER_PORT=8133
export GITHUB_REPO_URL=https://github.com/test/repo
export GITHUB_TOKEN=test_token
export GITHUB_BRANCH=main
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Suites

1. REST API Tests:
```bash
pytest tests/rest/test_endpoints.py
```

2. AGP Gateway Tests:
```bash
pytest tests/agp/test_gateway.py
```

### Run Tests with Coverage Report
```bash
pytest --cov=app tests/
```

## Test Structure

### REST API Tests (`tests/rest/test_endpoints.py`)
- Health check endpoint tests
- Main runs endpoint tests
- Error handling tests
- Timeout tests
- Input validation tests

### AGP Gateway Tests (`tests/agp/test_gateway.py`)
- Gateway connection tests
- Message exchange tests
- Error handling tests
- Connection retry tests
- Timeout tests

### Test Configuration (`tests/conftest.py`)
- Common fixtures
- Environment setup
- Shared test data

## Notes

1. AGP Gateway tests will be skipped if the AGP API package is not available
2. Tests use mocking to avoid actual network calls
3. Environment variables can be overridden for different test environments
4. Coverage reports help identify untested code paths

## Troubleshooting

1. If AGP Gateway tests are skipped:
   - Ensure the AGP API package is installed
   - Check if the package is in your Python path

2. If tests fail to connect:
   - Verify the agent service is running
   - Check environment variables
   - Ensure correct host and port configuration

3. For coverage issues:
   - Run with `--cov=app` to see detailed coverage report
   - Add missing test cases for uncovered code 