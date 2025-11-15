"""
Create database tables for Proactive Intervention System
Implementation of requirements from SYSTEM_IMPROVEMENT_ANALYSIS.md
"""

import sqlite3
import os

def create_intervention_tables():
    """Create tables for intervention tracking and feedback"""
    
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'lms.db')
    print(f"Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create intervention_logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intervention_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            intervention_type TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            triggered_by TEXT NOT NULL,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id_student)
        )
    """)
    
    # Create intervention_feedback table for closed-loop feedback
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intervention_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intervention_id INTEGER NOT NULL,
            effectiveness_rating INTEGER CHECK (effectiveness_rating >= 1 AND effectiveness_rating <= 5),
            student_response TEXT,
            outcome TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (intervention_id) REFERENCES intervention_logs (id)
        )
    """)
    
    # Create intervention_strategies table for storing successful strategies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intervention_strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_type TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            student_profile TEXT,
            success_rate REAL DEFAULT 0.0,
            usage_count INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create student_intervention_history for tracking student journey
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_intervention_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            intervention_date DATE NOT NULL,
            risk_before REAL,
            risk_after REAL,
            intervention_type TEXT,
            outcome TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id_student)
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intervention_logs_student ON intervention_logs(student_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intervention_logs_date ON intervention_logs(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intervention_feedback_intervention ON intervention_feedback(intervention_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_history_student ON student_intervention_history(student_id)")
    
    conn.commit()
    conn.close()
    
    print("✅ Intervention tracking tables created successfully!")

if __name__ == "__main__":
    create_intervention_tables()