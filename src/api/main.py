"""
FastAPI Backend for LMS Portal
Provides REST API endpoints for the Next.js frontend
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import sys
import os
import requests
import base64

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

class QuizCreate(BaseModel):
    course_id: int
    lesson_id: Optional[int] = None
    title: str
    description: str = ""
    duration_minutes: int = 30
    passing_score: float = 70.0
    max_attempts: int = 3

class QuizQuestion(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"
    points: float = 1.0
    explanation: str = ""
    answers: List[Dict]

class QuizSubmission(BaseModel):
    attempt_id: int
    responses: List[Dict]

class ForumPostCreate(BaseModel):
    forum_id: int
    student_id: int
    title: str
    content: str

class ForumReplyCreate(BaseModel):
    post_id: int
    student_id: int
    content: str

class CourseCreate(BaseModel):
    title: str
    description: str
    thumbnail_url: Optional[str] = None
    instructor_name: str
    instructor_title: Optional[str] = None
    duration_hours: Optional[int] = None
    level: str = "Beginner"
    category: str
    code_module: Optional[str] = None
    course_code: Optional[str] = None

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    instructor_name: Optional[str] = None
    instructor_title: Optional[str] = None
    duration_hours: Optional[int] = None
    level: Optional[str] = None
    category: Optional[str] = None
    code_module: Optional[str] = None
    course_code: Optional[str] = None

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
        
        # Get quiz performance data
        quiz_perf = db.get_student_quiz_performance(student_id)
        
        # Calculate pass rate (only if there are quizzes taken)
        total_quizzes = quiz_perf.get('total_quizzes_taken', 0)
        quizzes_passed = quiz_perf.get('quizzes_passed', 0)
        pass_rate = (quizzes_passed / total_quizzes * 100) if total_quizzes > 0 else 0
        
        # Add quiz stats to student object
        student['quiz_completed'] = total_quizzes
        student['pass_rate'] = pass_rate
        student['avg_quiz_score'] = quiz_perf.get('avg_score', 0)
        
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
        # Use database method instead of direct connection
        db.update_student_progress(
            student_id=progress_data.student_id,
            course_id=course_id,
            lesson_id=progress_data.lesson_id,
            progress_percent=progress_data.progress_percent,
            completed=progress_data.completed
        )
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to update progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lessons/{lesson_id}/video-progress")
async def update_video_progress(lesson_id: int, request: dict):
    """Update video watch progress for a lesson"""
    try:
        student_id = request.get('student_id')
        watch_time = request.get('watch_time', 0)
        video_duration = request.get('video_duration', 0)
        watch_percentage = request.get('watch_percentage', 0)
        
        db.update_video_progress(
            student_id=student_id,
            lesson_id=lesson_id,
            watch_time=watch_time,
            video_duration=video_duration,
            watch_percentage=watch_percentage
        )
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lessons/{lesson_id}/video-progress/{student_id}")
async def get_video_progress(lesson_id: int, student_id: int):
    """Get video watch progress for a lesson"""
    try:
        progress = db.get_video_progress(student_id, lesson_id)
        return {"progress": progress}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== QUIZ ENDPOINTS ====================

@app.get("/api/lessons/{lesson_id}/quiz")
async def get_lesson_quiz(lesson_id: int):
    """Get quiz for a lesson"""
    try:
        quiz = db.get_lesson_quiz(lesson_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="No quiz found for this lesson")
        return {"quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/quiz/{quiz_id}/submit")
async def submit_quiz(quiz_id: int, request: dict):
    """Submit quiz answers and calculate score"""
    try:
        student_id = request.get('student_id')
        lesson_id = request.get('lesson_id')
        answers = request.get('answers', {})
        score = request.get('score', 0)
        passed = request.get('passed', False)
        time_taken = request.get('time_taken')
        
        # Save quiz result
        result_id = db.save_quiz_result(
            student_id=student_id,
            quiz_id=quiz_id,
            lesson_id=lesson_id,
            answers=answers,
            score=score,
            passed=passed,
            time_taken=time_taken
        )
        
        return {"success": True, "result_id": result_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== FORUM ENDPOINTS ====================

@app.get("/api/lessons/{lesson_id}/forum")
async def get_lesson_forum(lesson_id: int):
    """Get forum posts for a lesson"""
    try:
        posts = db.get_forum_posts(lesson_id)
        return {"posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lessons/{lesson_id}/forum")
async def create_forum_post(lesson_id: int, request: dict):
    """Create a new forum post"""
    try:
        title = request.get('title')
        content = request.get('content')
        author_id = request.get('author_id')
        author = request.get('author')
        
        post_id = db.create_forum_post(
            lesson_id=lesson_id,
            title=title,
            content=content,
            author_id=author_id,
            author=author
        )
        
        return {"success": True, "post_id": post_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forum/posts/{post_id}/replies")
async def get_forum_replies(post_id: int):
    """Get replies for a forum post"""
    try:
        replies = db.get_forum_replies(post_id)
        return {"replies": replies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forum/posts/{post_id}/replies")
async def create_forum_reply(post_id: int, request: dict):
    """Create a reply to a forum post"""
    try:
        content = request.get('content')
        author_id = request.get('author_id')
        author = request.get('author')
        
        reply_id = db.create_forum_reply(
            post_id=post_id,
            content=content,
            author_id=author_id,
            author=author
        )
        
        return {"success": True, "reply_id": reply_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forum/posts/{post_id}/vote")
async def vote_forum_post(post_id: int, request: dict):
    """Vote on a forum post"""
    try:
        student_id = request.get('student_id')
        vote_type = request.get('vote_type')  # 'like' or 'dislike'
        
        db.vote_forum_post(post_id, student_id, vote_type)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lessons/{lesson_id}/user-votes/{student_id}")
async def get_user_votes(lesson_id: int, student_id: int):
    """Get user's votes for all posts in a lesson"""
    try:
        votes = db.get_user_votes_for_lesson(lesson_id, student_id)
        return {"votes": votes}
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
    """Chat with AI advisor using comprehensive student context"""
    try:
        if not rag_system:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        # Get complete student context from database
        full_context = db.get_student_full_context(request.student_id)
        
        if not full_context:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Build conversation context from recent chats
        conversation_summary = ""
        if full_context.get('recent_chats'):
            recent_topics = []
            for chat in full_context['recent_chats'][:3]:
                recent_topics.append(f"Q: {chat.get('message', '')[:100]}... A: {chat.get('response', '')[:100]}...")
            conversation_summary = "\n".join(recent_topics)
        
        # Chat with RAG system using full context
        result = rag_system.chat(
            request.message,
            student_data=full_context['student'],  # Keep for backward compatibility
            conversation_context=request.conversation_context or conversation_summary,
            full_context=full_context  # Pass complete context
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

# ==================== Quiz API Endpoints ====================

@app.post("/api/quizzes")
async def create_quiz(quiz_data: QuizCreate):
    """Create a new quiz"""
    try:
        quiz_id = db.create_quiz(
            course_id=quiz_data.course_id,
            title=quiz_data.title,
            lesson_id=quiz_data.lesson_id,
            description=quiz_data.description,
            duration_minutes=quiz_data.duration_minutes,
            passing_score=quiz_data.passing_score,
            max_attempts=quiz_data.max_attempts
        )
        return {"success": True, "quiz_id": quiz_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/quizzes/{quiz_id}/questions")
async def add_quiz_question(quiz_id: int, question_data: QuizQuestion):
    """Add a question to a quiz"""
    try:
        question_id = db.add_quiz_question(
            quiz_id=quiz_id,
            question_text=question_data.question_text,
            question_type=question_data.question_type,
            points=question_data.points,
            explanation=question_data.explanation
        )
        
        # Add answers
        for idx, answer in enumerate(question_data.answers):
            db.add_quiz_answer(
                question_id=question_id,
                answer_text=answer['text'],
                is_correct=answer.get('is_correct', False),
                answer_order=idx
            )
        
        return {"success": True, "question_id": question_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quizzes/{quiz_id}")
async def get_quiz(quiz_id: int):
    """Get quiz details with questions"""
    try:
        quiz = db.get_quiz(quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        questions = db.get_quiz_questions(quiz_id)
        
        return {
            "quiz": quiz,
            "questions": questions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/courses/{course_id}/quizzes")
async def get_course_quizzes(course_id: int):
    """Get all quizzes for a course"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM quizzes 
            WHERE course_id = ? AND is_active = 1
            ORDER BY created_at DESC
        """, (course_id,))
        quizzes = [dict(row) for row in cursor.fetchall()]
        return {"quizzes": quizzes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/quizzes/{quiz_id}/start")
async def start_quiz(quiz_id: int, student_id: int):
    """Start a quiz attempt"""
    try:
        # Check if student has attempts left
        quiz = db.get_quiz(quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        attempts = db.get_student_quiz_attempts(student_id, quiz_id)
        if len(attempts) >= quiz['max_attempts']:
            raise HTTPException(status_code=400, detail="Maximum attempts reached")
        
        attempt_id = db.start_quiz_attempt(student_id, quiz_id)
        return {"success": True, "attempt_id": attempt_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/quizzes/submit")
async def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get results"""
    try:
        result = db.submit_quiz_attempt(
            attempt_id=submission.attempt_id,
            responses=submission.responses
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/student/{student_id}/quiz-attempts")
async def get_student_quiz_attempts(student_id: int, quiz_id: Optional[int] = None):
    """Get student's quiz attempts"""
    try:
        attempts = db.get_student_quiz_attempts(student_id, quiz_id)
        return {"attempts": attempts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Forum API Endpoints ====================

@app.post("/api/forums")
async def create_forum(course_id: int, title: str, description: str = ""):
    """Create a forum for a course"""
    try:
        forum_id = db.create_forum(course_id, title, description)
        return {"success": True, "forum_id": forum_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/courses/{course_id}/forums")
async def get_course_forums(course_id: int):
    """Get all forums for a course"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM forums 
            WHERE course_id = ? AND is_active = 1
            ORDER BY created_at DESC
        """, (course_id,))
        forums = [dict(row) for row in cursor.fetchall()]
        return {"forums": forums}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forum-posts")
async def create_forum_post(post_data: ForumPostCreate):
    """Create a new forum post"""
    try:
        post_id = db.create_forum_post(
            forum_id=post_data.forum_id,
            student_id=post_data.student_id,
            title=post_data.title,
            content=post_data.content
        )
        return {"success": True, "post_id": post_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forums/{forum_id}/posts")
async def get_forum_posts(forum_id: int, limit: int = 50):
    """Get posts in a forum"""
    try:
        posts = db.get_forum_posts(forum_id, limit)
        return {"posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forum-posts/{post_id}")
async def get_forum_post(post_id: int):
    """Get a forum post with replies"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT fp.*, s.first_name, s.last_name, s.email
            FROM forum_posts fp
            JOIN students s ON fp.student_id = s.id_student
            WHERE fp.id = ?
        """, (post_id,))
        
        post = cursor.fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post = dict(post)
        replies = db.get_forum_replies(post_id)
        
        return {
            "post": post,
            "replies": replies
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forum-replies")
async def create_forum_reply(reply_data: ForumReplyCreate):
    """Create a reply to a forum post"""
    try:
        reply_id = db.create_forum_reply(
            post_id=reply_data.post_id,
            student_id=reply_data.student_id,
            content=reply_data.content
        )
        return {"success": True, "reply_id": reply_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forum-reactions")
async def add_forum_reaction(student_id: int, post_id: Optional[int] = None, reply_id: Optional[int] = None, reaction_type: str = "like"):
    """Add a reaction to a post or reply"""
    try:
        success = db.add_forum_reaction(student_id, post_id, reply_id, reaction_type)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Image Upload ====================

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image to ImgBB and return URL"""
    try:
        # Get ImgBB API key from environment
        imgbb_api_key = os.getenv('IMGBB_API_KEY')
        if not imgbb_api_key:
            raise HTTPException(status_code=500, detail="ImgBB API key not configured")
        
        # Read file content
        file_content = await file.read()
        
        # Convert to base64
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Upload to ImgBB
        url = "https://api.imgbb.com/1/upload"
        payload = {
            'key': imgbb_api_key,
            'image': file_base64,
            'name': file.filename
        }
        
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                image_url = result['data']['url']
                return {
                    "success": True,
                    "url": image_url,
                    "filename": file.filename,
                    "size": len(file_content)
                }
            else:
                raise HTTPException(status_code=400, detail="Failed to upload image to ImgBB")
        else:
            raise HTTPException(status_code=400, detail=f"ImgBB API error: {response.status_code}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ==================== Admin Course Management ====================

@app.post("/api/admin/courses")
async def create_course(course_data: CourseCreate):
    """Admin: Create a new course"""
    try:
        conn = db.connect()
        cursor = conn.cursor()

        # Auto-generate unique course_code if not provided
        course_code = course_data.course_code
        if not course_code:
            import re, random
            # Build initial code from title initials (e.g., Machine Learning Fundamentals -> MLF)
            initials = ''.join([w[0] for w in re.findall(r"[A-Za-z0-9]+", course_data.title)])[:6].upper()
            base = initials or "COURSE"
            # Ensure uniqueness by checking existing records
            attempt = 0
            candidate = base
            while True:
                cursor.execute("SELECT 1 FROM courses WHERE course_code = ?", (candidate,))
                if not cursor.fetchone():
                    break
                attempt += 1
                candidate = f"{base}-{attempt}"
            course_code = candidate

        cursor.execute("""
            INSERT INTO courses (title, description, thumbnail_url, instructor_name, 
                               instructor_title, duration_hours, level, category, code_module, course_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course_data.title, course_data.description, course_data.thumbnail_url,
            course_data.instructor_name, course_data.instructor_title,
            course_data.duration_hours, course_data.level, course_data.category,
            course_data.code_module, course_code
        ))
        
        course_id = cursor.lastrowid
        conn.commit()
        
        return {"success": True, "course_id": course_id, "course_code": course_code, "message": "Course created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/courses/{course_id}")
async def update_course(course_id: int, course_data: CourseUpdate):
    """Admin: Update a course"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Build dynamic update query
        updates = []
        values = []
        
        for field, value in course_data.dict(exclude_unset=True).items():
            updates.append(f"{field} = ?")
            values.append(value)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(course_id)
        query = f"UPDATE courses SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Course not found")
        
        conn.commit()
        return {"success": True, "message": "Course updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/courses/{course_id}")
async def delete_course(course_id: int):
    """Admin: Delete a course"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Check if course exists
        cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Delete related data first (lessons, enrollments, etc.)
        cursor.execute("DELETE FROM lessons WHERE course_id = ?", (course_id,))
        cursor.execute("DELETE FROM course_enrollments WHERE course_id = ?", (course_id,))
        cursor.execute("DELETE FROM student_progress WHERE course_id = ?", (course_id,))
        cursor.execute("DELETE FROM quizzes WHERE course_id = ?", (course_id,))
        cursor.execute("DELETE FROM forums WHERE course_id = ?", (course_id,))
        
        # Delete the course
        cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        
        conn.commit()
        return {"success": True, "message": "Course and related data deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PROACTIVE INTERVENTION ENDPOINTS
# ============================================================================

class InterventionRequest(BaseModel):
    student_id: int
    intervention_type: str
    risk_level: str
    triggered_by: str
    metadata: Optional[Dict] = None

class InterventionResponse(BaseModel):
    student_id: int
    intervention_id: str
    action_taken: str
    timestamp: str

@app.post("/api/interventions/trigger")
async def trigger_intervention(request: InterventionRequest):
    """
    Trigger a proactive intervention for a student
    Implementation of Proactive Intervention from SYSTEM_IMPROVEMENT_ANALYSIS.md
    """
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Log the intervention trigger
        cursor.execute("""
            INSERT INTO intervention_logs (
                student_id, intervention_type, risk_level, 
                triggered_by, metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (
            request.student_id,
            request.intervention_type,
            request.risk_level,
            request.triggered_by,
            str(request.metadata) if request.metadata else None
        ))
        
        intervention_id = cursor.lastrowid
        
        # Generate intervention strategy based on risk level and student data
        student_data = cursor.execute("""
            SELECT * FROM students WHERE id_student = ?
        """, (request.student_id,)).fetchone()
        
        if not student_data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Convert Row to dict
        student_dict = dict(student_data)
        
        # Create intervention response based on risk level
        intervention_strategy = generate_intervention_strategy(
            student_dict, request.risk_level, request.intervention_type
        )
        
        conn.commit()
        
        return {
            "success": True,
            "intervention_id": intervention_id,
            "strategy": intervention_strategy,
            "timestamp": "now"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interventions/student/{student_id}")
async def get_student_interventions(student_id: int, limit: int = 10):
    """Get intervention history for a student"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        interventions = cursor.execute("""
            SELECT * FROM intervention_logs 
            WHERE student_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (student_id, limit)).fetchall()
        
        return {
            "interventions": [dict(row) for row in interventions]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interventions/feedback")
async def record_intervention_feedback(
    intervention_id: int,
    effectiveness: int,  # 1-5 scale
    student_response: str,
    outcome: Optional[str] = None
):
    """
    Record feedback on intervention effectiveness
    Implementation of Closed-Loop Feedback from SYSTEM_IMPROVEMENT_ANALYSIS.md
    """
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO intervention_feedback (
                intervention_id, effectiveness_rating, 
                student_response, outcome, created_at
            ) VALUES (?, ?, ?, ?, datetime('now'))
        """, (intervention_id, effectiveness, student_response, outcome))
        
        conn.commit()
        
        return {"success": True, "message": "Feedback recorded"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_intervention_strategy(student_data, risk_level: str, intervention_type: str) -> Dict:
    """
    Generate intervention strategy based on student data and risk level
    Implementation of Multi-Level Intervention from SYSTEM_IMPROVEMENT_ANALYSIS.md
    """
    risk_probability = student_data.get('risk_probability', 0)
    avg_score = student_data.get('avg_score', 0)
    num_days_active = student_data.get('num_days_active', 0)
    
    strategies = []
    
    # High Risk (70-85%+)
    if risk_probability >= 0.7:
        strategies.extend([
            {
                "type": "urgent_advisor",
                "title": "Immediate AI Advisor Support",
                "description": "High risk detected. Immediate personalized guidance recommended.",
                "priority": "critical",
                "action": "chat_now"
            },
            {
                "type": "human_escalation",
                "title": "Human Advisor Notification",
                "description": "Academic advisor has been notified for additional support.",
                "priority": "high",
                "action": "advisor_contact"
            }
        ])
        
        if avg_score and avg_score < 50:
            strategies.append({
                "type": "intensive_study",
                "title": "Intensive Study Plan",
                "description": "Customized study plan with additional resources.",
                "priority": "high",
                "action": "study_plan"
            })
    
    # Medium Risk (40-70%)
    elif risk_probability >= 0.4:
        strategies.extend([
            {
                "type": "preventive_support",
                "title": "Preventive Academic Support",
                "description": "Early intervention to prevent risk escalation.",
                "priority": "medium",
                "action": "preventive_chat"
            },
            {
                "type": "progress_review",
                "title": "Progress Review Session",
                "description": "Review current progress and identify improvement areas.",
                "priority": "medium",
                "action": "progress_review"
            }
        ])
    
    # Low engagement specific interventions
    if num_days_active and num_days_active < 30:
        strategies.append({
            "type": "engagement_boost",
            "title": "Engagement Recovery Program",
            "description": "Structured plan to increase learning engagement.",
            "priority": "high" if risk_probability >= 0.7 else "medium",
            "action": "engagement_plan"
        })
    
    return {
        "risk_level": risk_level,
        "strategies": strategies,
        "auto_generated": True,
        "timestamp": "now"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

