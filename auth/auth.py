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
        return hashlib.sha256(password.encode()).hexdigest()

    def signup_user(self, username, password):
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

    def update_score(self, username, score):
        """Update the highest score for a user if the new score is higher."""
        self.cursor.execute("SELECT highest_score FROM users WHERE username = ?", (username,))
        current_score = self.cursor.fetchone()
        if current_score and score > current_score[0]:
            self.cursor.execute("UPDATE users SET highest_score = ? WHERE username = ?", (score, username))
            self.conn.commit()
            print(f"Updated {username}'s highest score to {score}")

    def get_top_players(self):
        """Retrieve the top 5 players by highest score."""
        self.cursor.execute("SELECT username, highest_score FROM users ORDER BY highest_score DESC LIMIT 5")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()