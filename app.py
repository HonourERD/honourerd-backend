 
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)  # ✅ Allow frontend to talk to backend

# ✅ Load database credentials
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.route("/")
def home():
    return jsonify({"message": "Welcome to HonourERD API!"})

# ✅ Handle user login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user_identifier = data.get("user_identifier")

    # ✅ Check if the user already exists
    cur.execute("SELECT user_id FROM users WHERE user_identifier = %s", (user_identifier,))
    user = cur.fetchone()

    if user:
        return jsonify({"success": True, "message": "User found!"})
    else:
        # ✅ If the user doesn't exist, create them
        cur.execute("INSERT INTO users (user_identifier) VALUES (%s) RETURNING user_id", (user_identifier,))
        conn.commit()
        return jsonify({"success": True, "message": "New user created!"})

if __name__ == "__main__":
    app.run(debug=True)
