#!/bin/bash
# Quick start script for DrSeba.com

echo "=========================================="
echo "DrSeba.com - Healthcare Platform"
echo "Quick Start Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create sample data
echo "Creating sample data..."
python setup.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the development server, run:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Access the application at: http://127.0.0.1:8000"
echo ""
echo "Default Login Credentials:"
echo "  Admin:    admin / admin123"
echo "  Doctor:   doctor1 / doctor123"
echo "  Patient:  patient1 / patient123"
echo ""
