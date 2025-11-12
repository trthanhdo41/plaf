-- PLAF Database Schema Only
-- Generated on: 2025-11-12 18:36:38.199033

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

CREATE TABLE chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_student INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                context TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_student) REFERENCES students(id_student)
            );

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

CREATE TABLE course_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_module TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                material_type TEXT,
                week INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

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

CREATE TABLE forum_reply_votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reply_id INTEGER,
        student_id INTEGER,
        vote_type TEXT CHECK(vote_type IN ('like', 'dislike')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (reply_id) REFERENCES forum_replies (id),
        UNIQUE(reply_id, student_id)
    );

CREATE TABLE forum_votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        student_id INTEGER,
        vote_type TEXT CHECK(vote_type IN ('like', 'dislike')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES forum_posts (id),
        UNIQUE(post_id, student_id)
    );

CREATE TABLE forums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            );

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

CREATE TABLE quiz_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                answer_text TEXT NOT NULL,
                is_correct INTEGER DEFAULT 0,
                answer_order INTEGER DEFAULT 0,
                FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE
            );

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

CREATE TABLE sqlite_sequence(name,seq);

CREATE TABLE student_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        assessment_title TEXT,
        score REAL,
        max_score REAL DEFAULT 100.0,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id_student)
    );

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

CREATE TABLE "vle" (
"id_site" INTEGER,
  "code_module" TEXT,
  "code_presentation" TEXT,
  "activity_type" TEXT,
  "week_from" REAL,
  "week_to" REAL
);

