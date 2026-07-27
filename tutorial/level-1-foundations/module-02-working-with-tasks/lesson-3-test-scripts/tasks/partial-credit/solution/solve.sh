#!/bin/bash

cat > /app/calculator.py << 'PYTHON'
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b
PYTHON

echo "Calculator solution created."
