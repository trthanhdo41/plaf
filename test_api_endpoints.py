"""
Test API endpoints for PLAF LMS system.
Run FastAPI server first: uvicorn src.api.main:app --reload
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Health Check")
    logger.info("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        return False

def test_auth():
    """Test authentication endpoints"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Authentication")
    logger.info("=" * 60)
    
    try:
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "student@example.com",
            "password": "password123"
        })
        logger.info(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            student_id = data['student']['id_student']
            logger.info(f"✅ Logged in as: {data['student']['first_name']} {data['student']['last_name']}")
            logger.info(f"   Student ID: {student_id}")
            return True, student_id
        else:
            logger.error(f"❌ Login failed: {response.text}")
            return False, None
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        return False, None

def test_courses(student_id):
    """Test course endpoints"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Courses")
    logger.info("=" * 60)
    
    try:
        # Get all courses
        response = requests.get(f"{BASE_URL}/api/courses")
        logger.info(f"Get Courses Status: {response.status_code}")
        
        if response.status_code == 200:
            courses = response.json()['courses']
            logger.info(f"✅ Found {len(courses)} courses")
            
            if courses:
                course_id = courses[0]['id']
                logger.info(f"   First course: {courses[0]['title']}")
                
                # Get course detail
                response = requests.get(f"{BASE_URL}/api/courses/{course_id}?student_id={student_id}")
                if response.status_code == 200:
                    course_detail = response.json()
                    logger.info(f"✅ Course has {len(course_detail['lessons'])} lessons")
                    logger.info(f"   Overall progress: {course_detail['overall_progress']:.1f}%")
                    return True, course_id
        
        return False, None
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        return False, None

def test_quizzes(student_id, course_id):
    """Test quiz endpoints"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Quizzes")
    logger.info("=" * 60)
    
    try:
        # Get course quizzes
        response = requests.get(f"{BASE_URL}/api/courses/{course_id}/quizzes")
        logger.info(f"Get Quizzes Status: {response.status_code}")
        
        if response.status_code == 200:
            quizzes = response.json()['quizzes']
            logger.info(f"✅ Found {len(quizzes)} quiz(zes)")
            
            if quizzes:
                quiz_id = quizzes[0]['id']
                logger.info(f"   Quiz: {quizzes[0]['title']}")
                
                # Get quiz details
                response = requests.get(f"{BASE_URL}/api/quizzes/{quiz_id}")
                if response.status_code == 200:
                    quiz_data = response.json()
                    questions = quiz_data['questions']
                    logger.info(f"✅ Quiz has {len(questions)} questions")
                    
                    # Start quiz
                    response = requests.post(f"{BASE_URL}/api/quizzes/{quiz_id}/start?student_id={student_id}")
                    if response.status_code == 200:
                        attempt_id = response.json()['attempt_id']
                        logger.info(f"✅ Started quiz attempt ID: {attempt_id}")
                        
                        # Submit quiz (answer all correctly)
                        responses = []
                        for question in questions:
                            correct_answer = next((a for a in question['answers'] if a['is_correct']), None)
                            if correct_answer:
                                responses.append({
                                    "question_id": question['id'],
                                    "answer_id": correct_answer['id']
                                })
                        
                        response = requests.post(f"{BASE_URL}/api/quizzes/submit", json={
                            "attempt_id": attempt_id,
                            "responses": responses
                        })
                        
                        if response.status_code == 200:
                            result = response.json()
                            logger.info(f"✅ Quiz submitted!")
                            logger.info(f"   Score: {result['score']:.1f}%")
                            logger.info(f"   Passed: {result['passed']}")
                            return True
        
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_forums(student_id, course_id):
    """Test forum endpoints"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Forums")
    logger.info("=" * 60)
    
    try:
        # Get course forums
        response = requests.get(f"{BASE_URL}/api/courses/{course_id}/forums")
        logger.info(f"Get Forums Status: {response.status_code}")
        
        if response.status_code == 200:
            forums = response.json()['forums']
            logger.info(f"✅ Found {len(forums)} forum(s)")
            
            if forums:
                forum_id = forums[0]['id']
                
                # Create post
                response = requests.post(f"{BASE_URL}/api/forum-posts", json={
                    "forum_id": forum_id,
                    "student_id": student_id,
                    "title": "Need help with Python loops",
                    "content": "I'm having trouble understanding for loops. Can someone explain?"
                })
                
                if response.status_code == 200:
                    post_id = response.json()['post_id']
                    logger.info(f"✅ Created forum post ID: {post_id}")
                    
                    # Create reply
                    response = requests.post(f"{BASE_URL}/api/forum-replies", json={
                        "post_id": post_id,
                        "student_id": student_id,
                        "content": "For loops iterate over a sequence. Try starting with simple examples!"
                    })
                    
                    if response.status_code == 200:
                        reply_id = response.json()['reply_id']
                        logger.info(f"✅ Created reply ID: {reply_id}")
                        
                        # Get post with replies
                        response = requests.get(f"{BASE_URL}/api/forum-posts/{post_id}")
                        if response.status_code == 200:
                            post_data = response.json()
                            logger.info(f"✅ Retrieved post with {len(post_data['replies'])} reply/replies")
                            return True
        
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_progress_tracking(student_id, course_id):
    """Test progress tracking"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Progress Tracking")
    logger.info("=" * 60)
    
    try:
        # Get course detail to get lesson ID
        response = requests.get(f"{BASE_URL}/api/courses/{course_id}?student_id={student_id}")
        if response.status_code == 200:
            course_detail = response.json()
            lessons = course_detail['lessons']
            
            if lessons:
                lesson_id = lessons[0]['id']
                
                # Update progress
                response = requests.post(f"{BASE_URL}/api/courses/{course_id}/progress", json={
                    "student_id": student_id,
                    "lesson_id": lesson_id,
                    "completed": True,
                    "progress_percent": 100.0
                })
                
                if response.status_code == 200:
                    logger.info(f"✅ Updated progress for lesson {lesson_id}")
                    
                    # Get updated course detail
                    response = requests.get(f"{BASE_URL}/api/courses/{course_id}?student_id={student_id}")
                    if response.status_code == 200:
                        updated_detail = response.json()
                        logger.info(f"✅ Overall progress: {updated_detail['overall_progress']:.1f}%")
                        return True
        
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        return False

def main():
    """Run all API tests"""
    logger.info("\n" + "=" * 60)
    logger.info("PLAF LMS API ENDPOINT TESTS")
    logger.info("=" * 60)
    logger.info("\nMake sure FastAPI server is running:")
    logger.info("  uvicorn src.api.main:app --reload")
    logger.info("")
    
    results = {}
    
    # Test 1: Health check
    results['health'] = test_health_check()
    
    # Test 2: Authentication
    auth_success, student_id = test_auth()
    results['auth'] = auth_success
    
    if not student_id:
        logger.error("\n❌ Cannot continue without student_id")
        return 1
    
    # Test 3: Courses
    courses_success, course_id = test_courses(student_id)
    results['courses'] = courses_success
    
    if not course_id:
        logger.error("\n❌ Cannot continue without course_id")
        return 1
    
    # Test 4: Quizzes
    results['quizzes'] = test_quizzes(student_id, course_id)
    
    # Test 5: Forums
    results['forums'] = test_forums(student_id, course_id)
    
    # Test 6: Progress tracking
    results['progress'] = test_progress_tracking(student_id, course_id)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name.upper()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    logger.info(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 ALL API TESTS PASSED!\n")
        return 0
    else:
        logger.error(f"\n⚠️  {total_tests - passed_tests} test(s) failed.\n")
        return 1

if __name__ == "__main__":
    exit(main())
