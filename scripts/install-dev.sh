#!/bin/bash
# Development installation script for GentooUI

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🐧 GentooUI Development Installation"
echo "===================================="

# Check Python version
if ! python3 --version | grep -q "Python 3\.[89]\|Python 3\.1[0-9]"; then
    echo "❌ Python 3.8+ is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$PROJECT_DIR/.venv"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$PROJECT_DIR/.venv/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "📚 Installing development dependencies..."
pip install -e ".[dev,docs]"

# Install pre-commit hooks (if available)
if command -v pre-commit >/dev/null 2>&1; then
    echo "🔗 Installing pre-commit hooks..."
    pre-commit install
fi

echo ""
echo "✅ Development installation complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the application:"
echo "  gentooui --help"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
echo "To build documentation:"
echo "  cd docs && make html"
