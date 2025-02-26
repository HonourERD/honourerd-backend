 
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)  # Allow frontend to talk to backend

# Load database credentials
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.route("/")
def home():
    return jsonify({"message": "Welcome to HonourERD API!"})

# Handle user login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user_identifier = data.get("user_identifier")

    if not user_identifier:
        return jsonify({"success": False, "message": "No identifier provided"}), 400

    # Check if user exists
    cur.execute("SELECT user_id FROM users WHERE user_identifier = %s", (user_identifier,))
    user = cur.fetchone()

    if user:
        return jsonify({"success": True, "message": "User found!"})
    else:
        # If the user doesn't exist, create them
        cur.execute("INSERT INTO users (user_identifier) VALUES (%s) RETURNING user_id", (user_identifier,))
        conn.commit()
        return jsonify({"success": True, "message": "New user created!"})

    
# Handle quiz score submission
@app.route("/submit-score", methods=["POST"])
def submit_score():
    data = request.json
    user_identifier = data.get("user_identifier")
    score = data.get("score")
    total_questions = data.get("total_questions")

    if not user_identifier or score is None or total_questions is None:
        return jsonify({"success": False, "message": "Missing data"}), 400

    #  Insert or update the user's score in the database
    cur.execute(
        """
        INSERT INTO quiz_results (user_identifier, score, total_questions) 
        VALUES (%s, %s, %s)
        ON CONFLICT (user_identifier) 
        DO UPDATE SET score = EXCLUDED.score;
        """, 
        (user_identifier, score, total_questions)
    )
    conn.commit()

    return jsonify({"success": True, "message": "Score submitted successfully!"})


    #  Check if the user already exists
    cur.execute("SELECT user_id FROM users WHERE user_identifier = %s", (user_identifier,))
    user = cur.fetchone()

    if user:
        return jsonify({"success": True, "message": "User found!"})
    else:
    
        cur.execute("INSERT INTO users (user_identifier) VALUES (%s) RETURNING user_id", (user_identifier,))
        conn.commit()
        return jsonify({"success": True, "message": "New user created!"})

if __name__ == "__main__":
    app.run(debug=True)
