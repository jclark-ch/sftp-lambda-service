#!/bin/bash
set -e

# Configuration
TEST_DIR="tests"
COVERAGE_THRESHOLD=80

# Function to display script usage
usage() {
    echo "Usage: $0 [unit|integration|all]"
    exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    usage
fi

# Validate the argument
case "$1" in
    unit|integration|all) TEST_TYPE=$1 ;;
    *) usage ;;
esac

echo "Setting up test environment..."
pip install -r requirements.txt
pip install pytest pytest-cov

echo "Running tests..."
if [ "$TEST_TYPE" == "unit" ] || [ "$TEST_TYPE" == "all" ]; then
    echo "Running unit tests..."
    pytest $TEST_DIR/test_lambda_function.py $TEST_DIR/test_secrets_manager.py --cov=src --cov-report=term-missing --cov-fail-under=$COVERAGE_THRESHOLD
fi

if [ "$TEST_TYPE" == "integration" ] || [ "$TEST_TYPE" == "all" ]; then
    echo "Running integration tests..."
    # Add your integration test command here
    # For example: pytest $TEST_DIR/test_integration.py
    echo "Integration tests not implemented yet."
fi

echo "All tests completed successfully!"