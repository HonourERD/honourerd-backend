 
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

#  Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

#  Create Users Table (if not exists)
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
	user_identifier TEXT UNIQUE NOT NULL 
    );
""")

#  Create Quiz Results Table (if not exists)
cur.execute("""
    CREATE TABLE IF NOT EXISTS quiz_results (
        id  SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(user_id),
        score INT,
        total_questions INT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

conn.commit()
print("Database setup complete!")
