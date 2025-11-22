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
                num_of_prev_attempts INTEGER DEFAULT 0,
                studied_credits INTEGER DEFAULT 0,
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
                code_module TEXT,
                code_presentation TEXT,
                assessment_type TEXT,
                date_due INTEGER,
                weight REAL,
                score REAL,
                date_submitted INTEGER,
                is_banked INTEGER DEFAULT 0,
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
        
        # Courses table (for demo courses)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                thumbnail_url TEXT,
                instructor_name TEXT,
                instructor_title TEXT,
                duration_hours INTEGER,
                level TEXT,
                category TEXT,
                code_module TEXT,
                course_code TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Ensure code_module column exists for existing databases
        try:
            cursor.execute("ALTER TABLE courses ADD COLUMN code_module TEXT")
        except Exception:
            # Column already exists or table just created
            pass
        
        # Ensure course_code column exists and is unique for existing databases
        try:
            cursor.execute("ALTER TABLE courses ADD COLUMN course_code TEXT")
        except Exception:
            pass
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_courses_course_code ON courses(course_code)")
        except Exception:
            pass
        
        # Lessons table (for course content)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                video_url TEXT,
                lesson_type TEXT DEFAULT 'video',  -- video, reading, quiz
                duration_minutes INTEGER,
                lesson_order INTEGER,
                is_free INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)
        
        # Student progress table (track learning progress)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                completed BOOLEAN DEFAULT 0,
                progress_percent REAL DEFAULT 0.0,
                time_spent_minutes INTEGER DEFAULT 0,
                video_watch_time INTEGER DEFAULT 0,
                video_duration INTEGER DEFAULT 0,
                watch_percentage REAL DEFAULT 0.0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id_student),
                FOREIGN KEY (course_id) REFERENCES courses (id),
                FOREIGN KEY (lesson_id) REFERENCES lessons (id),
                UNIQUE(student_id, course_id, lesson_id)
            )
        """)
        
        # Course enrollments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                progress_percent REAL DEFAULT 0.0,
                completed_at TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id_student) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                UNIQUE(student_id, course_id)
            )
        """)
        
        # Quizzes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                lesson_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                duration_minutes INTEGER DEFAULT 30,
                passing_score REAL DEFAULT 70.0,
                max_attempts INTEGER DEFAULT 3,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL
            )
        """)
        
        # Quiz questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                question_type TEXT DEFAULT 'multiple_choice',
                points REAL DEFAULT 1.0,
                explanation TEXT,
                question_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
            )
        """)
        
        # Quiz answers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                answer_text TEXT NOT NULL,
                is_correct INTEGER DEFAULT 0,
                answer_order INTEGER DEFAULT 0,
                FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE
            )
        """)
        
        # Student quiz attempts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                quiz_id INTEGER NOT NULL,
                attempt_number INTEGER DEFAULT 1,
                score REAL DEFAULT 0.0,
                total_points REAL DEFAULT 0.0,
                passed INTEGER DEFAULT 0,
                time_spent INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                submitted_at TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id_student) ON DELETE CASCADE,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
            )
        """)
        
        # Student quiz responses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_quiz_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempt_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                answer_id INTEGER,
                answer_text TEXT,
                is_correct INTEGER DEFAULT 0,
                points_earned REAL DEFAULT 0.0,
                FOREIGN KEY (attempt_id) REFERENCES student_quiz_attempts(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE,
                FOREIGN KEY (answer_id) REFERENCES quiz_answers(id) ON DELETE SET NULL
            )
        """)
        
        # Forums table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)
        
        # Forum posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forum_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                forum_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                is_pinned INTEGER DEFAULT 0,
                is_locked INTEGER DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (forum_id) REFERENCES forums(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(id_student) ON DELETE CASCADE
            )
        """)
        
        # Forum replies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forum_replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                is_solution INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(id_student) ON DELETE CASCADE
            )
        """)
        
        # Forum reactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forum_reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                post_id INTEGER,
                reply_id INTEGER,
                reaction_type TEXT DEFAULT 'like',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id_student) ON DELETE CASCADE,
                FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE,
                FOREIGN KEY (reply_id) REFERENCES forum_replies(id) ON DELETE CASCADE,
                UNIQUE(student_id, post_id, reply_id, reaction_type)
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
        
        # Get student data directly from students table
        cursor.execute("""
            SELECT total_clicks, num_days_active, avg_score
            FROM students 
            WHERE id_student = ?
        """, (student_id,))
        
        student_data = cursor.fetchone()
        if student_data:
            activity_stats = {
                'total_activities': student_data['total_clicks'] or 0,
                'total_clicks': student_data['total_clicks'] or 0,
                'days_active': student_data['num_days_active'] or 0
            }
        else:
            activity_stats = {'total_activities': 0, 'total_clicks': 0, 'days_active': 0}
        
        # Get assessment stats from student_assessments table
        cursor.execute("""
            SELECT COUNT(*) as total_assessments,
                   AVG(score) as avg_score
            FROM student_assessments
            WHERE student_id = ?
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
            **chat_stats,
            'late_submissions': 0  # Add default value
        }
    
    def update_video_progress(self, student_id: int, lesson_id: int, watch_time: int, video_duration: int, watch_percentage: float):
        """Update video watch progress for a lesson."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO student_progress 
            (student_id, lesson_id, video_watch_time, video_duration, watch_percentage, last_accessed)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (student_id, lesson_id, watch_time, video_duration, watch_percentage))
        
        conn.commit()
        logger.info(f"Updated video progress for student {student_id}, lesson {lesson_id}: {watch_percentage:.1f}%")
    
    def get_video_progress(self, student_id: int, lesson_id: int) -> Dict:
        """Get video watch progress for a lesson."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT video_watch_time, video_duration, watch_percentage, completed
            FROM student_progress 
            WHERE student_id = ? AND lesson_id = ?
        """, (student_id, lesson_id))
        
        result = cursor.fetchone()
        if result:
            return {
                'watch_time': result['video_watch_time'] or 0,
                'duration': result['video_duration'] or 0,
                'percentage': result['watch_percentage'] or 0,
                'completed': bool(result['completed'])
            }
        
        return {'watch_time': 0, 'duration': 0, 'percentage': 0, 'completed': False}
    
    def update_student_progress(self, student_id: int, course_id: int, lesson_id: int, progress_percent: float, completed: bool):
        """Update student progress for a lesson."""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Insert or update progress
            cursor.execute("""
                INSERT OR REPLACE INTO student_progress 
                (student_id, course_id, lesson_id, completed, progress_percent, last_accessed)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (student_id, course_id, lesson_id, 1 if completed else 0, progress_percent))
            
            conn.commit()
            logger.info(f"Updated progress for student {student_id}, lesson {lesson_id}: {progress_percent}% ({'completed' if completed else 'in progress'})")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update student progress: {e}")
            raise e
        finally:
            conn.close()
    
    # ==================== Quiz System Methods ====================
    
    def get_lesson_quiz(self, lesson_id: int) -> Dict:
        """Get quiz for a lesson."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM quizzes WHERE lesson_id = ? AND is_active = 1
        """, (lesson_id,))
        
        quiz = cursor.fetchone()
        if not quiz:
            return None
            
        # Get quiz questions
        cursor.execute("""
            SELECT * FROM quiz_questions WHERE quiz_id = ? ORDER BY question_order
        """, (quiz['id'],))
        
        questions = cursor.fetchall()
        
        return {
            'id': quiz['id'],
            'title': quiz['title'],
            'description': quiz['description'],
            'passing_score': quiz['passing_score'],
            'duration_minutes': quiz['duration_minutes'],
            'questions': [
                {
                    'id': q['id'],
                    'question': q['question_text'],
                    'options': [q['option_a'], q['option_b'], q['option_c'], q['option_d']],
                    'correct_answer': q['correct_option'],
                    'explanation': q['explanation']
                } for q in questions
            ]
        }
    
    def save_quiz_result(self, student_id: int, quiz_id: int, lesson_id: int, answers: dict, score: float, passed: bool, time_taken: int = None) -> int:
        """Save quiz result."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO quiz_results 
            (student_id, quiz_id, lesson_id, answers, score, passed, time_taken, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (student_id, quiz_id, lesson_id, str(answers), score, 1 if passed else 0, time_taken))
        
        conn.commit()
        result_id = cursor.lastrowid
        
        # Update student progress if passed
        if passed:
            cursor.execute("""
                UPDATE student_progress 
                SET completed = 1, progress_percent = 100.0
                WHERE student_id = ? AND lesson_id = ?
            """, (student_id, lesson_id))
            conn.commit()
        
        logger.info(f"Saved quiz result {result_id} for student {student_id}: {score:.1f}% ({'PASSED' if passed else 'FAILED'})")
        return result_id
    
    # ==================== Forum System Methods ====================
    
    def get_forum_posts(self, lesson_id: int) -> List[Dict]:
        """Get forum posts for a lesson."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Simple query first
        cursor.execute("""
            SELECT * FROM forum_posts 
            WHERE lesson_id = ?
            ORDER BY is_pinned DESC, created_at DESC
        """, (lesson_id,))
        
        posts = cursor.fetchall()
        result = []
        
        for post in posts:
            post_dict = dict(post)
            
            # Get replies count
            cursor.execute("SELECT COUNT(*) FROM forum_replies WHERE post_id = ?", (post['id'],))
            post_dict['replies_count'] = cursor.fetchone()[0]
            
            # Get likes count
            cursor.execute("SELECT COUNT(*) FROM forum_votes WHERE post_id = ? AND vote_type = 'like'", (post['id'],))
            post_dict['likes'] = cursor.fetchone()[0]
            
            # Get dislikes count
            cursor.execute("SELECT COUNT(*) FROM forum_votes WHERE post_id = ? AND vote_type = 'dislike'", (post['id'],))
            post_dict['dislikes'] = cursor.fetchone()[0]
            
            result.append(post_dict)
        
        return result
    
    def create_forum_post(self, lesson_id: int, title: str, content: str, author_id: int, author: str) -> int:
        """Create a new forum post."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO forum_posts (lesson_id, title, content, author_id, author, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'), datetime('now', 'localtime'))
        """, (lesson_id, title, content, author_id, author))
        
        conn.commit()
        post_id = cursor.lastrowid
        logger.info(f"Created forum post {post_id}: {title}")
        return post_id
    
    def get_forum_replies(self, post_id: int) -> List[Dict]:
        """Get replies for a forum post."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT fr.*, s.first_name, s.last_name,
                   0 as likes, 0 as dislikes
            FROM forum_replies fr
            LEFT JOIN students s ON fr.student_id = s.id_student
            WHERE fr.post_id = ?
            ORDER BY fr.is_solution DESC, fr.created_at ASC
        """, (post_id,))
        
        replies = cursor.fetchall()
        return [dict(reply) for reply in replies]
    
    def create_forum_reply(self, post_id: int, content: str, author_id: int, author: str) -> int:
        """Create a reply to a forum post."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO forum_replies (post_id, content, student_id, created_at)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
        """, (post_id, content, author_id))
        
        conn.commit()
        reply_id = cursor.lastrowid
        logger.info(f"Created forum reply {reply_id} for post {post_id}")
        return reply_id
    
    def vote_forum_post(self, post_id: int, student_id: int, vote_type: str):
        """Vote on a forum post. If same vote exists, remove it (unlike/undislike)."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Check if user already voted with same type
        cursor.execute("""
            SELECT vote_type FROM forum_votes 
            WHERE post_id = ? AND student_id = ?
        """, (post_id, student_id))
        
        existing_vote = cursor.fetchone()
        
        if existing_vote and existing_vote['vote_type'] == vote_type:
            # Same vote type - remove it (unlike/undislike)
            cursor.execute("""
                DELETE FROM forum_votes WHERE post_id = ? AND student_id = ?
            """, (post_id, student_id))
            logger.info(f"Student {student_id} removed {vote_type} on post {post_id}")
        else:
            # Different vote type or no vote - remove existing and add new
            cursor.execute("""
                DELETE FROM forum_votes WHERE post_id = ? AND student_id = ?
            """, (post_id, student_id))
            
            cursor.execute("""
                INSERT INTO forum_votes (post_id, student_id, vote_type, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (post_id, student_id, vote_type))
            logger.info(f"Student {student_id} voted {vote_type} on post {post_id}")
        
        conn.commit()
    
    def get_user_votes_for_lesson(self, lesson_id: int, student_id: int) -> Dict[int, str]:
        """Get user's votes for all posts in a lesson."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT fv.post_id, fv.vote_type
            FROM forum_votes fv
            JOIN forum_posts fp ON fv.post_id = fp.id
            WHERE fp.lesson_id = ? AND fv.student_id = ?
        """, (lesson_id, student_id))
        
        votes = {}
        for row in cursor.fetchall():
            votes[row['post_id']] = row['vote_type']
        
        return votes
    
    def get_student_full_context(self, student_id: int) -> Dict:
        """Get comprehensive student context for AI chatbot."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Get student basic info
            cursor.execute("SELECT * FROM students WHERE id_student = ?", (student_id,))
            student = cursor.fetchone()
            
            if not student:
                return {}
            
            # Get current enrollments and progress
            cursor.execute("""
                SELECT c.title as course_title, c.id as course_id,
                       COUNT(l.id) as total_lessons,
                       COUNT(CASE WHEN sp.completed = 1 THEN 1 END) as completed_lessons,
                       AVG(CASE WHEN sp.progress_percent > 0 THEN sp.progress_percent END) as avg_progress
                FROM course_enrollments ce
                JOIN courses c ON ce.course_id = c.id
                LEFT JOIN lessons l ON c.id = l.course_id
                LEFT JOIN student_progress sp ON l.id = sp.lesson_id AND sp.student_id = ?
                WHERE ce.student_id = ?
                GROUP BY c.id, c.title
            """, (student_id, student_id))
            
            courses = cursor.fetchall()
            
            # Get quiz results
            quiz_results = []
            try:
                cursor.execute("""
                    SELECT 
                        sqa.score,
                        sqa.passed,
                        sqa.attempt_number,
                        sqa.time_spent,
                        q.title as quiz_title,
                        c.title as course_title,
                        l.title as lesson_title
                    FROM student_quiz_attempts sqa
                    JOIN quizzes q ON sqa.quiz_id = q.id
                    LEFT JOIN lessons l ON q.lesson_id = l.id
                    LEFT JOIN courses c ON l.course_id = c.id
                    WHERE sqa.student_id = ?
                    ORDER BY sqa.submitted_at DESC, sqa.id DESC
                    LIMIT 10
                """, (student_id,))
                quiz_results = cursor.fetchall()
            except sqlite3.Error as e:
                logger.warning(f"Quiz results not available: {e}")
                quiz_results = []
            
            # Get forum activity
            forum_posts = 0
            try:
                cursor.execute("""
                    SELECT COUNT(*) as posts_count
                    FROM forum_posts
                    WHERE student_id = ?
                """, (student_id,))
                row = cursor.fetchone()
                forum_posts = row['posts_count'] if row else 0
            except sqlite3.Error as e:
                logger.warning(f"Forum data not available: {e}")
            
            # Get recent chat history
            cursor.execute("""
                SELECT message, response, timestamp
                FROM chat_history
                WHERE id_student = ?
                ORDER BY timestamp DESC
                LIMIT 5
            """, (student_id,))
            
            chat_history = cursor.fetchall()
            
            # Calculate overall stats from course enrollments
            total_courses = len(courses)
            total_completed_lessons = sum(course['completed_lessons'] or 0 for course in courses)
            total_lessons = sum(course['total_lessons'] or 0 for course in courses)
            course_progress = (total_completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            
            # Quiz performance from quiz results
            quiz_scores = [quiz['score'] for quiz in quiz_results if quiz['score'] is not None]
            quiz_avg_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
            passed_quizzes = sum(1 for quiz in quiz_results if quiz['passed'])
            
            # Check for simulation mode
            sim_day = self.get_simulation_day(student_id)
            
            # Get OULAD activity and assessment data (calculate from activities/assessments tables)
            # This is the ground truth data for students
            if sim_day is not None:
                cursor.execute("""
                    SELECT COUNT(DISTINCT date) as days_active,
                           SUM(clicks) as total_clicks,
                           COUNT(*) as total_activities
                    FROM activities
                    WHERE id_student = ? AND date <= ?
                """, (student_id, sim_day))
            else:
                cursor.execute("""
                    SELECT COUNT(DISTINCT date) as days_active,
                           SUM(clicks) as total_clicks,
                           COUNT(*) as total_activities
                    FROM activities
                    WHERE id_student = ?
                """, (student_id,))
                
            activity_data = cursor.fetchone()
            days_active = activity_data['days_active'] if activity_data else 0
            total_clicks = activity_data['total_clicks'] if activity_data else 0
            
            # Calculate OULAD-compliant grade using Two-Component Rule
            # Official OULAD Rule: Pass IF (OCAS ≥ 40) AND (OES ≥ 40)
            # Source: https://analyse.kmi.open.ac.uk/open_dataset
            
            # Calculate OCAS (Overall Continuous Assessment Score)
            # OCAS = Σ(TMA/CMA score × weight) / 100
            if sim_day is not None:
                cursor.execute("""
                    SELECT 
                        SUM(score * weight) / 100.0 as ocas,
                        COUNT(*) as total_tma_cma
                    FROM assessments
                    WHERE id_student = ?
                    AND score IS NOT NULL
                    AND weight IS NOT NULL
                    AND weight > 0
                    AND assessment_type IN ('TMA', 'CMA')
                    AND date_submitted <= ?
                """, (student_id, sim_day))
            else:
                cursor.execute("""
                    SELECT 
                        SUM(score * weight) / 100.0 as ocas,
                        COUNT(*) as total_tma_cma
                    FROM assessments
                    WHERE id_student = ?
                    AND score IS NOT NULL
                    AND weight IS NOT NULL
                    AND weight > 0
                    AND assessment_type IN ('TMA', 'CMA')
                """, (student_id,))
                
            tma_data = cursor.fetchone()
            
            # Get OES (Overall Examination Score)
            cursor.execute("""
                SELECT score as oes
                FROM assessments
                WHERE id_student = ?
                AND assessment_type = 'Exam'
                AND score IS NOT NULL
                LIMIT 1
            """, (student_id,))
            exam_data = cursor.fetchone()
            
            # Extract values
            ocas = tma_data['ocas'] if tma_data and tma_data['ocas'] else 0
            oes = exam_data['oes'] if exam_data and exam_data['oes'] else None
            total_assessments = tma_data['total_tma_cma'] if tma_data else 0
            
            # For display purposes, show the component scores
            # Note: Student passes ONLY if BOTH OCAS ≥ 40 AND OES ≥ 40
            assessment_avg_score = ocas  # Show OCAS as the primary score
            exam_score = oes
            
            # Use student table data as fallback (for backward compatibility)
            student_dict = dict(student)
            primary_avg_score = assessment_avg_score or quiz_avg_score
            primary_progress = course_progress if total_courses > 0 else 0
            risk_probability = student_dict.get('risk_probability', 0) or 0


            
            return {
                'student': student_dict,
                'courses': [dict(course) for course in courses],
                'quiz_results': [dict(quiz) for quiz in quiz_results],
                'forum_posts_count': forum_posts,
                'recent_chats': [dict(chat) for chat in chat_history],
                'stats': {
                    # Course-based stats
                    'total_courses': total_courses,
                    'total_lessons': total_lessons,
                    'completed_lessons': total_completed_lessons,
                    'course_progress': course_progress,
                    'total_quizzes': len(quiz_results),
                    'passed_quizzes': passed_quizzes,
                    'quiz_avg_score': quiz_avg_score,
                    'forum_activity': forum_posts,
                    
                    # Primary stats (from student table or calculated)
                    'overall_progress': primary_progress,
                    'avg_score': primary_avg_score,
                    'risk_probability': risk_probability,
                    'days_active': days_active,
                    'num_days_active': days_active,  # Alias for compatibility
                    'total_clicks': total_clicks,  # Original name from activities
                    'total_engagement': total_clicks,  # Alias for compatibility
                    'is_at_risk': student_dict.get('is_at_risk', 0),
                    
                    # Academic status
                    'has_course_data': total_courses > 0,
                    'has_quiz_data': len(quiz_results) > 0,
                    'has_oulad_data': bool(primary_avg_score or days_active or total_clicks)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get student full context: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def get_chat_history(self, student_id: int, limit: int = 10) -> List[Dict]:
        """Get recent chat history."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM (
                SELECT * FROM chat_history
                WHERE id_student = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ) AS recent
            ORDER BY timestamp ASC
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
    
    def get_student_courses(self, student_id: int) -> List[Dict]:
        """Get all courses enrolled by student."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, ce.progress_percent, ce.enrolled_at, ce.completed_at
            FROM courses c
            INNER JOIN course_enrollments ce ON c.id = ce.course_id
            WHERE ce.student_id = ?
            ORDER BY ce.enrolled_at DESC
        """, (student_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_student_learning_progress(self, student_id: int) -> Dict:
        """Get comprehensive learning progress for student."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get enrolled courses count
        cursor.execute("""
            SELECT COUNT(*) as total_courses,
                   SUM(CASE WHEN completed_at IS NOT NULL THEN 1 ELSE 0 END) as completed_courses,
                   AVG(progress_percent) as avg_progress
            FROM course_enrollments
            WHERE student_id = ?
        """, (student_id,))
        course_stats = dict(cursor.fetchone())
        
        # Get lesson completion stats
        cursor.execute("""
            SELECT COUNT(*) as total_lessons_accessed,
                   SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_lessons,
                   SUM(time_spent_minutes) as total_time_spent,
                   AVG(progress_percent) as avg_lesson_progress
            FROM student_progress
            WHERE student_id = ?
        """, (student_id,))
        lesson_stats = dict(cursor.fetchone())
        
        # Get recent activity
        cursor.execute("""
            SELECT activity_type, COUNT(*) as count, MAX(timestamp) as last_activity
            FROM activities
            WHERE id_student = ?
            GROUP BY activity_type
            ORDER BY count DESC
            LIMIT 5
        """, (student_id,))
        recent_activities = [dict(row) for row in cursor.fetchall()]
        
        return {
            **course_stats,
            **lesson_stats,
            'recent_activities': recent_activities
        }
    
    def get_student_activity_stats(self, student_id: int) -> Dict:
        """Aggregate VLE activity stats for a student."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_activities,
                COALESCE(SUM(clicks), 0) as total_clicks,
                COUNT(DISTINCT date) as active_days
            FROM activities
            WHERE id_student = ?
        """, (student_id,))
        
        row = cursor.fetchone()
        if not row:
            return {'total_activities': 0, 'total_clicks': 0, 'active_days': 0}
        return dict(row)
    
    def get_student_assessment_stats(self, student_id: int) -> Dict:
        """Aggregate assessment stats using OULAD Two-Component Rule."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Calculate OCAS (Overall Continuous Assessment Score)
        cursor.execute("""
            SELECT 
                COUNT(*) as total_tma_cma,
                SUM(score * weight) / 100.0 as ocas
            FROM assessments
            WHERE id_student = ?
            AND assessment_type IN ('TMA', 'CMA')
            AND score IS NOT NULL
            AND weight IS NOT NULL
        """, (student_id,))
        
        ocas_row = cursor.fetchone()
        ocas = ocas_row['ocas'] if ocas_row and ocas_row['ocas'] is not None else 0
        total_tma_cma = ocas_row['total_tma_cma'] if ocas_row else 0
        
        # Calculate OES (Overall Exam Score)
        cursor.execute("""
            SELECT 
                COUNT(*) as total_exams,
                SUM(score * weight) / 100.0 as oes
            FROM assessments
            WHERE id_student = ?
            AND assessment_type = 'Exam'
            AND score IS NOT NULL
            AND weight IS NOT NULL
        """, (student_id,))
        
        oes_row = cursor.fetchone()
        oes = oes_row['oes'] if oes_row and oes_row['oes'] is not None else 0
        total_exams = oes_row['total_exams'] if oes_row else 0
        
        # OULAD Two-Component Rule: Pass IF (OCAS ≥ 40) AND (OES ≥ 40)
        passes_rule = (ocas >= 40) and (oes is not None and oes >= 40)
        
        total_assessments = total_tma_cma + total_exams
        
        return {
            'total_assessments': total_assessments,
            'avg_score': ocas,  # Show OCAS as primary score
            'total_score': ocas,  # Legacy compatibility
            'ocas': ocas,  # Overall Continuous Assessment Score
            'oes': oes,  # Overall Examination Score
            'has_exam': oes is not None,
            'passes_oulad_rule': passes_rule
        }
    
    def get_student_quiz_performance(self, student_id: int) -> Dict:
        """Get student's quiz performance summary."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(DISTINCT quiz_id) as total_quizzes_taken,
                   AVG(score) as avg_score,
                   SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as quizzes_passed,
                   AVG(time_spent) as avg_time_spent
            FROM student_quiz_attempts
            WHERE student_id = ?
        """, (student_id,))
        
        result = cursor.fetchone()
        if result:
            return dict(result)
        return {
            'total_quizzes_taken': 0,
            'avg_score': 0,
            'quizzes_passed': 0,
            'avg_time_spent': 0
        }
    
    
    # ==================== Quiz System Methods ====================
    
    def create_quiz(self, course_id: int, title: str, **kwargs) -> int:
        """Create a new quiz."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO quizzes (course_id, lesson_id, title, description, 
                                duration_minutes, passing_score, max_attempts, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course_id,
            kwargs.get('lesson_id'),
            title,
            kwargs.get('description', ''),
            kwargs.get('duration_minutes', 30),
            kwargs.get('passing_score', 70.0),
            kwargs.get('max_attempts', 3),
            kwargs.get('is_active', 1)
        ))
        
        conn.commit()
        quiz_id = cursor.lastrowid
        logger.info(f"Created quiz {quiz_id}: {title}")
        return quiz_id
    
    def add_quiz_question(self, quiz_id: int, question_text: str, **kwargs) -> int:
        """Add a question to a quiz."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO quiz_questions (quiz_id, question_text, question_type, 
                                       points, explanation, question_order)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            quiz_id,
            question_text,
            kwargs.get('question_type', 'multiple_choice'),
            kwargs.get('points', 1.0),
            kwargs.get('explanation', ''),
            kwargs.get('question_order', 0)
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def add_quiz_answer(self, question_id: int, answer_text: str, is_correct: bool = False, **kwargs) -> int:
        """Add an answer option to a question."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO quiz_answers (question_id, answer_text, is_correct, answer_order)
            VALUES (?, ?, ?, ?)
        """, (
            question_id,
            answer_text,
            1 if is_correct else 0,
            kwargs.get('answer_order', 0)
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_quiz(self, quiz_id: int) -> Optional[Dict]:
        """Get quiz details."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        quiz = cursor.fetchone()
        
        if quiz:
            return dict(quiz)
        return None
    
    def get_quiz_questions(self, quiz_id: int) -> List[Dict]:
        """Get all questions for a quiz with their answers."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM quiz_questions 
            WHERE quiz_id = ? 
            ORDER BY question_order, id
        """, (quiz_id,))
        
        questions = [dict(row) for row in cursor.fetchall()]
        
        # Get answers for each question
        for question in questions:
            cursor.execute("""
                SELECT * FROM quiz_answers 
                WHERE question_id = ? 
                ORDER BY answer_order, id
            """, (question['id'],))
            question['answers'] = [dict(row) for row in cursor.fetchall()]
        
        return questions
    
    def start_quiz_attempt(self, student_id: int, quiz_id: int) -> int:
        """Start a new quiz attempt."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get attempt number
        cursor.execute("""
            SELECT COUNT(*) as count FROM student_quiz_attempts 
            WHERE student_id = ? AND quiz_id = ?
        """, (student_id, quiz_id))
        
        attempt_number = cursor.fetchone()['count'] + 1
        
        # Create attempt
        cursor.execute("""
            INSERT INTO student_quiz_attempts (student_id, quiz_id, attempt_number, started_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (student_id, quiz_id, attempt_number))
        
        conn.commit()
        attempt_id = cursor.lastrowid
        logger.info(f"Started quiz attempt {attempt_id} for student {student_id}")
        return attempt_id
    
    def submit_quiz_attempt(self, attempt_id: int, responses: List[Dict]) -> Dict:
        """Submit quiz attempt and calculate score."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get attempt info
        cursor.execute("""
            SELECT * FROM student_quiz_attempts WHERE id = ?
        """, (attempt_id,))
        attempt = dict(cursor.fetchone())
        
        # Get quiz info
        quiz = self.get_quiz(attempt['quiz_id'])
        questions = self.get_quiz_questions(attempt['quiz_id'])
        
        total_points = sum(q['points'] for q in questions)
        earned_points = 0.0
        
        # Process each response
        for response in responses:
            question_id = response['question_id']
            answer_id = response.get('answer_id')
            answer_text = response.get('answer_text', '')
            
            # Find the question
            question = next((q for q in questions if q['id'] == question_id), None)
            if not question:
                continue
            
            is_correct = 0
            points_earned = 0.0
            
            # Check if answer is correct
            if answer_id:
                correct_answer = next((a for a in question['answers'] if a['id'] == answer_id and a['is_correct']), None)
                if correct_answer:
                    is_correct = 1
                    points_earned = question['points']
                    earned_points += points_earned
            
            # Save response
            cursor.execute("""
                INSERT INTO student_quiz_responses 
                (attempt_id, question_id, answer_id, answer_text, is_correct, points_earned)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (attempt_id, question_id, answer_id, answer_text, is_correct, points_earned))
        
        # Calculate score percentage
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = 1 if score >= quiz['passing_score'] else 0
        
        # Update attempt
        cursor.execute("""
            UPDATE student_quiz_attempts 
            SET score = ?, total_points = ?, passed = ?, submitted_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (score, total_points, passed, attempt_id))
        
        conn.commit()
        
        logger.info(f"Submitted quiz attempt {attempt_id}: {score:.1f}% ({passed})")
        
        return {
            'attempt_id': attempt_id,
            'score': score,
            'total_points': total_points,
            'earned_points': earned_points,
            'passed': passed,
            'passing_score': quiz['passing_score']
        }
    
    def get_student_quiz_attempts(self, student_id: int, quiz_id: int = None) -> List[Dict]:
        """Get quiz attempts for a student."""
        conn = self.connect()
        cursor = conn.cursor()
        
        if quiz_id:
            cursor.execute("""
                SELECT * FROM student_quiz_attempts 
                WHERE student_id = ? AND quiz_id = ?
                ORDER BY started_at DESC
            """, (student_id, quiz_id))
        else:
            cursor.execute("""
                SELECT * FROM student_quiz_attempts 
                WHERE student_id = ?
                ORDER BY started_at DESC
            """, (student_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== Forum System Methods ====================
    
    def create_forum(self, course_id: int, title: str, description: str = '') -> int:
        """Create a forum for a course."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO forums (course_id, title, description)
            VALUES (?, ?, ?)
        """, (course_id, title, description))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_forum_replies(self, post_id: int) -> List[Dict]:
        """Get replies to a forum post."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Increment view count
        cursor.execute("""
            UPDATE forum_posts SET view_count = view_count + 1 WHERE id = ?
        """, (post_id,))
        
        cursor.execute("""
            SELECT fr.*, s.first_name, s.last_name, s.email
            FROM forum_replies fr
            JOIN students s ON fr.student_id = s.id_student
            WHERE fr.post_id = ?
            ORDER BY fr.is_solution DESC, fr.created_at ASC
        """, (post_id,))
        
        conn.commit()
        return [dict(row) for row in cursor.fetchall()]
    
    def add_forum_reaction(self, student_id: int, post_id: int = None, reply_id: int = None, reaction_type: str = "like") -> bool:
        """Add a reaction to a post or reply"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO forum_reactions (student_id, post_id, reply_id, reaction_type)
                VALUES (?, ?, ?, ?)
            """, (student_id, post_id, reply_id, reaction_type))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding forum reaction: {e}")
            return False
    
    def update_video_progress(self, student_id: int, course_id: int, lesson_id: int, 
                            watch_time: int, video_duration: int) -> bool:
        """Update video watch progress"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Calculate watch percentage
            watch_percentage = (watch_time / video_duration * 100) if video_duration > 0 else 0
            
            # Check if student must watch at least 80% to mark as complete
            can_complete = watch_percentage >= 80
            
            cursor.execute("""
                INSERT OR REPLACE INTO student_progress 
                (student_id, course_id, lesson_id, video_watch_time, video_duration, 
                 watch_percentage, completed, progress_percent, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                student_id, course_id, lesson_id, watch_time, video_duration,
                watch_percentage, can_complete, watch_percentage
            ))
            
            conn.commit()
            logger.info(f"Updated video progress: {watch_percentage:.1f}% watched, can_complete: {can_complete}")
            return True
        except Exception as e:
            logger.error(f"Error updating video progress: {e}")
            return False
    
    def can_mark_lesson_complete(self, student_id: int, lesson_id: int) -> Dict:
        """Check if student can mark lesson as complete based on video watch time"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Get lesson type and progress
            cursor.execute("""
                SELECT l.lesson_type, l.duration_minutes,
                       sp.video_watch_time, sp.video_duration, sp.watch_percentage
                FROM lessons l
                LEFT JOIN student_progress sp ON l.id = sp.lesson_id AND sp.student_id = ?
                WHERE l.id = ?
            """, (student_id, lesson_id))
            
            result = cursor.fetchone()
            if not result:
                return {"can_complete": False, "reason": "Lesson not found"}
            
            lesson_type = result['lesson_type']
            watch_percentage = result['watch_percentage'] or 0
            
            # For video lessons, require 80% watch time
            if lesson_type == 'video':
                if watch_percentage >= 80:
                    return {"can_complete": True, "watch_percentage": watch_percentage}
                else:
                    return {
                        "can_complete": False, 
                        "reason": f"Must watch at least 80% of video (currently {watch_percentage:.1f}%)",
                        "watch_percentage": watch_percentage
                    }
            else:
                # For non-video lessons (reading, quiz), allow immediate completion
                return {"can_complete": True, "watch_percentage": 100}
                
        except Exception as e:
            logger.error(f"Error checking lesson completion: {e}")
            return {"can_complete": False, "reason": "Error checking completion status"}

    def get_student_registration_info(self, student_id: int) -> Optional[Dict]:
        """Get registration timing information for student."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT sr.date_registration, sr.date_unregistration,
                   s.code_module, s.code_presentation
            FROM student_registration sr
            JOIN students s ON sr.id_student = s.id_student
            WHERE sr.id_student = ?
        """, (student_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_course_progress(self, student_id: int) -> Optional[Dict]:
        """Calculate course progress % based on current engagement vs total course length."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get student's module and presentation
        cursor.execute("""
            SELECT code_module, code_presentation, final_result
            FROM students
            WHERE id_student = ?
        """, (student_id,))
        
        student_row = cursor.fetchone()
        if not student_row:
            return None
        
        student_data = dict(student_row)
        
        # Get course length from original OULAD data (if available in a courses table)
        # For now, use typical Open University course length: 269 days for DDD
        # This could be enhanced by querying a courses table with actual length data
        course_length_map = {
            'AAA': 251, 'BBB': 252, 'CCC': 236,
            'DDD': 269, 'EEE': 153, 'FFF': 242, 'GGG': 262
        }
        
        course_length = course_length_map.get(student_data['code_module'], 269)
        
        # Get latest activity date (proxy for "current day" in course)
        cursor.execute("""
            SELECT MAX(date) as latest_day
            FROM activities
            WHERE id_student = ?
        """, (student_id,))
        
        activity_row = cursor.fetchone()
        current_day = dict(activity_row)['latest_day'] if activity_row else 0
        current_day = current_day or 0  # Handle None
        
        # Calculate progress
        progress_percent = min((current_day / course_length) * 100, 100) if course_length > 0 else 0
        
        return {
            'course_length': course_length,
            'current_day': current_day,
            'progress_percent': round(progress_percent, 1),
            'days_remaining': max(course_length - current_day, 0),
            'is_withdrawn': student_data['final_result'] == 'Withdrawn',
            'final_result': student_data['final_result']
        }
    
    def get_student_data_at_day(self, student_id: int, day: int) -> Dict:
        """
        Fetch student data as it would appear on a specific day of the course.
        Used for 'Time-Travel' risk prediction.
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # 1. Get Demographics (Static)
        cursor.execute("""
            SELECT gender, region, highest_education, imd_band, age_band, disability, num_of_prev_attempts
            FROM students WHERE id_student = ?
        """, (student_id,))
        demographics = dict(cursor.fetchone())
        
        # 2. Get Assessments submitted BEFORE or ON 'day'
        cursor.execute("""
            SELECT score, date_submitted
            FROM assessments
            WHERE id_student = ? 
            AND date_submitted <= ?
            AND score IS NOT NULL
        """, (student_id, day))
        assessments = cursor.fetchall()
        
        scores = [a['score'] for a in assessments]
        avg_score = sum(scores) / len(scores) if scores else 0
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        
        # 3. Get VLE Clicks BEFORE or ON 'day'
        cursor.execute("""
            SELECT SUM(clicks) as total_clicks, COUNT(DISTINCT date) as active_days, COUNT(DISTINCT resource_id) as unique_resources
            FROM activities
            WHERE id_student = ?
            AND date <= ?
        """, (student_id, day))
        vle_stats = cursor.fetchone()
        
        total_clicks = vle_stats['total_clicks'] if vle_stats['total_clicks'] else 0
        active_days = vle_stats['active_days'] if vle_stats['active_days'] else 0
        unique_resources = vle_stats['unique_resources'] if vle_stats['unique_resources'] else 0
        
        # Derived features
        avg_clicks_per_day = total_clicks / day if day > 0 else 0
        clicks_per_active_day = total_clicks / active_days if active_days > 0 else 0
        
        return {
            'demographics': demographics,
            'features': {
                'avg_score': avg_score,
                'min_score': min_score,
                'max_score': max_score,
                'total_clicks': total_clicks,
                'avg_clicks_per_day': avg_clicks_per_day,
                'num_days_active': active_days,
                'num_unique_resources': unique_resources,
                'clicks_per_active_day': clicks_per_active_day,
                'resource_diversity': unique_resources,
                'study_intensity': total_clicks,
                'submission_rate': 1.0, # Simplified
                'num_unregistrations': demographics['num_of_prev_attempts'],
                'registered_early': 0, # Placeholder
                'has_unregistrations': 0 # Placeholder
            }
        }
    
    def get_upcoming_assessments(self, student_id: int, current_day: Optional[int] = None) -> List[Dict]:
        """Get unsubmitted assessments with weights, sorted by due date.
           If current_day is provided, filters based on that day (Time-Travel).
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get student's module and presentation
        cursor.execute("""
            SELECT code_module, code_presentation
            FROM students
            WHERE id_student = ?
        """, (student_id,))
        
        student_row = cursor.fetchone()
        if not student_row:
            return []
        
        student_data = dict(student_row)
        
        # Get all assessments for this module/presentation
        cursor.execute("""
            SELECT ai.id_assessment, ai.assessment_type, ai.date as date_due, ai.weight
            FROM assessment_info ai
            WHERE ai.code_module = ? AND ai.code_presentation = ?
            ORDER BY ai.date ASC
        """, (student_data['code_module'], student_data['code_presentation']))
        
        all_assessments = [dict(row) for row in cursor.fetchall()]
        
        # Get submitted assessments
        # If simulation mode: Only count submissions BEFORE or ON current_day
        if current_day is not None:
            cursor.execute("""
                SELECT DISTINCT id_assessment
                FROM assessments
                WHERE id_student = ? AND date_submitted <= ?
            """, (student_id, current_day))
        else:
            cursor.execute("""
                SELECT DISTINCT id_assessment
                FROM assessments
                WHERE id_student = ?
            """, (student_id,))
        
        submitted_ids = {row['id_assessment'] for row in cursor.fetchall()}
        
        # Filter and status
        upcoming = []
        for assessment in all_assessments:
            # If submitted, it's not upcoming (unless we want to show history, but this function implies 'upcoming')
            # Actually, for the dashboard, we usually want to see what's NEXT.
            # But if we want to show "Overdue", we need to include unsubmitted past items.
            
            if assessment['id_assessment'] in submitted_ids:
                continue
                
            # It is unsubmitted (or submitted in future relative to sim day)
            assessment['is_high_weight'] = assessment['weight'] >= 20.0
            assessment['is_exam'] = assessment['assessment_type'] == 'Exam'
            
            # Determine status
            if current_day is not None and assessment['date_due'] is not None and assessment['date_due'] < current_day:
                assessment['status'] = 'Overdue'
            else:
                assessment['status'] = 'Upcoming'
                
            upcoming.append(assessment)
    
        return upcoming

    def get_course_progress(self, student_id: int, current_day: Optional[int] = None) -> Dict:
        """Get course progress stats. Respects simulation day."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get total course length (approximate or from presentation)
        # OULAD doesn't strictly define length, but usually ~269 days
        total_days = 269
        
        # Determine "now"
        if current_day is not None:
            days_elapsed = min(current_day, total_days)
        else:
            # Default to end of course for historical data
            days_elapsed = total_days
            
        progress_percentage = (days_elapsed / total_days) * 100
        
        # Get completed assessments count (respecting sim day)
        if current_day is not None:
            cursor.execute("""
                SELECT COUNT(DISTINCT id_assessment) as count
                FROM assessments
                WHERE id_student = ? AND date_submitted <= ?
            """, (student_id, current_day))
        else:
            cursor.execute("""
                SELECT COUNT(DISTINCT id_assessment) as count
                FROM assessments
                WHERE id_student = ?
            """, (student_id,))
            
        completed_assessments = cursor.fetchone()['count']
        
        return {
            "days_elapsed": days_elapsed,
            "total_days": total_days,
            "progress_percentage": round(progress_percentage, 1),
            "completed_assessments": completed_assessments
        }


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

