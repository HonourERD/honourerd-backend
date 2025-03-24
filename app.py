from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv

# Setup Flask app
app = Flask(__name__)

# ✅ FIX: Allow CORS from GitHub Pages
CORS(app, origins=["https://honourerd.github.io"])  # Replace with your GitHub Pages URL

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to the database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.route("/")
def home():
    return jsonify({"message": "Welcome to HonourERD API!"})


# ✅ Login Route
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user_identifier = data.get("user_identifier")

    if not user_identifier:
        return jsonify({"success": False, "message": "No identifier provided"}), 400

    cur.execute("SELECT user_id FROM users WHERE user_identifier = %s", (user_identifier,))
    user = cur.fetchone()

    if user:
        return jsonify({"success": True, "message": "User found!"})
    else:
        cur.execute("INSERT INTO users (user_identifier) VALUES (%s) RETURNING user_id", (user_identifier,))
        conn.commit()
        return jsonify({"success": True, "message": "New user created!"})


# ✅ Submit Score Route
@app.route("/submit_score", methods=["POST"])
def submit_score():
    data = request.get_json(silent=True)
    print("📩 Incoming data:", data)

    user_identifier = data.get("user_identifier")
    answers = data.get("answers", {})

    if not user_identifier or not answers:
        return jsonify({"success": False, "message": "Missing data"}), 400

    try:
        cur = conn.cursor()

        # Shift q0 → q1, q1 → q2...
        columns = ", ".join([f"q{int(q) + 1}" for q in answers.keys()])
        values = tuple(answers[q] for q in answers.keys())
        placeholders = ", ".join(["%s"] * len(answers))
        updates = ", ".join([f"q{int(q) + 1} = EXCLUDED.q{int(q) + 1}" for q in answers.keys()])

        query = f"""
        INSERT INTO quiz_results (user_identifier, {columns})
        VALUES (%s, {placeholders})
        ON CONFLICT (user_identifier)
        DO UPDATE SET {updates};
        """

        cur.execute(query, (user_identifier, *values))
        conn.commit()

        print("✅ Score submitted to DB!")
        return jsonify({"success": True, "message": "Answers submitted successfully!"})

    except Exception as e:
        conn.rollback()
        print("❌ DB Error:", e)
        return jsonify({"success": False, "message": f"Database error: {str(e)}"})

    finally:
        cur.close()


if __name__ == "__main__":
    app.run(debug=True)
