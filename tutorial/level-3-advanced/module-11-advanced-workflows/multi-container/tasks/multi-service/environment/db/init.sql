-- Initialize the database schema for the multi-service task

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed with one existing user
INSERT INTO users (name, email) VALUES ('seed_user', 'seed@harbor.dev');
