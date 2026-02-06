#!/bin/bash

echo "🧹 Cleaning up repository for fresh Render deployment..."

# Remove Python cache and build artifacts
echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

echo "Removing .pyc files..."
find . -name "*.pyc" -delete 2>/dev/null

echo "Removing virtual environments..."
rm -rf .venv venv env

echo "Removing build artifacts..."
rm -rf *.egg-info
rm -rf build/
rm -rf dist/
rm -rf .pytest_cache/

echo "Removing IDE files..."
rm -rf .vscode/
rm -rf .idea/
rm -f .DS_Store

echo "Removing log files..."
rm -f *.log

echo "✅ Cleanup complete! Ready for fresh deployment."