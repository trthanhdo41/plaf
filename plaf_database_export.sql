-- PLAF Learning Management System Database Export
-- Generated on: 2025-11-12 18:36:38.195030
-- Database: data/lms.db

-- ==================== SCHEMA ====================

-- Table: activities
CREATE TABLE activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_student INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                resource_id INTEGER,
                resource_type TEXT,
                clicks INTEGER DEFAULT 1,
                date INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_student) REFERENCES students(id_student)
            );

-- Table: assessments
CREATE TABLE assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_student INTEGER NOT NULL,
                id_assessment INTEGER NOT NULL,
                score REAL,
                submission_date INTEGER,
                is_late INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_student) REFERENCES students(id_student)
            );

-- Table: chat_history
CREATE TABLE chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_student INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                context TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_student) REFERENCES students(id_student)
            );

-- Table: course_enrollments
CREATE TABLE course_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            progress_percent REAL DEFAULT 0.0,
            completed_at TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id_student) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            UNIQUE(student_id, course_id)
        );

-- Table: course_materials
CREATE TABLE course_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_module TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                material_type TEXT,
                week INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

-- Table: courses
CREATE TABLE courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            thumbnail_url TEXT,
            instructor_name TEXT,
            instructor_title TEXT,
            duration_hours INTEGER,
            level TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

-- Table: forum_posts
CREATE TABLE forum_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        author_id INTEGER,
        author TEXT,
        is_pinned INTEGER DEFAULT 0,
        is_solved INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

-- Table: forum_reactions
CREATE TABLE forum_reactions (
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
            );

-- Table: forum_replies
CREATE TABLE forum_replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                is_solution INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(id_student) ON DELETE CASCADE
            );

-- Table: forum_reply_votes
CREATE TABLE forum_reply_votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reply_id INTEGER,
        student_id INTEGER,
        vote_type TEXT CHECK(vote_type IN ('like', 'dislike')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (reply_id) REFERENCES forum_replies (id),
        UNIQUE(reply_id, student_id)
    );

-- Table: forum_votes
CREATE TABLE forum_votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        student_id INTEGER,
        vote_type TEXT CHECK(vote_type IN ('like', 'dislike')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES forum_posts (id),
        UNIQUE(post_id, student_id)
    );

-- Table: forums
CREATE TABLE forums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            );

-- Table: interventions
CREATE TABLE interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_student INTEGER NOT NULL,
                intervention_type TEXT NOT NULL,
                description TEXT,
                advisor_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (id_student) REFERENCES students(id_student)
            );

-- Table: lessons
CREATE TABLE lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            video_url TEXT,
            lesson_type TEXT DEFAULT 'video',
            duration_minutes INTEGER,
            lesson_order INTEGER,
            is_free INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        );

-- Table: quiz_answers
CREATE TABLE quiz_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                answer_text TEXT NOT NULL,
                is_correct INTEGER DEFAULT 0,
                answer_order INTEGER DEFAULT 0,
                FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE
            );

-- Table: quiz_questions
CREATE TABLE quiz_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER,
        question_text TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option INTEGER NOT NULL,
        explanation TEXT,
        question_order INTEGER DEFAULT 1
    );

-- Table: quiz_results
CREATE TABLE quiz_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        quiz_id INTEGER,
        lesson_id INTEGER,
        answers TEXT,
        score REAL,
        passed INTEGER,
        time_taken INTEGER,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

-- Table: quizzes
CREATE TABLE quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        lesson_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        duration_minutes INTEGER DEFAULT 30,
        passing_score REAL DEFAULT 70.0,
        max_attempts INTEGER DEFAULT 3,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

-- Table: sqlite_sequence
CREATE TABLE sqlite_sequence(name,seq);

-- Table: student_assessments
CREATE TABLE student_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        assessment_title TEXT,
        score REAL,
        max_score REAL DEFAULT 100.0,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id_student)
    );

-- Table: student_progress
CREATE TABLE student_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            progress_percent REAL DEFAULT 0.0,
            time_spent_minutes INTEGER DEFAULT 0,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id_student) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
            UNIQUE(student_id, lesson_id)
        );

-- Table: student_quiz_attempts
CREATE TABLE student_quiz_attempts (
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
            );

-- Table: student_quiz_responses
CREATE TABLE student_quiz_responses (
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
            );

-- Table: students
CREATE TABLE students (
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
            , num_days_active INTEGER DEFAULT 0, total_clicks INTEGER DEFAULT 0, avg_score REAL DEFAULT 0.0);

-- Table: vle
CREATE TABLE "vle" (
"id_site" INTEGER,
  "code_module" TEXT,
  "code_presentation" TEXT,
  "activity_type" TEXT,
  "week_from" REAL,
  "week_to" REAL
);

-- ==================== SAMPLE DATA ====================

-- Data for table: activities
-- No data in activities

-- Data for table: assessments
INSERT INTO assessments (id, id_student, id_assessment, score, submission_date, is_late, timestamp) VALUES (1, 2, 1001, 78.0, 20240115, 0, '2025-10-21 03:11:26');
INSERT INTO assessments (id, id_student, id_assessment, score, submission_date, is_late, timestamp) VALUES (2, 2, 1002, 92.0, 20240210, 0, '2025-10-21 03:11:26');
INSERT INTO assessments (id, id_student, id_assessment, score, submission_date, is_late, timestamp) VALUES (3, 2, 1003, 88.0, 20240305, 0, '2025-10-21 03:11:26');
INSERT INTO assessments (id, id_student, id_assessment, score, submission_date, is_late, timestamp) VALUES (4, 2, 1004, 65.0, 20240320, 0, '2025-10-21 03:11:26');
INSERT INTO assessments (id, id_student, id_assessment, score, submission_date, is_late, timestamp) VALUES (5, 2, 1005, 95.0, 20240401, 0, '2025-10-21 03:11:26');

-- Data for table: chat_history
INSERT INTO chat_history (id, id_student, message, response, context, timestamp) VALUES (7, 9, 'heLLO', 'Hello! How can I help you today? Let''s work together to make sure you''re on track with your EEE course.

Based on our resources, remember that modules like FFF and GGG have a variety of VLE activities. For example, FFF has a lot of URLs, resources, oucontent, subpages and pages; while GGG includes resources, oucontent, quizzes, subpages and forums. Make sure you''re engaging with all of these different activity types. Also, remember the importance of time management - creating a study schedule and breaking down large tasks can really make a difference.
', 'materials_EEE', '2025-10-19 15:20:36');
INSERT INTO chat_history (id, id_student, message, response, context, timestamp) VALUES (8, 9, 'BẠN ƠI', 'Chào bạn! It''s great to hear from you again. How are your studies going? Remember we talked about focusing on completing all the activity types in your modules for a comprehensive learning experience.

Specifically, for Module FFF, there are a lot of URLs, resources, oucontent, subpages and pages to go through. For Module GGG, focus on the resources, oucontent, quizzes, subpages, and forumng activities. Breaking these down into smaller, manageable chunks in your study schedule will really help you stay on track. Time management is key, so make sure you''re scheduling time for each activity type. Don''t hesitate to reach out if you''re feeling stuck or overwhelmed. Good luck!
', 'materials_EEE', '2025-10-19 15:20:40');
INSERT INTO chat_history (id, id_student, message, response, context, timestamp) VALUES (9, 9, 'lúc nảy tôi vừa nhắn gì tôi quên rồi nhỉ bạn nói tiếng việt đi', 'Chào bạn! Đừng lo lắng, chuyện quên là bình thường thôi. Lúc nãy chúng ta đang trao đổi về cách bạn có thể tối ưu việc học tập môn EEE.

Để giúp bạn học tập hiệu quả hơn, hãy nhớ rằng môn GGG có nhiều loại hoạt động khác nhau như resource, oucontent, quiz, subpage và forumng. Môn FFF cũng có rất nhiều hoạt động như url, resource, oucontent, subpage và page. Cố gắng hoàn thành đầy đủ các loại hoạt động này để nắm vững kiến thức nhé. Bên cạnh đó, quản lý thời gian rất quan trọng, hãy lập kế hoạch học tập cụ thể và chia nhỏ các nhiệm vụ lớn để tránh bị choáng ngợp. Chúc bạn học tốt!
', 'materials_EEE', '2025-10-19 15:20:51');
INSERT INTO chat_history (id, id_student, message, response, context, timestamp) VALUES (10, 9, 'bạn nhớ được tôi vừa nhắn gì ko', 'Chào bạn! Có, tôi nhớ bạn vừa hỏi tôi có nhớ tin nhắn trước của bạn không.

I''m here to help you succeed in your EEE course! Based on the information I have about your modules, particularly GGG and FFF, you have a lot of different VLE activities to engage with. To ensure comprehensive learning, I''d recommend focusing on completing all the activity types (resource, oucontent, quiz, subpage, forumng for GGG; and url, resource, oucontent, subpage, page for FFF). Remember, breaking down large tasks is key to time management. Create a schedule and focus on smaller, manageable chunks of work.

Keep up the great work! I''m here to support you every step of the way. Don''t hesitate to ask if you have any more questions or need further guidance.
', 'materials_EEE', '2025-10-19 15:21:07');
INSERT INTO chat_history (id, id_student, message, response, context, timestamp) VALUES (18, 2, 'How can I improve my grades?', 'Hi Student650515 Demo! It''s truly commendable that you''re reaching out about improving your grades in Course DDD – that''s a fantastic first step, and it shows great determination. While I see you''re currently in an at-risk status, please know that it''s absolutely possible to turn things around, and I''m here to support you in making that happen. Your proactive attitude is a huge asset!

To start, let''s focus on some targeted strategies for Course DDD. I recommend you begin by reviewing your past assignments, quizzes, and any feedback you''ve received. Identifying specific areas where you''ve struggled – whether it''s particular concepts, problem-solving methods, or even test-taking strategies – will help us pinpoint where to focus your efforts. Don''t hesitate to reach out to your Course DDD instructor or TA during their office hours; they are often the best resource for clarifying difficult material and offering tailored advice. Additionally, explore any tutoring services or study groups available for DDD; learning from peers can be incredibly beneficial.

Beyond that, effective study habits are crucial. Try to move beyond passive reading by actively engaging with the material: quiz yourself, explain concepts aloud, and practice problem-solving regularly. Breaking down your study sessions into manageable chunks can also improve focus and retention. Remember, every step you take to understand the material better is progress. We can work together to build a plan that feels manageable and effective for you. Keep up this proactive attitude, and let''s get you back on track!', NULL, '2025-10-21T11:06:12.839268+07:00');
INSERT INTO chat_history (id, id_student, message, response, context, timestamp) VALUES (19, 16, 'How can I improve my Python skills?', 'I''m sorry, I encountered an error. Please try asking your question again.', NULL, '2025-11-11T15:43:35.632272+07:00');
INSERT INTO chat_history (id, id_student, message, response, context, timestamp) VALUES (20, 16, 'I just completed my first Python quiz and got 100%! What should I focus on next?', 'I''m sorry, I encountered an error. Please try asking your question again.', NULL, '2025-11-11T15:47:02.902199+07:00');
INSERT INTO chat_history (id, id_student, message, response, context, timestamp) VALUES (21, 16, 'I just completed my first Python quiz and got 100%! What should I focus on next to improve my skills?', 'I''m sorry, I encountered an error. Please try asking your question again.', NULL, '2025-11-11T15:50:51.953598+07:00');
INSERT INTO chat_history (id, id_student, message, response, context, timestamp) VALUES (22, 16, 'I just completed my first Python quiz and got 100%! What should I focus on next to improve my skills?', 'I''m sorry, I encountered an error. Please try asking your question again.', NULL, '2025-11-11T16:10:20.761731+07:00');
INSERT INTO chat_history (id, id_student, message, response, context, timestamp) VALUES (23, 16, 'I just completed my first Python quiz and got 100%! What should I focus on next to improve my skills?', 'That''s fantastic news, John! A perfect 100% on your very first Python quiz is an outstanding achievement and a testament to your understanding. Congratulations on such a strong start!

I see this is your first quiz taken across all your enrolled courses, and with your "Python Programming for Beginners" course currently at 0.0% complete, it''s clear you''re either a quick learner or you''ve come into the course with some prior knowledge, which is excellent. To truly build on this success and deepen your skills, your immediate next step should be to delve into the next lessons within your "Python Programming for Beginners" course. Focus on accessing the course materials, completing the lessons, and actively engaging with any provided coding exercises or practice problems.

This hands-on engagement with the course content beyond just the quizzes will be crucial for solidifying your understanding and preparing you for more complex topics. Keep up this incredible momentum, John! We''re here to support you every step of the way as you progress through your Python journey.', NULL, '2025-11-11T16:20:04.581213+07:00');

-- Data for table: course_enrollments
INSERT INTO course_enrollments (id, student_id, course_id, enrolled_at, progress_percent, completed_at) VALUES (1, 16, 4, '2025-11-11 08:40:04', 0.0, NULL);
INSERT INTO course_enrollments (id, student_id, course_id, enrolled_at, progress_percent, completed_at) VALUES (2, 16, 5, '2025-11-11 08:40:04', 0.0, NULL);
INSERT INTO course_enrollments (id, student_id, course_id, enrolled_at, progress_percent, completed_at) VALUES (3, 16, 6, '2025-11-11 08:40:04', 0.0, NULL);
INSERT INTO course_enrollments (id, student_id, course_id, enrolled_at, progress_percent, completed_at) VALUES (4, 11391, 1, '2025-11-12 08:57:11', 0.0, NULL);
INSERT INTO course_enrollments (id, student_id, course_id, enrolled_at, progress_percent, completed_at) VALUES (5, 11391, 2, '2025-11-12 08:57:11', 0.0, NULL);
INSERT INTO course_enrollments (id, student_id, course_id, enrolled_at, progress_percent, completed_at) VALUES (6, 11391, 4, '2025-11-12 08:57:11', 0.0, NULL);
INSERT INTO course_enrollments (id, student_id, course_id, enrolled_at, progress_percent, completed_at) VALUES (7, 17, 1, '2025-11-12 11:24:14', 0.0, NULL);
INSERT INTO course_enrollments (id, student_id, course_id, enrolled_at, progress_percent, completed_at) VALUES (8, 17, 4, '2025-11-12 11:24:14', 0.0, NULL);
INSERT INTO course_enrollments (id, student_id, course_id, enrolled_at, progress_percent, completed_at) VALUES (9, 17, 7, '2025-11-12 11:24:14', 0.0, NULL);

-- Data for table: course_materials
-- No data in course_materials

-- Data for table: courses
INSERT INTO courses (id, title, description, thumbnail_url, instructor_name, instructor_title, duration_hours, level, category, created_at) VALUES (1, 'Machine Learning Fundamentals', 'Learn the fundamentals of machine learning including supervised learning, unsupervised learning, and neural networks. Perfect for beginners!', NULL, 'Dr. Sarah Johnson', 'Senior Data Scientist', 12, 'Beginner', 'Data Science', '2025-11-04 03:19:02');
INSERT INTO courses (id, title, description, thumbnail_url, instructor_name, instructor_title, duration_hours, level, category, created_at) VALUES (2, 'Complete Web Development Bootcamp', 'Master modern web development with HTML, CSS, JavaScript, React, and Node.js. Build real-world projects!', NULL, 'Prof. Michael Chen', 'Full Stack Developer', 40, 'Intermediate', 'Web Development', '2025-11-04 03:19:02');
INSERT INTO courses (id, title, description, thumbnail_url, instructor_name, instructor_title, duration_hours, level, category, created_at) VALUES (4, 'Python Programming for Beginners', 'Learn Python from scratch with hands-on projects and quizzes', NULL, 'Dr. Sarah Johnson', 'Senior Software Engineer', 40, 'Beginner', 'Programming', '2025-11-11 08:40:04');
INSERT INTO courses (id, title, description, thumbnail_url, instructor_name, instructor_title, duration_hours, level, category, created_at) VALUES (5, 'Web Development with React', 'Build modern web applications using React and Next.js', NULL, 'Michael Chen', 'Full Stack Developer', 35, 'Intermediate', 'Web Development', '2025-11-11 08:40:04');
INSERT INTO courses (id, title, description, thumbnail_url, instructor_name, instructor_title, duration_hours, level, category, created_at) VALUES (6, 'Data Science Fundamentals', 'Master data analysis, visualization, and machine learning basics', NULL, 'Prof. Emily Rodriguez', 'Data Science Lead', 50, 'Intermediate', 'Data Science', '2025-11-11 08:40:04');
INSERT INTO courses (id, title, description, thumbnail_url, instructor_name, instructor_title, duration_hours, level, category, created_at) VALUES (7, 'JavaScript Fundamentals', 'Master JavaScript from basics to advanced concepts with practical examples', NULL, 'Alex Thompson', 'Senior Frontend Developer', 25, 'Beginner', 'Programming', '2025-11-12 08:33:01');

-- Data for table: forum_posts
INSERT INTO forum_posts (id, lesson_id, title, content, author_id, author, is_pinned, is_solved, created_at, updated_at) VALUES (1, 1, 'Welcome to JavaScript!', 'Welcome to the JavaScript Basics discussion forum!', 1, 'Instructor', 1, 0, '2025-11-12 10:34:03', '2025-11-12 10:34:03');
INSERT INTO forum_posts (id, lesson_id, title, content, author_id, author, is_pinned, is_solved, created_at, updated_at) VALUES (2, 1, 'Variable Question', 'What is the difference between var, let, and const?', 17, 'Demo Student', 0, 0, '2025-11-12 10:34:03', '2025-11-12 10:34:03');
INSERT INTO forum_posts (id, lesson_id, title, content, author_id, author, is_pinned, is_solved, created_at, updated_at) VALUES (3, 1, 'Test Discussion', 'This is a test post', 17, 'Demo Student', 0, 0, '2025-11-12 10:44:33', '2025-11-12 10:44:33');
INSERT INTO forum_posts (id, lesson_id, title, content, author_id, author, is_pinned, is_solved, created_at, updated_at) VALUES (4, 1, 'Another Test', 'Testing forum creation', 17, 'Demo Student', 0, 0, '2025-11-12 10:48:57', '2025-11-12 10:48:57');
INSERT INTO forum_posts (id, lesson_id, title, content, author_id, author, is_pinned, is_solved, created_at, updated_at) VALUES (5, 10, 'Welcome to Python!', 'Welcome to Python Programming discussion!', 1, 'Instructor', 0, 0, '2025-11-12 10:50:03', '2025-11-12 10:50:03');
INSERT INTO forum_posts (id, lesson_id, title, content, author_id, author, is_pinned, is_solved, created_at, updated_at) VALUES (6, 10, 'test', 'test', 17, 'Demo Student', 0, 0, '2025-11-12 10:53:59', '2025-11-12 10:53:59');
INSERT INTO forum_posts (id, lesson_id, title, content, author_id, author, is_pinned, is_solved, created_at, updated_at) VALUES (7, 10, 'Fresh Test Post', 'This is a brand new test post created right now', 17, 'Demo Student', 0, 0, '2025-11-12 11:00:34', '2025-11-12 11:00:34');
INSERT INTO forum_posts (id, lesson_id, title, content, author_id, author, is_pinned, is_solved, created_at, updated_at) VALUES (8, 10, 'New Test Right Now', 'Testing current timestamp', 17, 'Demo Student', 0, 0, '2025-11-12 18:01:11', '2025-11-12 18:01:11');

-- Data for table: forum_reactions
INSERT INTO forum_reactions (id, student_id, post_id, reply_id, reaction_type, created_at) VALUES (1, 15, 1, NULL, 'like', '2025-11-11 08:38:31');

-- Data for table: forum_replies
INSERT INTO forum_replies (id, post_id, student_id, content, is_solution, created_at, updated_at) VALUES (1, 1, 15, 'Start with simple examples and practice regularly!', 0, '2025-11-11 08:38:31', '2025-11-11 08:38:31');
INSERT INTO forum_replies (id, post_id, student_id, content, is_solution, created_at, updated_at) VALUES (2, 5, 17, 'This is a test reply', 0, '2025-11-12 10:57:36', '2025-11-12 10:57:36');

-- Data for table: forum_reply_votes
-- No data in forum_reply_votes

-- Data for table: forum_votes
INSERT INTO forum_votes (id, post_id, student_id, vote_type, created_at) VALUES (24, 6, 17, 'like', '2025-11-12 10:57:57');
INSERT INTO forum_votes (id, post_id, student_id, vote_type, created_at) VALUES (33, 5, 17, 'dislike', '2025-11-12 11:00:40');
INSERT INTO forum_votes (id, post_id, student_id, vote_type, created_at) VALUES (88, 7, 17, 'dislike', '2025-11-12 11:04:38');
INSERT INTO forum_votes (id, post_id, student_id, vote_type, created_at) VALUES (91, 8, 17, 'dislike', '2025-11-12 11:06:00');

-- Data for table: forums
INSERT INTO forums (id, course_id, title, description, is_active, created_at) VALUES (1, 3, 'General Discussion', 'Discuss course topics here', 1, '2025-11-11 08:38:31');
INSERT INTO forums (id, course_id, title, description, is_active, created_at) VALUES (2, 4, 'Course Discussion Forum', 'Ask questions and discuss course topics with fellow students', 1, '2025-11-11 08:40:04');
INSERT INTO forums (id, course_id, title, description, is_active, created_at) VALUES (3, 5, 'Course Discussion Forum', 'Ask questions and discuss course topics with fellow students', 1, '2025-11-11 08:40:04');
INSERT INTO forums (id, course_id, title, description, is_active, created_at) VALUES (4, 6, 'Course Discussion Forum', 'Ask questions and discuss course topics with fellow students', 1, '2025-11-11 08:40:04');

-- Data for table: interventions
-- No data in interventions

-- Data for table: lessons
INSERT INTO lessons (id, course_id, title, content, video_url, lesson_type, duration_minutes, lesson_order, is_free, created_at) VALUES (1, 1, 'Introduction to Machine Learning', '
# Introduction to Machine Learning

Welcome to Machine Learning Fundamentals! In this course, you''ll learn everything you need to know to get started with ML.

## What is Machine Learning?

Machine Learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.

## Key Concepts:

- **Supervised Learning**: Learning from labeled data
- **Unsupervised Learning**: Finding patterns in unlabeled data
- **Reinforcement Learning**: Learning through interaction and rewards

## Course Structure:

This course is divided into 5 modules:
1. Introduction (you are here!)
2. Supervised Learning Algorithms
3. Unsupervised Learning
4. Neural Networks
5. Practical Projects

Let''s get started! 🚀
            ', 'https://www.youtube.com/watch?v=W6NZfCO5SIk', 'video', 15, 1, 0, '2025-11-04 03:19:02');
INSERT INTO lessons (id, course_id, title, content, video_url, lesson_type, duration_minutes, lesson_order, is_free, created_at) VALUES (2, 1, 'Supervised Learning: Regression', '
# Supervised Learning: Regression

Regression is a fundamental supervised learning technique used to predict continuous values.

## Types of Regression:

1. **Linear Regression**: Predicts continuous values using a straight line
2. **Polynomial Regression**: Uses polynomial functions for non-linear relationships
3. **Ridge & Lasso Regression**: Regularized versions to prevent overfitting

## Example Use Cases:

- Predicting house prices
- Forecasting sales
- Estimating temperature

## Key Metrics:

- **Mean Squared Error (MSE)**: Average squared difference
- **R-squared**: Proportion of variance explained

Practice makes perfect! Try building your first regression model.
            ', 'https://www.youtube.com/watch?v=hdI2bqOjy3c', 'video', 20, 2, 0, '2025-11-04 03:19:02');
INSERT INTO lessons (id, course_id, title, content, video_url, lesson_type, duration_minutes, lesson_order, is_free, created_at) VALUES (3, 1, 'Supervised Learning: Classification', '
# Supervised Learning: Classification

Classification is used to predict categorical labels or classes.

## Common Algorithms:

1. **Logistic Regression**: For binary classification
2. **Decision Trees**: Easy to interpret
3. **Random Forest**: Ensemble of decision trees
4. **Support Vector Machines (SVM)**: Powerful for complex boundaries

## Evaluation Metrics:

- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-Score**: Harmonic mean of precision and recall

## Real-World Applications:

- Email spam detection
- Medical diagnosis
- Image recognition
            ', 'https://www.youtube.com/embed/HGTJBPNC-Gw?start=4', 'video', 25, 3, 0, '2025-11-04 03:19:02');
INSERT INTO lessons (id, course_id, title, content, video_url, lesson_type, duration_minutes, lesson_order, is_free, created_at) VALUES (4, 1, 'Unsupervised Learning: Clustering', '
# Unsupervised Learning: Clustering

Clustering groups similar data points together without labeled examples.

## Popular Algorithms:

1. **K-Means**: Partition data into k clusters
2. **Hierarchical Clustering**: Creates tree of clusters
3. **DBSCAN**: Density-based clustering

## Applications:

- Customer segmentation
- Image compression
- Anomaly detection

## Choosing the Right Algorithm:

- **K-Means**: When you know the number of clusters
- **Hierarchical**: When you want to explore relationships
- **DBSCAN**: For clusters of arbitrary shape
            ', 'https://www.youtube.com/embed/HGTJBPNC-Gw?start=4', 'video', 22, 4, 0, '2025-11-04 03:19:02');
INSERT INTO lessons (id, course_id, title, content, video_url, lesson_type, duration_minutes, lesson_order, is_free, created_at) VALUES (5, 1, 'Introduction to Neural Networks', '
# Introduction to Neural Networks

Neural networks are inspired by the human brain and form the foundation of deep learning.

## Architecture:

- **Input Layer**: Receives data
- **Hidden Layers**: Process information
- **Output Layer**: Produces predictions

## Key Concepts:

- **Activation Functions**: Sigmoid, ReLU, Tanh
- **Backpropagation**: Learning algorithm
- **Gradient Descent**: Optimization technique

## When to Use Neural Networks:

- Complex non-linear relationships
- Large datasets
- Image, text, or speech data

Ready to build your first neural network!
            ', 'https://www.youtube.com/embed/HGTJBPNC-Gw?start=4', 'video', 30, 5, 0, '2025-11-04 03:19:02');
INSERT INTO lessons (id, course_id, title, content, video_url, lesson_type, duration_minutes, lesson_order, is_free, created_at) VALUES (6, 2, 'HTML & CSS Basics', '
# HTML & CSS Basics

HTML and CSS are the building blocks of web development.

## HTML Structure:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Page</title>
</head>
<body>
    <h1>Hello World!</h1>
</body>
</html>
```

## CSS Styling:

```css
h1 {
    color: blue;
    font-size: 24px;
}
```

## Key Concepts:

- Semantic HTML
- CSS Selectors
- Flexbox and Grid
- Responsive Design

Start building beautiful websites!
            ', 'https://www.youtube.com/embed/HGTJBPNC-Gw?start=4', 'video', 30, 1, 0, '2025-11-04 03:19:02');
INSERT INTO lessons (id, course_id, title, content, video_url, lesson_type, duration_minutes, lesson_order, is_free, created_at) VALUES (7, 2, 'JavaScript Fundamentals', '
# JavaScript Fundamentals

JavaScript makes websites interactive and dynamic.

## Variables and Data Types:

```javascript
let name = "John";
const age = 25;
var isStudent = true;
```

## Functions:

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}
```

## Control Flow:

- if/else statements
- for loops
- while loops
- switch statements

Master these fundamentals to build amazing web apps!
            ', 'https://www.youtube.com/embed/HGTJBPNC-Gw?start=4', 'video', 35, 2, 0, '2025-11-04 03:19:02');
INSERT INTO lessons (id, course_id, title, content, video_url, lesson_type, duration_minutes, lesson_order, is_free, created_at) VALUES (8, 2, 'React: Building Modern UIs', '
# React: Building Modern UIs

React is a powerful library for building user interfaces.

## Components:

```jsx
function Welcome() {
    return <h1>Hello, React!</h1>;
}
```

## State Management:

```jsx
const [count, setCount] = useState(0);
```

## Key Features:

- Component-based architecture
- Virtual DOM
- Hooks (useState, useEffect)
- Props and State

Build interactive, reusable components!
            ', 'https://www.youtube.com/embed/HGTJBPNC-Gw?start=4', 'video', 40, 3, 0, '2025-11-04 03:19:02');
INSERT INTO lessons (id, course_id, title, content, video_url, lesson_type, duration_minutes, lesson_order, is_free, created_at) VALUES (9, 2, 'Node.js & Backend Development', '
# Node.js & Backend Development

Node.js allows you to build server-side applications with JavaScript.

## Creating a Server:

```javascript
const http = require(''http'');

const server = http.createServer((req, res) => {
    res.writeHead(200, {''Content-Type'': ''text/plain''});
    res.end(''Hello, World!'');
});

server.listen(3000);
```

## Express Framework:

- Routing
- Middleware
- RESTful APIs
- Database integration

Build powerful backend services!
            ', 'https://www.youtube.com/embed/HGTJBPNC-Gw?start=4', 'video', 45, 4, 0, '2025-11-04 03:19:02');
INSERT INTO lessons (id, course_id, title, content, video_url, lesson_type, duration_minutes, lesson_order, is_free, created_at) VALUES (10, 4, 'Introduction to Python', 'Learn Python basics and setup your environment', 'https://www.youtube.com/embed/HGTJBPNC-Gw?start=4', 'video', 30, 1, 1, '2025-11-11 08:40:04');

-- Data for table: quiz_answers
INSERT INTO quiz_answers (id, question_id, answer_text, is_correct, answer_order) VALUES (1, 1, '3', 0, 0);
INSERT INTO quiz_answers (id, question_id, answer_text, is_correct, answer_order) VALUES (2, 1, '4', 1, 0);
INSERT INTO quiz_answers (id, question_id, answer_text, is_correct, answer_order) VALUES (3, 1, '5', 0, 0);
INSERT INTO quiz_answers (id, question_id, answer_text, is_correct, answer_order) VALUES (4, 1, '22', 0, 0);
INSERT INTO quiz_answers (id, question_id, answer_text, is_correct, answer_order) VALUES (5, 2, 'function', 0, 0);
INSERT INTO quiz_answers (id, question_id, answer_text, is_correct, answer_order) VALUES (6, 2, 'def', 1, 0);
INSERT INTO quiz_answers (id, question_id, answer_text, is_correct, answer_order) VALUES (7, 2, 'func', 0, 0);
INSERT INTO quiz_answers (id, question_id, answer_text, is_correct, answer_order) VALUES (8, 2, 'define', 0, 0);
INSERT INTO quiz_answers (id, question_id, answer_text, is_correct, answer_order) VALUES (9, 3, 'var x = 5', 0, 1);
INSERT INTO quiz_answers (id, question_id, answer_text, is_correct, answer_order) VALUES (10, 3, 'x = 5', 1, 2);

-- Data for table: quiz_questions
INSERT INTO quiz_questions (id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, question_order) VALUES (1, 1, 'What is the correct way to declare a variable in JavaScript?', 'variable myVar = 5;', 'var myVar = 5;', 'v myVar = 5;', 'declare myVar = 5;', 1, 'The var keyword is used to declare variables in JavaScript.', 1);
INSERT INTO quiz_questions (id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, question_order) VALUES (2, 1, 'Which of the following is NOT a JavaScript data type?', 'String', 'Boolean', 'Float', 'Number', 2, 'JavaScript has Number type for all numeric values, not separate Float type.', 2);
INSERT INTO quiz_questions (id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, question_order) VALUES (3, 1, 'What does console.log() do?', 'Creates a new variable', 'Outputs information to the console', 'Deletes a variable', 'Creates a function', 1, 'console.log() is used to output information to the browser console for debugging.', 3);
INSERT INTO quiz_questions (id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, question_order) VALUES (4, 1, 'How do you write a comment in JavaScript?', '<!-- This is a comment -->', '/* This is a comment */', '// This is a comment', 'Both B and C are correct', 3, 'JavaScript supports both single-line (//) and multi-line (/* */) comments.', 4);
INSERT INTO quiz_questions (id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, question_order) VALUES (5, 1, 'What is the result of 5 + "5" in JavaScript?', '10', '55', 'Error', 'undefined', 1, 'JavaScript converts the number 5 to a string and concatenates, resulting in "55".', 5);

-- Data for table: quiz_results
INSERT INTO quiz_results (id, student_id, quiz_id, lesson_id, answers, score, passed, time_taken, submitted_at) VALUES (1, 17, 1, NULL, NULL, 85.0, 1, NULL, '2025-11-12 11:24:33');
INSERT INTO quiz_results (id, student_id, quiz_id, lesson_id, answers, score, passed, time_taken, submitted_at) VALUES (2, 17, 4, NULL, NULL, 72.0, 1, NULL, '2025-11-12 11:24:33');

-- Data for table: quizzes
INSERT INTO quizzes (id, course_id, lesson_id, title, description, duration_minutes, passing_score, max_attempts, is_active, created_at) VALUES (1, 7, 1, 'JavaScript Basics Quiz', 'Test your understanding of JavaScript fundamentals', 15, 70.0, 3, 1, '2025-11-12 10:13:24');
INSERT INTO quizzes (id, course_id, lesson_id, title, description, duration_minutes, passing_score, max_attempts, is_active, created_at) VALUES (2, 4, 10, 'Python Basics Quiz', 'Test your Python knowledge', 15, 70.0, 3, 1, '2025-11-12 11:08:16');
INSERT INTO quizzes (id, course_id, lesson_id, title, description, duration_minutes, passing_score, max_attempts, is_active, created_at) VALUES (3, 1, 1, 'Introduction to ML Quiz', 'Test your knowledge from this lesson', 15, 70.0, 3, 1, '2025-11-12 11:09:39');
INSERT INTO quizzes (id, course_id, lesson_id, title, description, duration_minutes, passing_score, max_attempts, is_active, created_at) VALUES (4, 1, 1, 'Introduction to ML Quiz', 'Test your knowledge from this lesson', 15, 70.0, 3, 1, '2025-11-12 11:09:55');
INSERT INTO quizzes (id, course_id, lesson_id, title, description, duration_minutes, passing_score, max_attempts, is_active, created_at) VALUES (5, 1, 2, 'Supervised Learning Quiz', 'Test your knowledge from this lesson', 15, 70.0, 3, 1, '2025-11-12 11:09:55');
INSERT INTO quizzes (id, course_id, lesson_id, title, description, duration_minutes, passing_score, max_attempts, is_active, created_at) VALUES (6, 1, 3, 'Classification Quiz', 'Test your knowledge from this lesson', 15, 70.0, 3, 1, '2025-11-12 11:09:55');
INSERT INTO quizzes (id, course_id, lesson_id, title, description, duration_minutes, passing_score, max_attempts, is_active, created_at) VALUES (7, 1, 4, 'Clustering Quiz', 'Test your knowledge from this lesson', 15, 70.0, 3, 1, '2025-11-12 11:09:55');
INSERT INTO quizzes (id, course_id, lesson_id, title, description, duration_minutes, passing_score, max_attempts, is_active, created_at) VALUES (8, 1, 5, 'Neural Networks Quiz', 'Test your knowledge from this lesson', 15, 70.0, 3, 1, '2025-11-12 11:09:55');
INSERT INTO quizzes (id, course_id, lesson_id, title, description, duration_minutes, passing_score, max_attempts, is_active, created_at) VALUES (9, 2, 6, 'HTML & CSS Quiz', 'Test your knowledge from this lesson', 15, 70.0, 3, 1, '2025-11-12 11:09:55');
INSERT INTO quizzes (id, course_id, lesson_id, title, description, duration_minutes, passing_score, max_attempts, is_active, created_at) VALUES (10, 2, 7, 'JavaScript Fundamentals Quiz', 'Test your knowledge from this lesson', 15, 70.0, 3, 1, '2025-11-12 11:09:55');

-- Data for table: sqlite_sequence
INSERT INTO sqlite_sequence (name, seq) VALUES ('chat_history', 39);
INSERT INTO sqlite_sequence (name, seq) VALUES ('assessments', 5);
INSERT INTO sqlite_sequence (name, seq) VALUES ('courses', 7);
INSERT INTO sqlite_sequence (name, seq) VALUES ('lessons', 26);
INSERT INTO sqlite_sequence (name, seq) VALUES ('student_progress', 7);
INSERT INTO sqlite_sequence (name, seq) VALUES ('quiz_answers', 28);
INSERT INTO sqlite_sequence (name, seq) VALUES ('student_quiz_attempts', 2);
INSERT INTO sqlite_sequence (name, seq) VALUES ('student_quiz_responses', 5);
INSERT INTO sqlite_sequence (name, seq) VALUES ('forums', 4);
INSERT INTO sqlite_sequence (name, seq) VALUES ('forum_replies', 2);

-- Data for table: student_assessments
INSERT INTO student_assessments (id, student_id, assessment_title, score, max_score, submitted_at) VALUES (1, 17, 'Quiz 1: JavaScript Basics', 85.0, 100.0, NULL);
INSERT INTO student_assessments (id, student_id, assessment_title, score, max_score, submitted_at) VALUES (2, 17, 'Assignment 1: Variables & Functions', 78.0, 100.0, NULL);
INSERT INTO student_assessments (id, student_id, assessment_title, score, max_score, submitted_at) VALUES (3, 17, 'Quiz 2: DOM Manipulation', 88.0, 100.0, NULL);
INSERT INTO student_assessments (id, student_id, assessment_title, score, max_score, submitted_at) VALUES (4, 17, 'Project 1: Interactive Website', 82.0, 100.0, NULL);
INSERT INTO student_assessments (id, student_id, assessment_title, score, max_score, submitted_at) VALUES (5, 17, 'Final Assessment', 79.0, 100.0, NULL);

-- Data for table: student_progress
INSERT INTO student_progress (id, student_id, course_id, lesson_id, completed, progress_percent, time_spent_minutes, last_accessed, completed_at) VALUES (1, 2, 1, 1, 1, 100.0, 0, '2025-11-04 04:12:11', NULL);
INSERT INTO student_progress (id, student_id, course_id, lesson_id, completed, progress_percent, time_spent_minutes, last_accessed, completed_at) VALUES (2, 16, 7, 23, 1, 100.0, 0, '2025-11-12 08:35:30', NULL);
INSERT INTO student_progress (id, student_id, course_id, lesson_id, completed, progress_percent, time_spent_minutes, last_accessed, completed_at) VALUES (3, 16, 7, 24, 1, 100.0, 0, '2025-11-12 08:35:43', NULL);
INSERT INTO student_progress (id, student_id, course_id, lesson_id, completed, progress_percent, time_spent_minutes, last_accessed, completed_at) VALUES (4, 17, 7, 23, 1, 100.0, 0, '2025-11-12 09:02:56', NULL);
INSERT INTO student_progress (id, student_id, course_id, lesson_id, completed, progress_percent, time_spent_minutes, last_accessed, completed_at) VALUES (5, 17, 4, 1, 1, 100.0, 0, '2025-11-12 09:03:44', NULL);
INSERT INTO student_progress (id, student_id, course_id, lesson_id, completed, progress_percent, time_spent_minutes, last_accessed, completed_at) VALUES (6, 17, 4, 10, 1, 100.0, 0, '2025-11-12 10:39:12', NULL);
INSERT INTO student_progress (id, student_id, course_id, lesson_id, completed, progress_percent, time_spent_minutes, last_accessed, completed_at) VALUES (7, 17, 4, 13, 1, 100.0, 0, '2025-11-12 10:39:16', NULL);

-- Data for table: student_quiz_attempts
INSERT INTO student_quiz_attempts (id, student_id, quiz_id, attempt_number, score, total_points, passed, time_spent, started_at, submitted_at) VALUES (1, 15, 1, 1, 100.0, 2.0, 1, 0, '2025-11-11 08:38:31', '2025-11-11 08:38:31');
INSERT INTO student_quiz_attempts (id, student_id, quiz_id, attempt_number, score, total_points, passed, time_spent, started_at, submitted_at) VALUES (2, 16, 2, 1, 100.0, 3.0, 1, 0, '2025-11-11 08:45:18', '2025-11-11 08:45:26');

-- Data for table: student_quiz_responses
INSERT INTO student_quiz_responses (id, attempt_id, question_id, answer_id, answer_text, is_correct, points_earned) VALUES (1, 1, 1, 2, '', 1, 1.0);
INSERT INTO student_quiz_responses (id, attempt_id, question_id, answer_id, answer_text, is_correct, points_earned) VALUES (2, 1, 2, 6, '', 1, 1.0);
INSERT INTO student_quiz_responses (id, attempt_id, question_id, answer_id, answer_text, is_correct, points_earned) VALUES (3, 2, 3, 10, '', 1, 1.0);
INSERT INTO student_quiz_responses (id, attempt_id, question_id, answer_id, answer_text, is_correct, points_earned) VALUES (4, 2, 4, 15, '', 1, 1.0);
INSERT INTO student_quiz_responses (id, attempt_id, question_id, answer_id, answer_text, is_correct, points_earned) VALUES (5, 2, 5, 18, '', 1, 1.0);

-- Data for table: students
INSERT INTO students (id_student, email, password_hash, first_name, last_name, code_module, code_presentation, gender, region, highest_education, imd_band, age_band, disability, final_result, is_at_risk, risk_probability, created_at, updated_at, num_days_active, total_clicks, avg_score) VALUES (1, 'student432862@ou.ac.uk', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'Student432862', 'Demo', 'DDD', '2013J', 'M', 'Unknown', 'Unknown', '10-20%', '35-55', 'N', NULL, 1, 0.2139877935660668, '2025-10-18 17:42:13', '2025-10-18 17:42:13', 0, 0, 0.0);
INSERT INTO students (id_student, email, password_hash, first_name, last_name, code_module, code_presentation, gender, region, highest_education, imd_band, age_band, disability, final_result, is_at_risk, risk_probability, created_at, updated_at, num_days_active, total_clicks, avg_score) VALUES (2, 'student650515@ou.ac.uk', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'Student650515', 'Demo', 'DDD', '2014J', 'M', 'Unknown', 'Unknown', '10-20%', '35-55', 'N', NULL, 1, 0.9994001205845237, '2025-10-18 17:42:13', '2025-10-18 17:42:13', 45, 1250, 85.5);
INSERT INTO students (id_student, email, password_hash, first_name, last_name, code_module, code_presentation, gender, region, highest_education, imd_band, age_band, disability, final_result, is_at_risk, risk_probability, created_at, updated_at, num_days_active, total_clicks, avg_score) VALUES (3, 'student2634238@ou.ac.uk', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'Student2634238', 'Demo', 'CCC', '2014B', 'M', 'Unknown', 'Unknown', '10-20%', '35-55', 'N', NULL, 1, 0.9998584787381628, '2025-10-18 17:42:13', '2025-10-18 17:42:13', 0, 0, 0.0);
INSERT INTO students (id_student, email, password_hash, first_name, last_name, code_module, code_presentation, gender, region, highest_education, imd_band, age_band, disability, final_result, is_at_risk, risk_probability, created_at, updated_at, num_days_active, total_clicks, avg_score) VALUES (4, 'student604655@ou.ac.uk', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'Student604655', 'Demo', 'CCC', '2014B', 'M', 'Unknown', 'Unknown', '10-20%', '35-55', 'N', NULL, 1, 0.982185958236102, '2025-10-18 17:42:13', '2025-10-18 17:42:13', 0, 0, 0.0);
INSERT INTO students (id_student, email, password_hash, first_name, last_name, code_module, code_presentation, gender, region, highest_education, imd_band, age_band, disability, final_result, is_at_risk, risk_probability, created_at, updated_at, num_days_active, total_clicks, avg_score) VALUES (5, 'student595262@ou.ac.uk', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'Student595262', 'Demo', 'FFF', '2014J', 'M', 'Unknown', 'Unknown', '10-20%', '35-55', 'N', NULL, 1, 0.8639151880351822, '2025-10-18 17:42:13', '2025-10-18 17:42:13', 0, 0, 0.0);
INSERT INTO students (id_student, email, password_hash, first_name, last_name, code_module, code_presentation, gender, region, highest_education, imd_band, age_band, disability, final_result, is_at_risk, risk_probability, created_at, updated_at, num_days_active, total_clicks, avg_score) VALUES (6, 'student513428@ou.ac.uk', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'Student513428', 'Demo', 'FFF', '2014J', 'M', 'Unknown', 'Unknown', '10-20%', '35-55', 'N', NULL, 0, 0.0656768789016575, '2025-10-18 17:42:13', '2025-10-18 17:42:13', 0, 0, 0.0);
INSERT INTO students (id_student, email, password_hash, first_name, last_name, code_module, code_presentation, gender, region, highest_education, imd_band, age_band, disability, final_result, is_at_risk, risk_probability, created_at, updated_at, num_days_active, total_clicks, avg_score) VALUES (7, 'student588524@ou.ac.uk', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'Student588524', 'Demo', 'EEE', '2013J', 'M', 'Unknown', 'Unknown', '10-20%', '35-55', 'N', NULL, 0, 0.0170272967498486, '2025-10-18 17:42:13', '2025-10-18 17:42:13', 0, 0, 0.0);
INSERT INTO students (id_student, email, password_hash, first_name, last_name, code_module, code_presentation, gender, region, highest_education, imd_band, age_band, disability, final_result, is_at_risk, risk_probability, created_at, updated_at, num_days_active, total_clicks, avg_score) VALUES (8, 'student348717@ou.ac.uk', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'Student348717', 'Demo', 'FFF', '2013J', 'M', 'Unknown', 'Unknown', '10-20%', '35-55', 'N', NULL, 0, 0.1972946427330677, '2025-10-18 17:42:13', '2025-10-18 17:42:13', 0, 0, 0.0);
INSERT INTO students (id_student, email, password_hash, first_name, last_name, code_module, code_presentation, gender, region, highest_education, imd_band, age_band, disability, final_result, is_at_risk, risk_probability, created_at, updated_at, num_days_active, total_clicks, avg_score) VALUES (9, 'tes123t@gmail.com', '7ccf882ae5394900f8ba94735d6eefa574ad9c2cbd0a447abd741ab4bcf5a39f', 'tes123t@gmail.com', 'tes123t@gmail.com', 'EEE', '2013J', 'M', 'Us', '', '', '', '', NULL, 0, 0.0, '2025-10-19 15:20:22', '2025-10-19 15:20:22', 0, 0, 0.0);
INSERT INTO students (id_student, email, password_hash, first_name, last_name, code_module, code_presentation, gender, region, highest_education, imd_band, age_band, disability, final_result, is_at_risk, risk_probability, created_at, updated_at, num_days_active, total_clicks, avg_score) VALUES (10, 'john@ou.ac.uk', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'joun', 'doe', '', '', '', '', '', '', '', '', NULL, 0, 0.0, '2025-10-21 02:55:22', '2025-10-21 02:55:22', 0, 0, 0.0);

-- Data for table: vle
INSERT INTO vle (id_site, code_module, code_presentation, activity_type, week_from, week_to) VALUES (546943, 'AAA', '2013J', 'resource', NULL, NULL);
INSERT INTO vle (id_site, code_module, code_presentation, activity_type, week_from, week_to) VALUES (546712, 'AAA', '2013J', 'oucontent', NULL, NULL);
INSERT INTO vle (id_site, code_module, code_presentation, activity_type, week_from, week_to) VALUES (546998, 'AAA', '2013J', 'resource', NULL, NULL);
INSERT INTO vle (id_site, code_module, code_presentation, activity_type, week_from, week_to) VALUES (546888, 'AAA', '2013J', 'url', NULL, NULL);
INSERT INTO vle (id_site, code_module, code_presentation, activity_type, week_from, week_to) VALUES (547035, 'AAA', '2013J', 'resource', NULL, NULL);
INSERT INTO vle (id_site, code_module, code_presentation, activity_type, week_from, week_to) VALUES (546614, 'AAA', '2013J', 'homepage', NULL, NULL);
INSERT INTO vle (id_site, code_module, code_presentation, activity_type, week_from, week_to) VALUES (546897, 'AAA', '2013J', 'url', NULL, NULL);
INSERT INTO vle (id_site, code_module, code_presentation, activity_type, week_from, week_to) VALUES (546678, 'AAA', '2013J', 'oucontent', NULL, NULL);
INSERT INTO vle (id_site, code_module, code_presentation, activity_type, week_from, week_to) VALUES (546933, 'AAA', '2013J', 'resource', NULL, NULL);
INSERT INTO vle (id_site, code_module, code_presentation, activity_type, week_from, week_to) VALUES (546708, 'AAA', '2013J', 'oucontent', NULL, NULL);

