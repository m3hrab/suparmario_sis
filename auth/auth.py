import sqlite3
import hashlib

class Database:
    
    def __init__(self, db_path="auth/users.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                highest_score INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    @staticmethod
    def hash_password(password):
        # Hash the password using SHA-256
        return hashlib.sha256(password.encode()).hexdigest()

    def signup_user(self, username, password):
        # inseert the username and hashed password into the database if the username is unique
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, self.hash_password(password)))
            self.conn.commit()
            return True, "Registration Successful!"
        except sqlite3.IntegrityError:
            return False, "Username already exists!"

    def login_user(self, username, password):
        self.cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        record = self.cursor.fetchone()
        return (True, "Login Successful!") if record and record[0] == self.hash_password(password) else (False, "Invalid Credentials!")

    def close(self):
        self.conn.close()

