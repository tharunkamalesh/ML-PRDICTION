"""
SQLite Database interface for anonymous assessment history and aggregate statistics.
Maintains privacy by storing zero PII (Personally Identifiable Information).
"""

import sqlite3
import os
import json
from datetime import datetime

from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "disease_prediction.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symptoms_count INTEGER NOT NULL,
            symptoms_list TEXT NOT NULL,
            primary_prediction TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            emergency_flag INTEGER NOT NULL DEFAULT 0,
            specialist_referred TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_assessment(symptoms, primary_prediction, confidence, emergency_flag, specialist):
    """Log an anonymous prediction event for metrics and dashboard display."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_history (
            timestamp, symptoms_count, symptoms_list,
            primary_prediction, confidence_score, emergency_flag, specialist_referred
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(timezone.utc).isoformat(),
        len(symptoms),
        json.dumps(symptoms),
        primary_prediction,
        round(confidence, 4),
        1 if emergency_flag else 0,
        specialist
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_history(limit=50):
    """Retrieve recent anonymous assessments."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, symptoms_count, symptoms_list,
               primary_prediction, confidence_score, emergency_flag, specialist_referred
        FROM assessment_history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "symptoms_count": r["symptoms_count"],
            "symptoms": json.loads(r["symptoms_list"]),
            "primary_prediction": r["primary_prediction"],
            "confidence_score": r["confidence_score"],
            "emergency_flag": bool(r["emergency_flag"]),
            "specialist_referred": r["specialist_referred"]
        })
    return results

def get_assessment_stats():
    """Retrieve summary counts and frequencies."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM assessment_history")
    total_assessments = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM assessment_history WHERE emergency_flag = 1")
    total_emergencies = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT primary_prediction, COUNT(*) as count
        FROM assessment_history
        GROUP BY primary_prediction
        ORDER BY count DESC
        LIMIT 5
    """)
    top_conditions = [{"disease": r[0], "count": r[1]} for r in cursor.fetchall()]
    
    conn.close()
    return {
        "total_assessments": total_assessments,
        "total_emergencies": total_emergencies,
        "top_conditions": top_conditions
    }

def clear_history():
    """Clear assessment records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assessment_history")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
