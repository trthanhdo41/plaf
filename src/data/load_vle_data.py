"""
Load VLE data from OULAD into database.

This script loads:
- vle.csv: VLE activities (resources, videos, quizzes)
- courses.csv: Course modules
"""

import pandas as pd
import sqlite3
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_db


def load_vle_data():
    """Load VLE data from OULAD into database."""
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    
    # Create VLE tables if not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vle (
            id_site INTEGER PRIMARY KEY,
            code_module TEXT NOT NULL,
            code_presentation TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            week_from TEXT,
            week_to TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            code_module TEXT NOT NULL,
            code_presentation TEXT NOT NULL,
            module_presentation_length INTEGER,
            PRIMARY KEY (code_module, code_presentation)
        )
    """)
    
    conn.commit()
    
    print("Loading VLE data from OULAD...")
    
    # Load vle.csv
    try:
        vle_df = pd.read_csv("OULAD dataset/vle.csv")
        print(f"Loaded {len(vle_df)} VLE activities")
        
        # Insert into database
        vle_df.to_sql('vle', conn, if_exists='replace', index=False)
        print("✅ VLE data loaded successfully")
        
    except Exception as e:
        print(f"❌ Error loading vle.csv: {e}")
    
    # Load courses.csv
    try:
        courses_df = pd.read_csv("OULAD dataset/courses.csv")
        print(f"Loaded {len(courses_df)} courses")
        
        # Insert into database
        courses_df.to_sql('courses', conn, if_exists='replace', index=False)
        print("✅ Courses data loaded successfully")
        
    except Exception as e:
        print(f"❌ Error loading courses.csv: {e}")
    
    # Create sample course materials from VLE data
    print("\nGenerating course materials from VLE data...")
    
    cursor.execute("""
        SELECT DISTINCT code_module, code_presentation, activity_type, COUNT(*) as count
        FROM vle
        GROUP BY code_module, code_presentation, activity_type
        ORDER BY code_module, code_presentation, activity_type
    """)
    
    vle_summary = cursor.fetchall()
    print(f"Found {len(vle_summary)} unique activity types across modules")
    
    conn.close()
    print("\n✅ VLE data loading complete!")


def get_vle_activities(code_module: str, code_presentation: str = None):
    """Get VLE activities for a specific module."""
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    
    if code_presentation:
        cursor.execute("""
            SELECT * FROM vle
            WHERE code_module = ? AND code_presentation = ?
            ORDER BY activity_type, id_site
        """, (code_module, code_presentation))
    else:
        cursor.execute("""
            SELECT * FROM vle
            WHERE code_module = ?
            ORDER BY activity_type, id_site
        """, (code_module,))
    
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def get_activity_types_summary(code_module: str):
    """Get summary of activity types for a module."""
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT activity_type, COUNT(*) as count
        FROM vle
        WHERE code_module = ?
        GROUP BY activity_type
        ORDER BY count DESC
    """, (code_module,))
    
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    load_vle_data()
    
    # Test: Get activities for AAA module
    print("\n--- Testing VLE data retrieval ---")
    activities = get_vle_activities("AAA", "2013J")
    print(f"Found {len(activities)} activities for AAA 2013J")
    
    summary = get_activity_types_summary("AAA")
    print("\nActivity types in AAA:")
    for item in summary:
        print(f"  - {item['activity_type']}: {item['count']} items")

