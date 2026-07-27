# Multi-Service Task: API + Database Integration

You are working with a web application that has two services:

1. **API** (Flask) — running on port 5000
2. **Database** (PostgreSQL) — running on port 5432

## Your Task

1. Use the API to create a new user by sending a POST request:
   ```
   curl -X POST http://localhost:5000/users \
     -H "Content-Type: application/json" \
     -d '{"name": "harbor_test_user", "email": "test@harbor.dev"}'
   ```

2. Verify the user was stored in the database by querying PostgreSQL directly:
   ```
   PGPASSWORD=harbor psql -h db -U harbor -d harbordb -c "SELECT * FROM users WHERE name='harbor_test_user';"
   ```

3. Use the API to retrieve all users and confirm the new user appears:
   ```
   curl http://localhost:5000/users
   ```

The task is complete when the user exists in both the API response and the database.
