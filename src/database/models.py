"""
Database models for LMS system.

Uses SQLite for simplicity, can switch to PostgreSQL for production.
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Database handler for LMS."""
    
    def __init__(self, db_path: str = "data/lms.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = None
        self.setup_database()
    
    def connect(self):
        """Create database connection."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return dict-like rows
        return self.conn
    
    def setup_database(self):
        """Create all tables if they don't exist."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id_student INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                code_module TEXT,
                code_presentation TEXT,
                gender TEXT,
                region TEXT,
                highest_education TEXT,
                imd_band TEXT,
                age_band TEXT,
                disability TEXT,
                final_result TEXT,
                is_at_risk INTEGER DEFAULT 0,
                risk_probability REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Activities table (VLE interactions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_student INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                resource_id INTEGER,
                resource_type TEXT,
                clicks INTEGER DEFAULT 1,
                date INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_student) REFERENCES students(id_student)
            )
        """)
        
        # Assessments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_student INTEGER NOT NULL,
                id_assessment INTEGER NOT NULL,
                score REAL,
                submission_date INTEGER,
                is_late INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_student) REFERENCES students(id_student)
            )
        """)
        
        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_student INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                context TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_student) REFERENCES students(id_student)
            )
        """)
        
        # Interventions table (advisor actions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_student INTEGER NOT NULL,
                intervention_type TEXT NOT NULL,
                description TEXT,
                advisor_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (id_student) REFERENCES students(id_student)
            )
        """)
        
        # Course materials table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_module TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                material_type TEXT,
                week INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # VLE table (from OULAD dataset)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vle (
                id_site INTEGER PRIMARY KEY,
                code_module TEXT NOT NULL,
                code_presentation TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                week_from INTEGER,
                week_to INTEGER
            )
        """)
        
        conn.commit()
        logger.info("Database tables created successfully")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_student(self, email: str, password: str, **kwargs) -> Optional[int]:
        """Create new student account."""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO students (email, password_hash, first_name, last_name,
                                    code_module, code_presentation, gender, region,
                                    highest_education, imd_band, age_band, disability)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email, password_hash,
                kwargs.get('first_name', ''),
                kwargs.get('last_name', ''),
                kwargs.get('code_module', ''),
                kwargs.get('code_presentation', ''),
                kwargs.get('gender', ''),
                kwargs.get('region', ''),
                kwargs.get('highest_education', ''),
                kwargs.get('imd_band', ''),
                kwargs.get('age_band', ''),
                kwargs.get('disability', '')
            ))
            
            conn.commit()
            student_id = cursor.lastrowid
            logger.info(f"Created student {student_id}: {email}")
            return student_id
            
        except sqlite3.IntegrityError:
            logger.error(f"Email already exists: {email}")
            return None
    
    def authenticate_student(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate student login."""
        conn = self.connect()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute("""
            SELECT * FROM students 
            WHERE email = ? AND password_hash = ?
        """, (email, password_hash))
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_student(self, student_id: int) -> Optional[Dict]:
        """Get student by ID."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students WHERE id_student = ?", (student_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def update_student_risk(self, student_id: int, is_at_risk: int, risk_probability: float):
        """Update student risk prediction."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE students 
            SET is_at_risk = ?, risk_probability = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id_student = ?
        """, (is_at_risk, risk_probability, student_id))
        
        conn.commit()
        logger.info(f"Updated risk for student {student_id}: {risk_probability:.2%}")
    
    def log_activity(self, student_id: int, activity_type: str, **kwargs):
        """Log student activity."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO activities (id_student, activity_type, resource_id, resource_type, clicks, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student_id, activity_type,
            kwargs.get('resource_id'),
            kwargs.get('resource_type'),
            kwargs.get('clicks', 1),
            kwargs.get('date')
        ))
        
        conn.commit()
    
    def log_chat(self, student_id: int, message: str, response: str, context: str = None):
        """Log chat interaction."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_history (id_student, message, response, context)
            VALUES (?, ?, ?, ?)
        """, (student_id, message, response, context))
        
        conn.commit()
    
    def get_student_stats(self, student_id: int) -> Dict:
        """Get student statistics."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get activity count
        cursor.execute("""
            SELECT COUNT(*) as total_activities, 
                   SUM(clicks) as total_clicks,
                   COUNT(DISTINCT date) as days_active
            FROM activities 
            WHERE id_student = ?
        """, (student_id,))
        
        activity_stats = dict(cursor.fetchone())
        
        # Get assessment stats
        cursor.execute("""
            SELECT COUNT(*) as total_assessments,
                   AVG(score) as avg_score,
                   SUM(CASE WHEN is_late = 1 THEN 1 ELSE 0 END) as late_submissions
            FROM assessments
            WHERE id_student = ?
        """, (student_id,))
        
        assessment_stats = dict(cursor.fetchone())
        
        # Get chat history count
        cursor.execute("""
            SELECT COUNT(*) as chat_count
            FROM chat_history
            WHERE id_student = ?
        """, (student_id,))
        
        chat_stats = dict(cursor.fetchone())
        
        return {
            **activity_stats,
            **assessment_stats,
            **chat_stats
        }
    
    def get_chat_history(self, student_id: int, limit: int = 10) -> List[Dict]:
        """Get recent chat history."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM chat_history
            WHERE id_student = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (student_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def save_chat_message(self, student_id: int, message: str, response: str):
        """Save a chat message to history."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Use datetime.now() for Vietnam timezone (UTC+7)
        from datetime import datetime, timezone, timedelta
        vietnam_tz = timezone(timedelta(hours=7))
        timestamp = datetime.now(vietnam_tz).isoformat()
        
        cursor.execute("""
            INSERT INTO chat_history (id_student, message, response, timestamp)
            VALUES (?, ?, ?, ?)
        """, (student_id, message, response, timestamp))
        
        conn.commit()
        logger.info(f"Saved chat message for student {student_id}")
    
    def clear_chat_history(self, student_id: int):
        """Clear chat history for a student."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM chat_history
            WHERE id_student = ?
        """, (student_id,))
        
        conn.commit()
        logger.info(f"Cleared chat history for student {student_id}")
    
    def add_course_material(self, code_module: str, title: str, content: str, **kwargs):
        """Add course material."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO course_materials (code_module, title, content, material_type, week)
            VALUES (?, ?, ?, ?, ?)
        """, (code_module, title, content, kwargs.get('material_type'), kwargs.get('week')))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_course_materials(self, code_module: str) -> List[Dict]:
        """Get all materials for a course."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM course_materials
            WHERE code_module = ?
            ORDER BY week, title
        """, (code_module,))
        
        return [dict(row) for row in cursor.fetchall()]


# Singleton instance
_db = None

def get_db() -> Database:
    """Get database singleton."""
    global _db
    if _db is None:
        _db = Database()
    return _db


if __name__ == "__main__":
    # Test database
    db = Database()
    print("Database initialized successfully")
    
    # Test student creation
    student_id = db.create_student(
        email="test@example.com",
        password="test123",
        first_name="John",
        last_name="Doe",
        code_module="AAA",
        code_presentation="2013J"
    )
    
    if student_id:
        print(f"Created student: {student_id}")
        
        # Test authentication
        student = db.authenticate_student("test@example.com", "test123")
        print(f"Authenticated: {student['email']}")
        
        # Test activity logging
        db.log_activity(student_id, "view_material", resource_id=1, resource_type="video")
        print("Logged activity")
        
        # Test stats
        stats = db.get_student_stats(student_id)
        print(f"Stats: {stats}")

