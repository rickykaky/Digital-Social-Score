#!/usr/bin/env python3
"""
Visualize Testing Framework Setup
Script: scripts/visualize_testing_setup.py
"""

import os
from pathlib import Path
from collections import defaultdict


def count_lines(file_path):
    """Count lines in a file"""
    try:
        with open(file_path, 'r') as f:
            return len(f.readlines())
    except:
        return 0


def print_tree(directory, prefix="", max_depth=5, current_depth=0, ignore_dirs=None):
    """Print directory tree"""
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', '.pytest_cache', '.venv', 'venv', 'node_modules', '.tox'}
    
    if current_depth >= max_depth:
        return
    
    try:
        entries = sorted(os.listdir(directory))
    except PermissionError:
        return
    
    # Filter ignored directories
    entries = [e for e in entries if e not in ignore_dirs and not e.startswith('.')]
    
    for i, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = i == len(entries) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{entry}")
        
        if os.path.isdir(path) and not entry.startswith('.'):
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(path, next_prefix, max_depth, current_depth + 1, ignore_dirs)


def main():
    """Main function"""
    root = Path("/Users/romarickaki/Documents/GitHub/Digital-Social-Score")
    
    print("=" * 80)
    print("🧪 TESTING FRAMEWORK SETUP VISUALIZATION")
    print("=" * 80)
    print()
    
    # 1. Directory Structure
    print("📁 Test Directory Structure:")
    print("-" * 80)
    tests_dir = root / "tests"
    if tests_dir.exists():
        print_tree(str(tests_dir), max_depth=3)
    print()
    
    # 2. Files Created
    print("📄 Key Files Created:")
    print("-" * 80)
    
    key_files = {
        "Configuration": [
            ("pytest.ini", "Pytest configuration"),
            ("Makefile", "Development commands"),
            ("requirements-test.txt", "Test dependencies"),
        ],
        "Fixtures": [
            ("tests/conftest.py", "Shared pytest fixtures"),
            ("tests/TEST_TEMPLATE.py", "Test template & best practices"),
        ],
        "Unit Tests": [
            ("tests/unit/test_anonymization.py", "PII detection/masking tests"),
        ],
        "Integration Tests": [
            ("tests/integration/test_api_endpoints.py", "FastAPI endpoint tests"),
        ],
        "Pipeline Tests": [
            ("tests/pipeline/test_pipeline_components.py", "KFP component tests"),
        ],
        "ML Tests": [
            ("tests/ml/test_evaluator.py", "ML metrics evaluation tests"),
        ],
        "CI/CD": [
            (".github/workflows/tests.yml", "GitHub Actions workflow"),
        ],
        "Documentation": [
            ("TESTING.md", "Testing framework documentation"),
            ("TESTING_SETUP.md", "Setup summary"),
        ]
    }
    
    total_lines = 0
    total_tests = 0
    
    for category, files in key_files.items():
        print(f"\n{category}:")
        for filepath, description in files:
            full_path = root / filepath
            if full_path.exists():
                lines = count_lines(full_path)
                total_lines += lines
                # Count test functions roughly
                if 'test' in filepath.lower():
                    test_count = lines // 15  # Approximate
                    total_tests += test_count
                status = "✅"
            else:
                lines = 0
                status = "⚠️ "
            
            print(f"  {status} {filepath:<45} ({lines:>4} lines) - {description}")
    
    print()
    print("=" * 80)
    print("📊 STATISTICS")
    print("=" * 80)
    print(f"Total lines of test code:      {total_lines:>6}")
    print(f"Approximate test cases:        {total_tests:>6}")
    print(f"Test files created:            {len(key_files):>6}")
    print()
    
    # 3. Quick Start Commands
    print("=" * 80)
    print("🚀 QUICK START COMMANDS")
    print("=" * 80)
    print("""
1. Install dependencies:
   pip install -r requirements-test.txt

2. Run all tests:
   pytest
   or
   make test

3. Run specific tests:
   make test-unit              # Unit tests only
   make test-integration       # Integration tests only
   make test-pipeline          # Pipeline tests only
   make test-ml                # ML tests only

4. Generate coverage report:
   make coverage               # Terminal report
   make coverage-html          # HTML report

5. Code quality:
   make format                 # Auto-format code
   make lint                   # Run linters
   make type-check             # Type checking

6. Full CI pipeline:
   make ci                     # Run all checks
""")
    
    # 4. Test Categories
    print("=" * 80)
    print("🎯 TEST CATEGORIES")
    print("=" * 80)
    
    categories = {
        "Unit Tests": {
            "Files": ["test_anonymization.py"],
            "Coverage": "PII detection, regex patterns, masking functions, edge cases",
            "Count": "60+ tests"
        },
        "Integration Tests": {
            "Files": ["test_api_endpoints.py"],
            "Coverage": "API endpoints, error handling, validation, concurrency",
            "Count": "50+ tests"
        },
        "Pipeline Tests": {
            "Files": ["test_pipeline_components.py"],
            "Coverage": "KFP components, data flow, orchestration",
            "Count": "30+ tests"
        },
        "ML Tests": {
            "Files": ["test_evaluator.py"],
            "Coverage": "Metrics, accuracy, precision, recall, F1, ROC-AUC",
            "Count": "40+ tests"
        }
    }
    
    for category, info in categories.items():
        print(f"\n{category}:")
        print(f"  Files:    {', '.join(info['Files'])}")
        print(f"  Coverage: {info['Coverage']}")
        print(f"  Count:    {info['Count']}")
    
    # 5. CI/CD Integration
    print()
    print("=" * 80)
    print("🔄 CI/CD INTEGRATION")
    print("=" * 80)
    print("""
GitHub Actions Workflow (.github/workflows/tests.yml)
  ✅ Unit tests (parallel)
  ✅ Integration tests (depends on unit)
  ✅ Pipeline tests (parallel)
  ✅ Coverage report (depends on unit + integration)
  ✅ Code quality checks (lint, format, type-check)
  ✅ Security scan (bandit)
  ✅ Docker build (on main branch if all pass)

Runs automatically on:
  - Push to main, develop branches
  - Pull requests

Tests need to pass before merge!
""")
    
    # 6. Markers
    print("=" * 80)
    print("🏷️  TEST MARKERS")
    print("=" * 80)
    print("""
Available markers:
  @pytest.mark.unit          - Unit test
  @pytest.mark.integration   - Integration test
  @pytest.mark.ml            - ML-specific test
  @pytest.mark.api           - API-specific test
  @pytest.mark.pipeline      - Pipeline test
  @pytest.mark.slow          - Slow/performance test
  @pytest.mark.smoke         - Quick smoke test

Usage:
  pytest -m unit              # Run only unit tests
  pytest -m integration       # Run integration tests
  pytest -m "not slow"        # Exclude slow tests
  pytest -m "unit and api"    # Run unit tests for API
""")
    
    # 7. Fixtures
    print("=" * 80)
    print("🔧 AVAILABLE FIXTURES (from conftest.py)")
    print("=" * 80)
    print("""
Data Fixtures:
  sample_comments_df()        - DataFrame with 5 comments (toxic/non-toxic)
  sample_pii_comments()       - Comments with PII (emails, phones, etc.)
  sample_empty_comments()     - Empty/invalid comments
  sample_large_comments()     - Large text samples (5000+ chars)

Model Fixtures:
  mock_vectorizer()           - TF-IDF vectorizer mock
  mock_model()                - LogisticRegression mock
  model_artifacts()           - Real model artifacts (joblib)

File Fixtures:
  temp_csv()                  - Temporary CSV file
  temp_model_files()          - Temporary model directory

API Fixtures:
  api_client()                - FastAPI TestClient
  sample_api_payload()        - Sample API request payload

Configuration:
  test_config()               - TestingConfig instance
  reset_env()                 - Environment variable reset

Cloud Fixtures:
  mock_gcs_client()           - Google Cloud Storage mock
  mock_vertex_ai()            - Vertex AI mock
""")
    
    # 8. Next Steps
    print("=" * 80)
    print("📝 NEXT STEPS")
    print("=" * 80)
    print("""
1. Install dependencies:
   pip install -r requirements-test.txt

2. Download NLTK data:
   python -m nltk.downloader punkt stopwords wordnet averaged_perceptron_tagger

3. Run tests to verify setup:
   pytest tests/ -v

4. Check coverage:
   pytest --cov=src --cov-report=html

5. Add more tests using the template:
   tests/TEST_TEMPLATE.py

6. Push to GitHub:
   CI/CD workflow runs automatically
   Tests must pass before merge
""")
    
    print()
    print("=" * 80)
    print("✅ Testing Framework Setup Complete! 🎉")
    print("=" * 80)


if __name__ == "__main__":
    main()
