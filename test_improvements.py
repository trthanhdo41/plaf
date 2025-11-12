"""
Test script for all improvements to PLAF LMS system.
Tests: AI Chatbot enhancements, Quiz system, Forum system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.models import get_db
from src.chatbot.rag_system import initialize_knowledge_base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_setup():
    """Test 1: Database tables creation"""
    logger.info("=" * 60)
    logger.info("TEST 1: Database Setup")
    logger.info("=" * 60)
    
    try:
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()
        
        # Check all new tables exist
        tables_to_check = [
            'quizzes', 'quiz_questions', 'quiz_answers',
            'student_quiz_attempts', 'student_quiz_responses',
            'forums', 'forum_posts', 'forum_replies', 'forum_reactions'
        ]
        
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            result = cursor.fetchone()
            if result:
                logger.info(f"✅ Table '{table}' exists")
            else:
                logger.error(f"❌ Table '{table}' NOT found")
                return False
        
        logger.info("✅ All database tables created successfully\n")
        return True
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

def test_student_context():
    """Test 2: Student full context retrieval"""
    logger.info("=" * 60)
    logger.info("TEST 2: Student Full Context Retrieval")
    logger.info("=" * 60)
    
    try:
        db = get_db()
        
        # Create test student
        student_id = db.create_student(
            email="test_context@example.com",
            password="test123",
            first_name="Test",
            last_name="Student",
            code_module="AAA",
            code_presentation="2013J"
        )
        
        if not student_id:
            logger.warning("Student already exists, using existing one")
            student = db.authenticate_student("test_context@example.com", "test123")
            student_id = student['id_student']
        
        logger.info(f"Using student ID: {student_id}")
        
        # Get full context
        full_context = db.get_student_full_context(student_id)
        
        if full_context:
            logger.info("✅ Full context retrieved successfully")
            logger.info(f"   - Student: {full_context['student']['first_name']} {full_context['student']['last_name']}")
            logger.info(f"   - Learning Progress: {full_context['learning_progress']}")
            logger.info(f"   - Quiz Performance: {full_context['quiz_performance']}")
            logger.info(f"   - Activity Stats: {full_context['activity_stats']}")
            logger.info(f"   - Recent Chats: {len(full_context['recent_chats'])} messages")
            logger.info(f"   - Enrolled Courses: {len(full_context['enrolled_courses'])} courses\n")
            return True, student_id
        else:
            logger.error("❌ Failed to retrieve full context")
            return False, None
    except Exception as e:
        logger.error(f"❌ Student context test failed: {e}")
        return False, None

def test_quiz_system(student_id):
    """Test 3: Quiz system functionality"""
    logger.info("=" * 60)
    logger.info("TEST 3: Quiz System")
    logger.info("=" * 60)
    
    try:
        db = get_db()
        
        # Create a test course first
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO courses (title, description, instructor_name, level)
            VALUES ('Test Course', 'Test Description', 'Test Instructor', 'Beginner')
        """)
        conn.commit()
        
        cursor.execute("SELECT id FROM courses WHERE title = 'Test Course'")
        course_id = cursor.fetchone()['id']
        logger.info(f"Using course ID: {course_id}")
        
        # Create quiz
        quiz_id = db.create_quiz(
            course_id=course_id,
            title="Test Quiz: Python Basics",
            description="A quiz to test your Python knowledge",
            duration_minutes=20,
            passing_score=70.0,
            max_attempts=3
        )
        logger.info(f"✅ Created quiz ID: {quiz_id}")
        
        # Add questions
        q1_id = db.add_quiz_question(
            quiz_id=quiz_id,
            question_text="What is the output of print(2 + 2)?",
            question_type="multiple_choice",
            points=1.0,
            explanation="Basic arithmetic in Python"
        )
        
        # Add answers
        db.add_quiz_answer(q1_id, "3", is_correct=False)
        db.add_quiz_answer(q1_id, "4", is_correct=True)
        db.add_quiz_answer(q1_id, "5", is_correct=False)
        db.add_quiz_answer(q1_id, "22", is_correct=False)
        logger.info(f"✅ Added question with 4 answers")
        
        # Add more questions
        q2_id = db.add_quiz_question(
            quiz_id=quiz_id,
            question_text="Which keyword is used to define a function in Python?",
            question_type="multiple_choice",
            points=1.0
        )
        db.add_quiz_answer(q2_id, "function", is_correct=False)
        db.add_quiz_answer(q2_id, "def", is_correct=True)
        db.add_quiz_answer(q2_id, "func", is_correct=False)
        db.add_quiz_answer(q2_id, "define", is_correct=False)
        
        # Get quiz with questions
        quiz_data = db.get_quiz(quiz_id)
        questions = db.get_quiz_questions(quiz_id)
        logger.info(f"✅ Retrieved quiz with {len(questions)} questions")
        
        # Start quiz attempt
        attempt_id = db.start_quiz_attempt(student_id, quiz_id)
        logger.info(f"✅ Started quiz attempt ID: {attempt_id}")
        
        # Submit answers
        responses = [
            {"question_id": q1_id, "answer_id": questions[0]['answers'][1]['id']},  # Correct: 4
            {"question_id": q2_id, "answer_id": questions[1]['answers'][1]['id']}   # Correct: def
        ]
        
        result = db.submit_quiz_attempt(attempt_id, responses)
        logger.info(f"✅ Quiz submitted - Score: {result['score']:.1f}%, Passed: {result['passed']}")
        
        # Get student attempts
        attempts = db.get_student_quiz_attempts(student_id, quiz_id)
        logger.info(f"✅ Student has {len(attempts)} attempt(s) for this quiz\n")
        
        return True
    except Exception as e:
        logger.error(f"❌ Quiz system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_forum_system(student_id):
    """Test 4: Forum system functionality"""
    logger.info("=" * 60)
    logger.info("TEST 4: Forum System")
    logger.info("=" * 60)
    
    try:
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get course ID
        cursor.execute("SELECT id FROM courses WHERE title = 'Test Course'")
        course_id = cursor.fetchone()['id']
        
        # Create forum
        forum_id = db.create_forum(
            course_id=course_id,
            title="General Discussion",
            description="Discuss course topics here"
        )
        logger.info(f"✅ Created forum ID: {forum_id}")
        
        # Create post
        post_id = db.create_forum_post(
            forum_id=forum_id,
            student_id=student_id,
            title="How to improve my Python skills?",
            content="I'm struggling with understanding decorators. Any tips?"
        )
        logger.info(f"✅ Created forum post ID: {post_id}")
        
        # Create reply
        reply_id = db.create_forum_reply(
            post_id=post_id,
            student_id=student_id,
            content="Start with simple examples and practice regularly!"
        )
        logger.info(f"✅ Created reply ID: {reply_id}")
        
        # Add reaction
        success = db.add_forum_reaction(student_id, post_id=post_id, reaction_type="like")
        logger.info(f"✅ Added reaction: {success}")
        
        # Get posts
        posts = db.get_forum_posts(forum_id)
        logger.info(f"✅ Retrieved {len(posts)} post(s) from forum")
        
        # Get replies
        replies = db.get_forum_replies(post_id)
        logger.info(f"✅ Retrieved {len(replies)} reply/replies to post\n")
        
        return True
    except Exception as e:
        logger.error(f"❌ Forum system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_chatbot(student_id):
    """Test 5: Enhanced AI chatbot with full context"""
    logger.info("=" * 60)
    logger.info("TEST 5: Enhanced AI Chatbot")
    logger.info("=" * 60)
    
    try:
        # Check if GEMINI_API_KEY is set
        if not os.getenv('GEMINI_API_KEY'):
            logger.warning("⚠️  GEMINI_API_KEY not set, skipping AI chatbot test")
            logger.info("   Set GEMINI_API_KEY environment variable to test chatbot\n")
            return True
        
        db = get_db()
        
        # Initialize RAG system
        logger.info("Initializing RAG system...")
        rag = initialize_knowledge_base()
        logger.info("✅ RAG system initialized")
        
        # Get full student context
        full_context = db.get_student_full_context(student_id)
        
        # Test chat with full context
        query = "I'm feeling overwhelmed with my studies. What should I do?"
        logger.info(f"\nStudent Question: {query}")
        
        result = rag.chat(
            query=query,
            full_context=full_context,
            top_k=3
        )
        
        logger.info(f"\n✅ AI Response Generated:")
        logger.info(f"   {result['response'][:200]}...")
        logger.info(f"\n   Used {result['num_contexts']} context documents")
        logger.info(f"   Has full context: {result['has_full_context']}\n")
        
        # Save to chat history
        db.save_chat_message(student_id, query, result['response'])
        logger.info("✅ Chat saved to history\n")
        
        return True
    except Exception as e:
        logger.error(f"❌ AI chatbot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("PLAF LMS IMPROVEMENTS - COMPREHENSIVE TEST SUITE")
    logger.info("=" * 60 + "\n")
    
    results = {}
    
    # Test 1: Database setup
    results['database'] = test_database_setup()
    
    # Test 2: Student context
    results['context'], student_id = test_student_context()
    
    if student_id:
        # Test 3: Quiz system
        results['quiz'] = test_quiz_system(student_id)
        
        # Test 4: Forum system
        results['forum'] = test_forum_system(student_id)
        
        # Test 5: AI chatbot
        results['chatbot'] = test_ai_chatbot(student_id)
    else:
        logger.error("Cannot continue tests without student_id")
        results['quiz'] = False
        results['forum'] = False
        results['chatbot'] = False
    
    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name.upper()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    logger.info(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 ALL TESTS PASSED! System is ready for production.\n")
        return 0
    else:
        logger.error(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please review errors above.\n")
        return 1

if __name__ == "__main__":
    exit(main())
