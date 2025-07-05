#!/bin/bash
"""
Quick development setup script for Arweave Today Podcaster.
"""

echo "🏗️  ARWEAVE PODCASTER - DEVELOPMENT SETUP"
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📍 Python version: $python_version"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $(basename $VIRTUAL_ENV)"
else
    echo "⚠️  No virtual environment detected"
    echo "💡 Consider creating one: python3 -m venv venv && source venv/bin/activate"
fi

# Install package in development mode
echo ""
echo "📦 Installing package in development mode..."
pip install -e .

# Install development dependencies
echo ""
echo "🛠️  Installing development dependencies..."
pip install -e .[dev]

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Setting up environment configuration..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "📝 Please edit .env with your API keys"
else
    echo "✅ .env file already exists"
fi

# Run tests to verify setup
echo ""
echo "🧪 Running tests to verify setup..."
python -m pytest tests/ -v

# Show status
echo ""
echo "=========================================="
echo "✅ DEVELOPMENT SETUP COMPLETE!"
echo "=========================================="
echo "🚀 Run podcast generator: python main.py"
echo "🧪 Run tests: pytest"
echo "📚 View docs: docs/"
echo "⚙️ Configure APIs: edit .env file"
echo "=========================================="
