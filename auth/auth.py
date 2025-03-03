import sqlite3

class HashTable:
    def __init__(self):
        self.table = {}

    def hash(self, key):
        hash_value = 0
        for char in key:
            hash_value = (hash_value * 31 + ord(char)) & 0xFFFFFFFF
        return hash_value

    def store(self, key, value):
        self.table[key] = value

    def retrieve(self, key):
        return self.table.get(key, None)

class Database:
    def __init__(self, db_path="auth/users.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.hashtable = HashTable()

        # user information table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                highest_score INTEGER DEFAULT 0
            )
        """)
        # game sessions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                score INTEGER,
                timestamp TEXT,
                lives_lost INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        self.conn.commit()

    @staticmethod
    def hash_password(password):
        # Use the HashTable to store and retrieve hashed passwords
        hashtable = HashTable()
        hashed_password = hashtable.hash(password)
        hashtable.store(password, hashed_password)
        return str(hashed_password)

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
        self.cursor.execute("SELECT highest_score FROM users WHERE username = ?", (username,))
        current_score = self.cursor.fetchone()
        if current_score and score > current_score[0]:
            self.cursor.execute("UPDATE users SET highest_score = ? WHERE username = ?", (score, username))
            self.conn.commit()
            # print(f"Updated {username} highest score to {score}")

    def get_top_players(self):
        self.cursor.execute("SELECT username, highest_score FROM users ORDER BY highest_score DESC LIMIT 5")
        return self.cursor.fetchall()

    def get_top_players_with_stats(self):
        self.cursor.execute("""
            SELECT u.username, u.highest_score, AVG(gs.lives_lost) as avg_lives_lost
            FROM users u
            LEFT JOIN game_sessions gs ON u.id = gs.user_id
            GROUP BY u.id, u.username, u.highest_score
            ORDER BY u.highest_score DESC
            LIMIT 5
        """)
        return self.cursor.fetchall()

    def log_game_session(self, user_id, score, lives_lost):
        """Log a game session with user_id, score, timestamp, and lives lost."""
        import time  
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  
        self.cursor.execute("INSERT INTO game_sessions (user_id, score, timestamp, lives_lost) VALUES (?, ?, ?, ?)",
                            (user_id, score, timestamp, lives_lost))
        self.conn.commit()
        # print(f"Logged session user_id {user_id}: score={score}, lives_lost={lives_lost}, timestamp={timestamp}")

    def get_user_id(self, username):
        """Get user ID from username."""
        self.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        self.conn.close()