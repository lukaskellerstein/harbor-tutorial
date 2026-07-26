#!/bin/bash

cat > /app/fetch_status.py << 'PYTHON'
import requests

def main():
    try:
        response = requests.get("http://example.com", timeout=10)
        print(response.status_code)
        with open("/app/response.html", "w") as f:
            f.write(response.text)
    except requests.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
PYTHON

echo "fetch_status solution created."
