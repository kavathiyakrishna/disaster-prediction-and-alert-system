# DB helper functions
import sqlite3
import os
from typing import List, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "disaster_alert.db")
DB_PATH = os.path.abspath(DB_PATH)

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def add_dataset(name: str, filename: str):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO datasets (name, filename) VALUES (?,?)", (name, filename))
    conn.commit()
    conn.close()

def list_datasets():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id,name,filename,uploaded_at FROM datasets ORDER BY uploaded_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def log_event(event_type: str, details: str):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT INTO logs (event_type, details) VALUES (?,?)", (event_type, details))
    conn.commit()
    conn.close()

def add_alert(disaster: str, probability: float, message: str):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT INTO alerts (disaster, probability, message) VALUES (?,?,?)", (disaster, probability, message))
    conn.commit()
    conn.close()

def list_alerts(unhandled_only: bool=True):
    conn = get_conn(); c = conn.cursor()
    if unhandled_only:
        c.execute("SELECT id,disaster,probability,message,timestamp,handled FROM alerts WHERE handled=0 ORDER BY timestamp DESC")
    else:
        c.execute("SELECT id,disaster,probability,message,timestamp,handled FROM alerts ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def mark_alert_handled(alert_id:int):
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE alerts SET handled=1 WHERE id=?", (alert_id,))
    conn.commit()
    conn.close()

def sync_datasets_with_folder(data_dir: str):
    """
    Auto-sync files in /data folder with datasets table.
    Only adds missing ones. Never deletes anything.
    """
    conn = get_conn()
    c = conn.cursor()

    # Get existing dataset filenames from DB
    c.execute("SELECT filename FROM datasets")
    db_files = {row[0] for row in c.fetchall()}

    # Scan the actual folder
    folder_files = {f for f in os.listdir(data_dir) if f.endswith(".csv")}

    # Insert only missing files
    for f in folder_files:
        if f not in db_files:
            name = f.replace("_dataset.csv", "").replace(".csv", "")
            c.execute("INSERT OR REPLACE INTO datasets (name, filename) VALUES (?,?)",
                      (name, f))

    conn.commit()
    conn.close()

