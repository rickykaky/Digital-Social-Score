#!/usr/bin/env python
"""
Simple validation script to verify the setup is correct.
"""

import sys
import importlib.util

def check_module(module_name, package_name=None):
    """Check if a module can be imported."""
    try:
        if package_name:
            __import__(package_name)
            print(f"✓ {package_name} is installed")
        else:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                print(f"✓ {module_name} module exists")
            else:
                print(f"✗ {module_name} module not found")
                return False
    except ImportError as e:
        print(f"✗ Error importing {package_name or module_name}: {e}")
        return False
    return True

def main():
    """Run validation checks."""
    print("=" * 50)
    print("Digital Social Score - Setup Validation")
    print("=" * 50)
    print()
    
    print("Checking project structure...")
    modules_to_check = [
        ("src.api.main", None),
        ("src.models.toxicity_classifier", None),
        ("src.utils.anonymizer", None),
        ("src.utils.data_processor", None),
        ("config", None),
    ]
    
    all_ok = True
    for module, package in modules_to_check:
        if not check_module(module, package):
            all_ok = False
    
    print()
    print("Checking required packages...")
    packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "transformers",
        "torch",
        "spacy",
        "pandas",
        "numpy",
        "cryptography",
        "prometheus_client",
    ]
    
    for package in packages:
        check_module(None, package)
    
    print()
    print("Checking data directories...")
    import os
    dirs = ["data/raw", "data/processed", "data/anonymized", "logs", "docs"]
    for d in dirs:
        if os.path.exists(d):
            print(f"✓ {d} exists")
        else:
            print(f"✗ {d} missing")
            all_ok = False
    
    print()
    print("Checking documentation files...")
    files = [
        "README.md",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "docs/ARCHITECTURE.md",
        "docs/API_DOCUMENTATION.md",
        "docs/GDPR_COMPLIANCE.md",
    ]
    for f in files:
        if os.path.exists(f):
            print(f"✓ {f} exists")
        else:
            print(f"✗ {f} missing")
            all_ok = False
    
    print()
    print("=" * 50)
    if all_ok:
        print("✓ Setup validation passed!")
        print()
        print("Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Download spaCy model: python -m spacy download en_core_web_sm")
        print("3. Start the API: uvicorn src.api.main:app --reload")
        print("4. Visit: http://localhost:8000/docs")
        return 0
    else:
        print("✗ Setup validation found some issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
