 
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()


cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
	user_identifier TEXT UNIQUE NOT NULL 
    );
""")


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
