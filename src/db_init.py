# Initialize sqlite DB, create tables, and add a default admin.
import sqlite3
import bcrypt
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "disaster_alert.db")
DB_PATH = os.path.abspath(DB_PATH)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # users: id, username, password_hash, role
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash BLOB NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    # datasets: id, name, filename, uploaded_at
    c.execute('''
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        filename TEXT UNIQUE,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    # logs: id, timestamp, event_type, details
    c.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT,
        details TEXT
    )
    ''')
    # alerts: id, disaster, probability, timestamp, handled
    c.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disaster TEXT,
        probability REAL,
        message TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        handled INTEGER DEFAULT 0
    )
    ''')
    conn.commit()

    # add default admin if not exists
    c.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not c.fetchone():
        pw = "adminpass"  # change immediately after first login
        pw_hash = bcrypt.hashpw(pw.encode(), bcrypt.gensalt())
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                  ("admin", pw_hash, "admin"))
        conn.commit()
        print("Default admin created: username=admin password=adminpass. Change immediately!")
    conn.close()

if __name__ == "__main__":
    init_db()
    print("DB initialized at:", DB_PATH)
