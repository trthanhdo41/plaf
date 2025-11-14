"""
Seed sample data for PLAF LMS system.
Creates courses, lessons, quizzes, and forums with realistic content.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.models import get_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_courses():
    """Create sample courses"""
    logger.info("Creating sample courses...")
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    
    courses = [
        {
            'title': 'Python Programming for Beginners',
            'description': 'Learn Python from scratch with hands-on projects and quizzes',
            'thumbnail_url': '/images/python-course.jpg',
            'instructor_name': 'Dr. Sarah Johnson',
            'instructor_title': 'Senior Software Engineer',
            'duration_hours': 40,
            'level': 'Beginner',
            'category': 'Programming',
            'code_module': 'CCC',  # Map to OULAD module CCC
        },
        {
            'title': 'Web Development with React',
            'description': 'Build modern web applications using React and Next.js',
            'thumbnail_url': '/images/react-course.jpg',
            'instructor_name': 'Michael Chen',
            'instructor_title': 'Full Stack Developer',
            'duration_hours': 35,
            'level': 'Intermediate',
            'category': 'Web Development',
            'code_module': 'DDD',  # Map to OULAD module DDD
        },
        {
            'title': 'Data Science Fundamentals',
            'description': 'Master data analysis, visualization, and machine learning basics',
            'thumbnail_url': '/images/datascience-course.jpg',
            'instructor_name': 'Prof. Emily Rodriguez',
            'instructor_title': 'Data Science Lead',
            'duration_hours': 50,
            'level': 'Intermediate',
            'category': 'Data Science',
            'code_module': 'EEE',  # Map to OULAD module EEE
        }
    ]
    
    course_ids = []
    for course in courses:
        cursor.execute("""
            INSERT INTO courses (title, description, thumbnail_url, instructor_name, 
                               instructor_title, duration_hours, level, category, code_module)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course['title'], course['description'], course['thumbnail_url'],
            course['instructor_name'], course['instructor_title'],
            course['duration_hours'], course['level'], course['category'],
            course.get('code_module'),
        ))
        course_ids.append(cursor.lastrowid)
        logger.info(f"✅ Created course: {course['title']}")
    
    conn.commit()
    return course_ids

def seed_lessons(course_ids):
    """Create sample lessons for courses"""
    logger.info("\nCreating sample lessons...")
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    
    # Python course lessons
    python_lessons = [
        {'title': 'Introduction to Python', 'content': 'Learn Python basics and setup your environment', 'video_url': 'https://youtube.com/watch?v=example1', 'lesson_type': 'video', 'duration_minutes': 30, 'lesson_order': 1, 'is_free': 1},
        {'title': 'Variables and Data Types', 'content': 'Understanding variables, strings, numbers, and booleans', 'video_url': 'https://youtube.com/watch?v=example2', 'lesson_type': 'video', 'duration_minutes': 45, 'lesson_order': 2, 'is_free': 1},
        {'title': 'Control Flow', 'content': 'If statements, loops, and conditional logic', 'video_url': 'https://youtube.com/watch?v=example3', 'lesson_type': 'video', 'duration_minutes': 50, 'lesson_order': 3, 'is_free': 0},
        {'title': 'Functions and Modules', 'content': 'Creating reusable code with functions', 'video_url': 'https://youtube.com/watch?v=example4', 'lesson_type': 'video', 'duration_minutes': 60, 'lesson_order': 4, 'is_free': 0},
        {'title': 'Quiz: Python Basics', 'content': 'Test your knowledge of Python fundamentals', 'lesson_type': 'quiz', 'duration_minutes': 20, 'lesson_order': 5, 'is_free': 0},
    ]
    
    # React course lessons
    react_lessons = [
        {'title': 'React Fundamentals', 'content': 'Components, props, and state', 'video_url': 'https://youtube.com/watch?v=react1', 'lesson_type': 'video', 'duration_minutes': 40, 'lesson_order': 1, 'is_free': 1},
        {'title': 'Hooks and Effects', 'content': 'useState, useEffect, and custom hooks', 'video_url': 'https://youtube.com/watch?v=react2', 'lesson_type': 'video', 'duration_minutes': 55, 'lesson_order': 2, 'is_free': 0},
        {'title': 'Routing with React Router', 'content': 'Navigation and dynamic routes', 'video_url': 'https://youtube.com/watch?v=react3', 'lesson_type': 'video', 'duration_minutes': 45, 'lesson_order': 3, 'is_free': 0},
        {'title': 'State Management', 'content': 'Context API and Redux basics', 'video_url': 'https://youtube.com/watch?v=react4', 'lesson_type': 'video', 'duration_minutes': 70, 'lesson_order': 4, 'is_free': 0},
    ]
    
    # Data Science course lessons
    ds_lessons = [
        {'title': 'Introduction to Data Science', 'content': 'Overview of data science workflow', 'video_url': 'https://youtube.com/watch?v=ds1', 'lesson_type': 'video', 'duration_minutes': 35, 'lesson_order': 1, 'is_free': 1},
        {'title': 'Data Analysis with Pandas', 'content': 'DataFrames, filtering, and aggregation', 'video_url': 'https://youtube.com/watch?v=ds2', 'lesson_type': 'video', 'duration_minutes': 60, 'lesson_order': 2, 'is_free': 0},
        {'title': 'Data Visualization', 'content': 'Creating charts with Matplotlib and Seaborn', 'video_url': 'https://youtube.com/watch?v=ds3', 'lesson_type': 'video', 'duration_minutes': 50, 'lesson_order': 3, 'is_free': 0},
        {'title': 'Machine Learning Basics', 'content': 'Supervised and unsupervised learning', 'video_url': 'https://youtube.com/watch?v=ds4', 'lesson_type': 'video', 'duration_minutes': 75, 'lesson_order': 4, 'is_free': 0},
    ]
    
    all_lessons = [
        (course_ids[0], python_lessons),
        (course_ids[1], react_lessons),
        (course_ids[2], ds_lessons)
    ]
    
    lesson_ids_by_course = {}
    for course_id, lessons in all_lessons:
        lesson_ids = []
        for lesson in lessons:
            cursor.execute("""
                INSERT INTO lessons (course_id, title, content, video_url, lesson_type, 
                                   duration_minutes, lesson_order, is_free)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                course_id, lesson['title'], lesson['content'], lesson.get('video_url'),
                lesson['lesson_type'], lesson['duration_minutes'], 
                lesson['lesson_order'], lesson['is_free']
            ))
            lesson_ids.append(cursor.lastrowid)
        lesson_ids_by_course[course_id] = lesson_ids
        logger.info(f"✅ Created {len(lessons)} lessons for course {course_id}")
    
    conn.commit()
    return lesson_ids_by_course

def seed_quizzes(course_ids, lesson_ids_by_course):
    """Create sample quizzes"""
    logger.info("\nCreating sample quizzes...")
    db = get_db()
    
    # Python quiz
    python_quiz_id = db.create_quiz(
        course_id=course_ids[0],
        lesson_id=lesson_ids_by_course[course_ids[0]][4],  # Quiz lesson
        title="Python Basics Assessment",
        description="Test your understanding of Python fundamentals",
        duration_minutes=25,
        passing_score=70.0,
        max_attempts=3
    )
    
    # Question 1
    q1 = db.add_quiz_question(
        quiz_id=python_quiz_id,
        question_text="What is the correct way to create a variable in Python?",
        question_type="multiple_choice",
        points=1.0,
        explanation="In Python, you simply assign a value to a variable name",
        question_order=1
    )
    db.add_quiz_answer(q1, "var x = 5", is_correct=False, answer_order=1)
    db.add_quiz_answer(q1, "x = 5", is_correct=True, answer_order=2)
    db.add_quiz_answer(q1, "int x = 5", is_correct=False, answer_order=3)
    db.add_quiz_answer(q1, "let x = 5", is_correct=False, answer_order=4)
    
    # Question 2
    q2 = db.add_quiz_question(
        quiz_id=python_quiz_id,
        question_text="Which of the following is a mutable data type in Python?",
        question_type="multiple_choice",
        points=1.0,
        explanation="Lists are mutable, meaning they can be modified after creation",
        question_order=2
    )
    db.add_quiz_answer(q2, "String", is_correct=False, answer_order=1)
    db.add_quiz_answer(q2, "Tuple", is_correct=False, answer_order=2)
    db.add_quiz_answer(q2, "List", is_correct=True, answer_order=3)
    db.add_quiz_answer(q2, "Integer", is_correct=False, answer_order=4)
    
    # Question 3
    q3 = db.add_quiz_question(
        quiz_id=python_quiz_id,
        question_text="What does the 'def' keyword do in Python?",
        question_type="multiple_choice",
        points=1.0,
        explanation="'def' is used to define a function",
        question_order=3
    )
    db.add_quiz_answer(q3, "Defines a variable", is_correct=False, answer_order=1)
    db.add_quiz_answer(q3, "Defines a function", is_correct=True, answer_order=2)
    db.add_quiz_answer(q3, "Defines a class", is_correct=False, answer_order=3)
    db.add_quiz_answer(q3, "Defines a loop", is_correct=False, answer_order=4)
    
    logger.info(f"✅ Created Python quiz with 3 questions")
    
    # React quiz
    react_quiz_id = db.create_quiz(
        course_id=course_ids[1],
        title="React Fundamentals Quiz",
        description="Test your React knowledge",
        duration_minutes=20,
        passing_score=75.0,
        max_attempts=3
    )
    
    q1 = db.add_quiz_question(
        quiz_id=react_quiz_id,
        question_text="What is JSX?",
        question_type="multiple_choice",
        points=1.0,
        explanation="JSX is a syntax extension for JavaScript that looks like HTML",
        question_order=1
    )
    db.add_quiz_answer(q1, "A JavaScript library", is_correct=False)
    db.add_quiz_answer(q1, "A syntax extension for JavaScript", is_correct=True)
    db.add_quiz_answer(q1, "A CSS framework", is_correct=False)
    db.add_quiz_answer(q1, "A database", is_correct=False)
    
    q2 = db.add_quiz_question(
        quiz_id=react_quiz_id,
        question_text="Which hook is used for side effects?",
        question_type="multiple_choice",
        points=1.0,
        explanation="useEffect is used for side effects like API calls",
        question_order=2
    )
    db.add_quiz_answer(q2, "useState", is_correct=False)
    db.add_quiz_answer(q2, "useEffect", is_correct=True)
    db.add_quiz_answer(q2, "useContext", is_correct=False)
    db.add_quiz_answer(q2, "useReducer", is_correct=False)
    
    logger.info(f"✅ Created React quiz with 2 questions")
    
    return [python_quiz_id, react_quiz_id]

def seed_forums(course_ids):
    """Create sample forums"""
    logger.info("\nCreating sample forums...")
    db = get_db()
    
    forum_ids = []
    for course_id in course_ids:
        forum_id = db.create_forum(
            course_id=course_id,
            title="Course Discussion Forum",
            description="Ask questions and discuss course topics with fellow students"
        )
        forum_ids.append(forum_id)
        logger.info(f"✅ Created forum for course {course_id}")
    
    return forum_ids

def create_sample_student():
    """Create a sample student for testing"""
    logger.info("\nCreating sample student...")
    db = get_db()
    
    student_id = db.create_student(
        email="student@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
        code_module="AAA",
        code_presentation="2013J",
        gender="M",
        region="South East Region",
        highest_education="HE Qualification",
        age_band="25-35"
    )
    
    if student_id:
        logger.info(f"✅ Created sample student: student@example.com (ID: {student_id})")
        return student_id
    else:
        logger.info("ℹ️  Sample student already exists")
        student = db.authenticate_student("student@example.com", "password123")
        return student['id_student'] if student else None

def enroll_student_in_courses(student_id, course_ids):
    """Enroll student in all courses"""
    logger.info("\nEnrolling student in courses...")
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    
    for course_id in course_ids:
        cursor.execute("""
            INSERT OR IGNORE INTO course_enrollments (student_id, course_id, progress_percent)
            VALUES (?, ?, ?)
        """, (student_id, course_id, 0.0))
    
    conn.commit()
    logger.info(f"✅ Enrolled student in {len(course_ids)} courses")

def main():
    """Seed all sample data"""
    logger.info("\n" + "=" * 60)
    logger.info("SEEDING SAMPLE DATA FOR PLAF LMS")
    logger.info("=" * 60 + "\n")
    
    try:
        # Create courses
        course_ids = seed_courses()
        
        # Create lessons
        lesson_ids_by_course = seed_lessons(course_ids)
        
        # Create quizzes
        quiz_ids = seed_quizzes(course_ids, lesson_ids_by_course)
        
        # Create forums
        forum_ids = seed_forums(course_ids)
        
        # Create sample student
        student_id = create_sample_student()
        
        if student_id:
            # Enroll student
            enroll_student_in_courses(student_id, course_ids)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ SAMPLE DATA SEEDED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"\nCreated:")
        logger.info(f"  - {len(course_ids)} courses")
        logger.info(f"  - {sum(len(lessons) for lessons in lesson_ids_by_course.values())} lessons")
        logger.info(f"  - {len(quiz_ids)} quizzes")
        logger.info(f"  - {len(forum_ids)} forums")
        logger.info(f"\nTest credentials:")
        logger.info(f"  Email: student@example.com")
        logger.info(f"  Password: password123")
        logger.info("\n")
        
        return 0
    except Exception as e:
        logger.error(f"\n❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
