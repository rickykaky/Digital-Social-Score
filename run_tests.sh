#!/bin/bash
# Quick Testing Guide for Digital Social Score
# Script pour tester rapidement le projet

set -e

echo "🧪 Digital Social Score - Testing Guide"
echo "========================================"
echo ""

# Detect Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $PYTHON_VERSION"
echo ""

# Check if venv is active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not active!"
    echo "   Run: python -m venv venv && source venv/bin/activate"
    exit 1
fi
echo "✅ Virtual environment: $VIRTUAL_ENV"
echo ""

# Step 1: Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
pip install -q -r requirements-test.txt

# Download NLTK data
echo "📥 Downloading NLTK data..."
python -m nltk.downloader -d ~/nltk_data punkt stopwords wordnet averaged_perceptron_tagger maxent_ne_chunker words 2>/dev/null || true

echo "✅ Dependencies installed"
echo ""

# Step 2: Run tests
echo "🧪 Running tests..."
echo ""

# Choose test type
if [ $# -eq 0 ]; then
    echo "Available test commands:"
    echo "  1) Run all tests"
    echo "  2) Run unit tests only"
    echo "  3) Run integration tests only"
    echo "  4) Run pipeline tests only"
    echo "  5) Run ML tests only"
    echo "  6) Generate coverage report"
    echo "  7) Run with coverage"
    echo ""
    read -p "Choose test type (1-7): " choice
else
    choice=$1
fi

case $choice in
    1)
        echo "Running all tests..."
        pytest tests/ -v --tb=short
        ;;
    2)
        echo "Running unit tests..."
        pytest tests/unit/ -v -m unit --tb=short
        ;;
    3)
        echo "Running integration tests..."
        pytest tests/integration/ -v -m integration --tb=short
        ;;
    4)
        echo "Running pipeline tests..."
        pytest tests/pipeline/ -v -m pipeline --tb=short
        ;;
    5)
        echo "Running ML tests..."
        pytest tests/ml/ -v -m ml --tb=short
        ;;
    6)
        echo "Generating coverage report..."
        pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
        echo "✅ Coverage report generated in htmlcov/index.html"
        ;;
    7)
        echo "Running tests with coverage..."
        pytest tests/ -v --cov=src --cov-report=term-missing
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Testing complete!"
