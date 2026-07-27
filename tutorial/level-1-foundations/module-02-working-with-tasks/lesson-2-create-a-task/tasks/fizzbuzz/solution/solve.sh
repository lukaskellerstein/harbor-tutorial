#!/bin/bash

# Reference solution for the FizzBuzz task.

cat > /app/fizzbuzz.py << 'PYTHON'
for i in range(1, 101):
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
PYTHON

echo "FizzBuzz solution created."
