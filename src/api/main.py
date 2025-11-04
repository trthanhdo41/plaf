"""
FastAPI Backend for LMS Portal
Provides REST API endpoints for the Next.js frontend
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import sys
import os

# Add project root to path (for absolute imports)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.models import get_db
from src.chatbot.rag_system import RAGSystem
from src.prescriptive.llm_advisor import LLMAdvisor

app = FastAPI(title="PLAF LMS API", version="1.0.0")

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = get_db()
rag_system = None
llm_advisor = None

@app.on_event("startup")
async def startup_event():
    """Initialize AI services on startup"""
    global rag_system, llm_advisor
    try:
        rag_system = RAGSystem()
        llm_advisor = LLMAdvisor()
    except Exception as e:
        print(f"Warning: AI services not initialized: {e}")

# Request/Response Models
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

class ChatRequest(BaseModel):
    message: str
    student_id: int
    conversation_context: Optional[str] = None

class AdviceRequest(BaseModel):
    student_id: int

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "PLAF LMS API is running",
        "version": "1.0.0"
    }

@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    """Authenticate student"""
    try:
        student = db.authenticate_student(credentials.email, credentials.password)
        
        if not student:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {
            "success": True,
            "student": student
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/register")
async def register(data: RegisterRequest):
    """Register new student"""
    try:
        # Check if email exists
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id_student FROM students WHERE email = ?", (data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Create student
        student_id = db.create_student(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name
        )
        
        # Get student data
        student = db.get_student(student_id)
        
        return {
            "success": True,
            "student": student
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/student/{student_id}")
async def get_student(student_id: int):
    """Get student data and statistics"""
    try:
        student = db.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get activity data (simplified for now)
        activities = []
        assessments = []
        
        # Try to get real data if available
        try:
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM activities WHERE id_student = ? LIMIT 10", (student_id,))
            activities = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT * FROM assessments WHERE id_student = ? LIMIT 10", (student_id,))
            assessments = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.warning(f"Could not fetch activities/assessments: {e}")
        
        return {
            "student": student,
            "activities": activities,
            "assessments": assessments
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/student/{student_id}/courses")
async def get_student_courses(student_id: int):
    """Get student's enrolled courses"""
    try:
        courses = db.get_student_courses(student_id)
        return {"courses": courses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/student/{student_id}/materials")
async def get_course_materials(student_id: int):
    """Get course materials for student"""
    try:
        # Get student's course info
        student = db.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get materials from VLE table
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM vle 
            WHERE code_module = ? AND code_presentation = ?
            ORDER BY activity_type, week_from
            LIMIT 50
        """, (student.get('code_module'), student.get('code_presentation')))
        
        materials = [dict(row) for row in cursor.fetchall()]
        return {"materials": materials}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/courses")
async def get_all_courses():
    """Get all available courses"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM courses ORDER BY created_at DESC
        """)
        courses = [dict(row) for row in cursor.fetchall()]
        return {"courses": courses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/courses/{course_id}")
async def get_course_detail(course_id: int, student_id: int = None):
    """Get course detail with lessons"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get course info
        cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        course = cursor.fetchone()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        course = dict(course)
        
        # Get lessons
        cursor.execute("""
            SELECT * FROM lessons 
            WHERE course_id = ? 
            ORDER BY lesson_order ASC
        """, (course_id,))
        lessons = [dict(row) for row in cursor.fetchall()]
        
        # Get student progress if student_id provided
        progress = {}
        if student_id:
            cursor.execute("""
                SELECT lesson_id, completed, progress_percent, time_spent_minutes
                FROM student_progress
                WHERE student_id = ? AND course_id = ?
            """, (student_id, course_id))
            for row in cursor.fetchall():
                progress[row['lesson_id']] = dict(row)
        
        # Calculate overall progress
        total_lessons = len(lessons)
        completed_lessons = sum(1 for p in progress.values() if p.get('completed'))
        overall_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        return {
            "course": course,
            "lessons": lessons,
            "progress": progress,
            "overall_progress": overall_progress
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/courses/{course_id}/lessons/{lesson_id}")
async def get_lesson_detail(course_id: int, lesson_id: int):
    """Get lesson detail"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM lessons 
            WHERE id = ? AND course_id = ?
        """, (lesson_id, course_id))
        lesson = cursor.fetchone()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return {"lesson": dict(lesson)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProgressUpdate(BaseModel):
    student_id: int
    lesson_id: int
    completed: bool = False
    progress_percent: float = 0.0

@app.post("/api/courses/{course_id}/progress")
async def update_progress(course_id: int, progress_data: ProgressUpdate):
    """Update student progress for a lesson"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Insert or update progress
        cursor.execute("""
            INSERT INTO student_progress 
            (student_id, course_id, lesson_id, completed, progress_percent, last_accessed)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(student_id, lesson_id) 
            DO UPDATE SET
                completed = excluded.completed,
                progress_percent = excluded.progress_percent,
                last_accessed = CURRENT_TIMESTAMP,
                completed_at = CASE WHEN excluded.completed = 1 THEN CURRENT_TIMESTAMP ELSE completed_at END
        """, (progress_data.student_id, course_id, progress_data.lesson_id, 1 if progress_data.completed else 0, progress_data.progress_percent))
        
        conn.commit()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/courses/{course_id}/enroll")
async def enroll_course(course_id: int, student_id: int):
    """Enroll student in a course"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO course_enrollments (student_id, course_id)
            VALUES (?, ?)
        """, (student_id, course_id))
        conn.commit()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """Chat with AI advisor"""
    try:
        if not rag_system:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        # Get student data
        student = db.get_student(request.student_id)
        
        # Chat with RAG system
        result = rag_system.chat(
            request.message,
            student_data=student,
            conversation_context=request.conversation_context
        )
        
        # Save chat history
        db.save_chat_message(
            student_id=request.student_id,
            message=request.message,
            response=result['response']
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/student/{student_id}/chat-history")
async def get_chat_history(student_id: int, limit: int = 10):
    """Get chat history for student"""
    try:
        history = db.get_chat_history(student_id, limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/student/{student_id}/chat-history")
async def clear_chat_history(student_id: int):
    """Clear chat history for student"""
    try:
        db.clear_chat_history(student_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/advice")
async def get_ai_advice(request: AdviceRequest):
    """Get personalized advice from LLM"""
    try:
        if not llm_advisor:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        # Get student data
        student = db.get_student(request.student_id)
        
        # Generate advice
        advice = llm_advisor.generate_advice(student_data=student)
        
        return advice
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

