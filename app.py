 
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv
import json


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Load database credentials
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.route("/")
def home():
    return jsonify({"message": "Welcome to HonourERD API!"})


# 🏆 Handle user login
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



def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


@app.route("/submit-score", methods=["POST"])
def submit_score():
    data = request.json
    user_identifier = data.get("user_identifier")
    answers = json.dumps(data.get("answers"))  # Convert Python dict to JSON

    if not user_identifier or not answers:
        return jsonify({"success": False, "message": "Missing data"}), 400

    try:
        conn = get_db_connection()  # ✅ Now this function actually exists
        cur = conn.cursor()

        # ✅ Insert or Update the JSONB answers for the user
        cur.execute(
            """
            INSERT INTO quiz_results (user_identifier, answers) 
            VALUES (%s, %s)
            ON CONFLICT (user_identifier) 
            DO UPDATE SET answers = EXCLUDED.answers;
            """, 
            (user_identifier, answers)
        )
        conn.commit()
        cur.close()
        conn.close()  # ✅ Close the connection

        return jsonify({"success": True, "message": "Answers submitted successfully!"})

    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)

