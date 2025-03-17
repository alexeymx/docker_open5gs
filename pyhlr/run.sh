#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install package if not installed
if ! pip show pyhlr > /dev/null; then
    echo "Installing PyHLR package..."
    pip install -e .
fi

# Run the service
PYTHONPATH=. python src/main.py 