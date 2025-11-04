#!/bin/bash

# Quick Start Script for Digital Social Score API
# This script sets up the environment and starts the API

set -e

echo "=================================================="
echo "Digital Social Score API - Quick Start"
echo "=================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo ""
echo "Running validation..."
python validate_setup.py

echo ""
echo "=================================================="
echo "Setup complete! Starting API server..."
echo "=================================================="
echo ""
echo "API will be available at:"
echo "  - Main API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the API
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
