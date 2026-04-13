import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "eval_results.db")

def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eval_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            rag_accuracy REAL,
            baseline_accuracy REAL,
            food_count INTEGER,
            notes TEXT,
            results_json TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_run(result_dict: dict):
    init_db()
    conn = _get_connection()
    cursor = conn.cursor()
    
    timestamp = result_dict.get("run_timestamp", datetime.now().isoformat())
    rag_acc = result_dict.get("rag_accuracy_pct", 0.0)
    base_acc = result_dict.get("baseline_accuracy_pct", 0.0)
    food_count = len(result_dict.get("per_food_results", []))
    notes = result_dict.get("model", "unknown-model")
    
    cursor.execute("""
        INSERT INTO eval_runs (timestamp, rag_accuracy, baseline_accuracy, food_count, notes, results_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, rag_acc, base_acc, food_count, notes, json.dumps(result_dict)))
    
    conn.commit()
    conn.close()

def get_history():
    init_db()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eval_runs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
