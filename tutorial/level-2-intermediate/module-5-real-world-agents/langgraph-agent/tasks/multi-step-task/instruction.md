Complete the following multi-step task:

1. Create a directory /app/project/
2. Create a file /app/project/config.json with this content:
   {"name": "demo", "version": "1.0", "entries": 5}
3. Write a Python script /app/project/generate.py that:
   - Reads config.json
   - Creates a file /app/project/output.txt containing exactly N lines
     (where N is the "entries" value from config.json)
   - Each line should be: "Entry <i>" where <i> is the 1-based index
4. Run the script: python3 /app/project/generate.py
