#!/bin/bash
# Oracle solution for the multi-service task
#
# Creates a user via the API and verifies it exists.

set -e

# Wait for the API to be ready
echo "Waiting for API to be ready..."
for i in $(seq 1 30); do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "API is ready."
        break
    fi
    sleep 1
done

# Create the test user via the API
echo "Creating test user..."
curl -s -X POST http://localhost:5000/users \
    -H "Content-Type: application/json" \
    -d '{"name": "harbor_test_user", "email": "test@harbor.dev"}'

echo ""
echo "Verifying user in database..."
PGPASSWORD=harbor psql -h db -U harbor -d harbordb -c \
    "SELECT * FROM users WHERE name='harbor_test_user';"

echo ""
echo "Listing all users via API..."
curl -s http://localhost:5000/users | python3 -m json.tool

echo ""
echo "Solution complete."
