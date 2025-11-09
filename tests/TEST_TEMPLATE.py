"""
Test Template and Best Practices
Fichier: tests/TEST_TEMPLATE.py

Use this template when writing new tests.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

# ============================================================================
# MODULE DOCSTRING
# ============================================================================
"""
Test suite for [module_name].

This module tests [brief_description].

Test organization:
- TestClassNameA: Tests for feature A
- TestClassNameB: Tests for feature B
"""


# ============================================================================
# CLASS-LEVEL FIXTURES
# ============================================================================


class TestFeatureA:
    """Tests for Feature A.

    This class groups related tests for Feature A functionality.
    Organize tests logically by feature/component.
    """

    # ========================================================================
    # SETUP & TEARDOWN
    # ========================================================================

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup before each test.

        Use this for initialization that should happen before every test.
        """
        print("\n--- Test Setup ---")
        # Initialize test data, mocks, etc.
        yield
        # Cleanup after test
        print("--- Test Cleanup ---")

    # ========================================================================
    # BASIC TEST PATTERN
    # ========================================================================

    @pytest.mark.unit
    def test_simple_functionality(self):
        """Test that simple_function returns expected output.

        Pattern:
        1. Arrange: Set up test data
        2. Act: Call the function
        3. Assert: Verify the result
        """
        # Arrange
        input_data = "test"
        expected_output = "expected"

        # Act
        from src.module import simple_function

        result = simple_function(input_data)

        # Assert
        assert result == expected_output

    # ========================================================================
    # PARAMETRIZED TESTS
    # ========================================================================

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("test1", "expected1"),
            ("test2", "expected2"),
            ("test3", "expected3"),
        ],
    )
    def test_multiple_inputs(self, input_val, expected):
        """Test function with multiple input values.

        @pytest.mark.parametrize allows testing multiple scenarios
        without duplicating test code.
        """
        from src.module import simple_function

        result = simple_function(input_val)
        assert result == expected

    # ========================================================================
    # EXCEPTION TESTING
    # ========================================================================

    @pytest.mark.unit
    def test_raises_exception_on_invalid_input(self):
        """Test that function raises expected exception.

        Use pytest.raises() context manager to verify exceptions.
        """
        from src.module import strict_function

        with pytest.raises(ValueError, match="Invalid input"):
            strict_function(None)

    # ========================================================================
    # MOCKING TESTS
    # ========================================================================

    @pytest.mark.unit
    @patch("src.module.external_function")
    def test_with_mocked_dependency(self, mock_external):
        """Test function that depends on external module.

        Use @patch to mock external dependencies and control their behavior.
        """
        # Arrange
        mock_external.return_value = "mocked_result"

        # Act
        from src.module import function_with_dependency

        result = function_with_dependency()

        # Assert
        assert result == "mocked_result"
        mock_external.assert_called_once()

    # ========================================================================
    # ASYNC TESTING
    # ========================================================================

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test async function.

        Use @pytest.mark.asyncio for async tests.
        Requires pytest-asyncio plugin.
        """
        from src.module import async_function

        result = await async_function()
        assert result is not None

    # ========================================================================
    # FIXTURE USAGE
    # ========================================================================

    @pytest.mark.unit
    def test_using_fixtures(self, sample_comments_df):
        """Test that uses fixtures from conftest.py.

        Fixtures provide reusable test data and setup.
        They're defined in conftest.py and can be used in any test.
        """
        # sample_comments_df is automatically injected
        assert len(sample_comments_df) > 0
        assert "comment_text" in sample_comments_df.columns

    # ========================================================================
    # DATABASE/FILE FIXTURES
    # ========================================================================

    @pytest.mark.unit
    def test_with_temp_file(self, tmp_path):
        """Test that uses temporary directory.

        tmp_path is a built-in fixture that provides a temporary directory.
        Use for testing file I/O operations.
        """
        # Create a test file
        test_file = tmp_path / "test_data.txt"
        test_file.write_text("test content")

        # Verify file was created
        assert test_file.exists()
        assert test_file.read_text() == "test content"

    # ========================================================================
    # PERFORMANCE TESTING
    # ========================================================================

    @pytest.mark.unit
    @pytest.mark.slow
    def test_performance(self):
        """Test that verifies performance requirements.

        Use @pytest.mark.slow for performance tests.
        These can be excluded with: pytest -m "not slow"
        """
        import time

        from src.module import optimized_function

        start = time.time()
        result = optimized_function()
        elapsed = time.time() - start

        # Should complete in < 1 second
        assert elapsed < 1.0
        assert result is not None

    # ========================================================================
    # COMPLEX MOCK EXAMPLE
    # ========================================================================

    @pytest.mark.unit
    def test_complex_mocking(self, mock_gcs_client):
        """Test with complex mocking setup.

        Example of mocking objects with specific behaviors.
        """
        # Use the mock_gcs_client fixture
        mock_gcs_client.bucket.return_value.blob.return_value.exists.return_value = True

        # Test code that uses the mock
        result = mock_gcs_client.bucket("test").blob("file.txt").exists()

        assert result is True


# ============================================================================
# INTEGRATION TEST EXAMPLE
# ============================================================================


class TestFeatureIntegration:
    """Integration tests for Feature A + Feature B interaction."""

    @pytest.mark.integration
    def test_full_workflow(self, api_client, sample_api_payload):
        """Test complete workflow from input to output.

        Integration tests verify components work together.
        Use fixtures for API client and sample data.
        """
        # Make API request
        response = api_client.post("/endpoint", json=sample_api_payload)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "result" in data


# ============================================================================
# BEST PRACTICES
# ============================================================================

# ✅ DO:
# - Use clear, descriptive test names: test_<function>_<scenario>
# - Use pytest markers to categorize tests
# - Keep tests small and focused (test one thing)
# - Use fixtures for setup/teardown
# - Use parametrize for multiple similar tests
# - Mock external dependencies
# - Test edge cases and error conditions
# - Use assertions with messages: assert result == expected, "reason"
# - Group related tests in classes

# ❌ DON'T:
# - Use vague test names: test_something_works
# - Write tests that depend on other tests
# - Use global state or shared mutable fixtures
# - Mock everything (mock only external dependencies)
# - Write tests that are too long or complex
# - Skip assertions or use poor assertions
# - Test multiple features in one test
# - Use sleep() or time.sleep() in tests
# - Ignore test failures

# ============================================================================
# TEST MARKERS
# ============================================================================

# Available markers (from pytest.ini):
# @pytest.mark.unit           - Unit test
# @pytest.mark.integration    - Integration test
# @pytest.mark.ml             - ML-specific test
# @pytest.mark.api            - API-specific test
# @pytest.mark.pipeline       - Pipeline test
# @pytest.mark.slow           - Slow/performance test
# @pytest.mark.smoke          - Quick smoke test

# Usage:
# pytest -m unit              # Run only unit tests
# pytest -m "not slow"        # Exclude slow tests
# pytest -m "unit and api"    # Run unit tests for API

# ============================================================================
# RUNNING TESTS
# ============================================================================

# Run all tests:
# pytest

# Run specific test file:
# pytest tests/unit/test_module.py

# Run specific test class:
# pytest tests/unit/test_module.py::TestClass

# Run specific test method:
# pytest tests/unit/test_module.py::TestClass::test_method

# Run with coverage:
# pytest --cov=src --cov-report=html

# Run in verbose mode:
# pytest -v

# Run with detailed output:
# pytest -vv

# Show print statements:
# pytest -s

# Stop at first failure:
# pytest -x

# Run last N failed tests:
# pytest --lf

# ============================================================================
# PYTEST FIXTURES - REFERENCE
# ============================================================================

# From conftest.py (shared across all tests):

# Data:
# - sample_comments_df()          DataFrame with 5 comments
# - sample_pii_comments()         Comments with personal info
# - sample_empty_comments()       Empty/invalid comments
# - sample_large_comments()       Large text samples

# Model:
# - mock_vectorizer()             TF-IDF vectorizer mock
# - mock_model()                  LogisticRegression mock
# - model_artifacts()             Real model artifacts

# Files:
# - temp_csv()                    Temporary CSV file
# - temp_model_files()            Temporary model directory

# API:
# - api_client()                  FastAPI TestClient
# - sample_api_payload()          Sample API request

# Built-in fixtures:
# - tmp_path                      Temporary directory
# - tmp_path_factory              Temporary directory factory
# - capsys                        Capture stdout/stderr
# - caplog                        Capture log messages
# - monkeypatch                   Monkey patching

# ============================================================================
# COMMON ASSERTIONS
# ============================================================================

# Basic:
# assert condition                           # Verify condition is True
# assert a == b                              # Verify equality
# assert a != b                              # Verify inequality
# assert a > b                               # Verify comparison

# Collections:
# assert len(collection) == 5                # Verify length
# assert item in collection                  # Verify membership
# assert a_dict['key'] == value              # Verify dict value

# Exceptions:
# with pytest.raises(ValueError):            # Verify exception
#     func()

# with pytest.raises(ValueError, match="msg"):  # Verify exception message
#     func()

# Approximate:
# assert abs(a - b) < 0.01                   # Floating point comparison
# import numpy as np
# assert np.allclose(a, b)                   # NumPy array comparison

# ============================================================================
# HELPFUL RESOURCES
# ============================================================================

# - Pytest documentation: https://docs.pytest.org/
# - Pytest fixtures: https://docs.pytest.org/en/stable/how-to/fixtures.html
# - TestClient (FastAPI): https://fastapi.tiangolo.com/advanced/testing-dependencies/
# - Mock documentation: https://docs.python.org/3/library/unittest.mock.html
# - Parametrize guide: https://docs.pytest.org/en/stable/how-to/parametrize.html

"""
Template ends here. Copy this pattern for new test files!
"""
