"""Simple Flask API for the multi-container Harbor task."""

# The imports below are provided by the task container image, not by this
# lesson's virtualenv, so they do not resolve when you open this file locally.
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import os

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://harbor:harbor@db:5432/harbordb"
)


def get_db_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(DATABASE_URL)


@app.route("/users", methods=["GET"])
def list_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, created_at FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    users = [
        {"id": r[0], "name": r[1], "email": r[2], "created_at": str(r[3])}
        for r in rows
    ]
    return jsonify(users)


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "name and email are required"}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
        (data["name"], data["email"]),
    )
    row = cur.fetchone()
    assert row is not None, "INSERT ... RETURNING id always yields exactly one row"
    user_id = row[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": user_id, "name": data["name"], "email": data["email"]}), 201


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
