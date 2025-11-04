"""
Seed demo courses data for Udemy-style learning experience.

This script creates demo courses with lessons, videos, and content.
"""

import sqlite3
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_db


def seed_demo_courses():
    """Seed demo courses with lessons."""
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    
    print("🌱 Seeding demo courses...")
    
    # Drop and recreate courses table if it has old schema
    cursor.execute("DROP TABLE IF EXISTS courses")
    cursor.execute("DROP TABLE IF EXISTS lessons")
    cursor.execute("DROP TABLE IF EXISTS student_progress")
    cursor.execute("DROP TABLE IF EXISTS course_enrollments")
    
    # Recreate tables (will be created by setup_database, but just in case)
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
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
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_progress (
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
        )
    """)
    
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
    
    # Course 1: Machine Learning Fundamentals
    cursor.execute("""
        INSERT INTO courses (
            title, description, thumbnail_url, instructor_name, 
            instructor_title, duration_hours, level, category
        ) VALUES (
            'Machine Learning Fundamentals',
            'Learn the fundamentals of machine learning including supervised learning, unsupervised learning, and neural networks. Perfect for beginners!',
            'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=400',
            'Dr. Sarah Johnson',
            'Senior Data Scientist',
            12,
            'Beginner',
            'Data Science'
        )
    """)
    
    course1_id = cursor.lastrowid
    
    # Lessons for Course 1
    course1_lessons = [
        {
            'title': 'Introduction to Machine Learning',
            'content': '''
# Introduction to Machine Learning

Welcome to Machine Learning Fundamentals! In this course, you'll learn everything you need to know to get started with ML.

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

Let's get started! 🚀
            ''',
            'video_url': 'https://www.youtube.com/embed/aircAruvnKk',
            'lesson_type': 'video',
            'duration_minutes': 15,
            'lesson_order': 1
        },
        {
            'title': 'Supervised Learning: Regression',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/fn_Qq_x6pUQ',
            'lesson_type': 'video',
            'duration_minutes': 20,
            'lesson_order': 2
        },
        {
            'title': 'Supervised Learning: Classification',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/aircAruvnKk',
            'lesson_type': 'video',
            'duration_minutes': 25,
            'lesson_order': 3
        },
        {
            'title': 'Unsupervised Learning: Clustering',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/aircAruvnKk',
            'lesson_type': 'video',
            'duration_minutes': 22,
            'lesson_order': 4
        },
        {
            'title': 'Introduction to Neural Networks',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/aircAruvnKk',
            'lesson_type': 'video',
            'duration_minutes': 30,
            'lesson_order': 5
        }
    ]
    
    for lesson in course1_lessons:
        cursor.execute("""
            INSERT INTO lessons (
                course_id, title, content, video_url, lesson_type,
                duration_minutes, lesson_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            course1_id, lesson['title'], lesson['content'], lesson['video_url'],
            lesson['lesson_type'], lesson['duration_minutes'], lesson['lesson_order']
        ))
    
    # Course 2: Web Development Bootcamp
    cursor.execute("""
        INSERT INTO courses (
            title, description, thumbnail_url, instructor_name,
            instructor_title, duration_hours, level, category
        ) VALUES (
            'Complete Web Development Bootcamp',
            'Master modern web development with HTML, CSS, JavaScript, React, and Node.js. Build real-world projects!',
            'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=400',
            'Prof. Michael Chen',
            'Full Stack Developer',
            40,
            'Intermediate',
            'Web Development'
        )
    """)
    
    course2_id = cursor.lastrowid
    
    # Lessons for Course 2
    course2_lessons = [
        {
            'title': 'HTML & CSS Basics',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/HGTJBPNC-Gw',
            'lesson_type': 'video',
            'duration_minutes': 30,
            'lesson_order': 1
        },
        {
            'title': 'JavaScript Fundamentals',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/W6NZfCO5SIk',
            'lesson_type': 'video',
            'duration_minutes': 35,
            'lesson_order': 2
        },
        {
            'title': 'React: Building Modern UIs',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/DLX62G4lc44',
            'lesson_type': 'video',
            'duration_minutes': 40,
            'lesson_order': 3
        },
        {
            'title': 'Node.js & Backend Development',
            'content': '''
# Node.js & Backend Development

Node.js allows you to build server-side applications with JavaScript.

## Creating a Server:

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Hello, World!');
});

server.listen(3000);
```

## Express Framework:

- Routing
- Middleware
- RESTful APIs
- Database integration

Build powerful backend services!
            ''',
            'video_url': 'https://www.youtube.com/embed/TlB_eWDSMt4',
            'lesson_type': 'video',
            'duration_minutes': 45,
            'lesson_order': 4
        }
    ]
    
    for lesson in course2_lessons:
        cursor.execute("""
            INSERT INTO lessons (
                course_id, title, content, video_url, lesson_type,
                duration_minutes, lesson_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            course2_id, lesson['title'], lesson['content'], lesson['video_url'],
            lesson['lesson_type'], lesson['duration_minutes'], lesson['lesson_order']
        ))
    
    conn.commit()
    print("✅ Demo courses seeded successfully!")
    print(f"   - Course 1: Machine Learning Fundamentals ({len(course1_lessons)} lessons)")
    print(f"   - Course 2: Complete Web Development Bootcamp ({len(course2_lessons)} lessons)")


if __name__ == "__main__":
    seed_demo_courses()




This script creates demo courses with lessons, videos, and content.
"""

import sqlite3
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_db


def seed_demo_courses():
    """Seed demo courses with lessons."""
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    
    print("🌱 Seeding demo courses...")
    
    # Drop and recreate courses table if it has old schema
    cursor.execute("DROP TABLE IF EXISTS courses")
    cursor.execute("DROP TABLE IF EXISTS lessons")
    cursor.execute("DROP TABLE IF EXISTS student_progress")
    cursor.execute("DROP TABLE IF EXISTS course_enrollments")
    
    # Recreate tables (will be created by setup_database, but just in case)
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
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
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_progress (
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
        )
    """)
    
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
    
    # Course 1: Machine Learning Fundamentals
    cursor.execute("""
        INSERT INTO courses (
            title, description, thumbnail_url, instructor_name, 
            instructor_title, duration_hours, level, category
        ) VALUES (
            'Machine Learning Fundamentals',
            'Learn the fundamentals of machine learning including supervised learning, unsupervised learning, and neural networks. Perfect for beginners!',
            'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=400',
            'Dr. Sarah Johnson',
            'Senior Data Scientist',
            12,
            'Beginner',
            'Data Science'
        )
    """)
    
    course1_id = cursor.lastrowid
    
    # Lessons for Course 1
    course1_lessons = [
        {
            'title': 'Introduction to Machine Learning',
            'content': '''
# Introduction to Machine Learning

Welcome to Machine Learning Fundamentals! In this course, you'll learn everything you need to know to get started with ML.

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

Let's get started! 🚀
            ''',
            'video_url': 'https://www.youtube.com/embed/aircAruvnKk',
            'lesson_type': 'video',
            'duration_minutes': 15,
            'lesson_order': 1
        },
        {
            'title': 'Supervised Learning: Regression',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/fn_Qq_x6pUQ',
            'lesson_type': 'video',
            'duration_minutes': 20,
            'lesson_order': 2
        },
        {
            'title': 'Supervised Learning: Classification',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/aircAruvnKk',
            'lesson_type': 'video',
            'duration_minutes': 25,
            'lesson_order': 3
        },
        {
            'title': 'Unsupervised Learning: Clustering',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/aircAruvnKk',
            'lesson_type': 'video',
            'duration_minutes': 22,
            'lesson_order': 4
        },
        {
            'title': 'Introduction to Neural Networks',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/aircAruvnKk',
            'lesson_type': 'video',
            'duration_minutes': 30,
            'lesson_order': 5
        }
    ]
    
    for lesson in course1_lessons:
        cursor.execute("""
            INSERT INTO lessons (
                course_id, title, content, video_url, lesson_type,
                duration_minutes, lesson_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            course1_id, lesson['title'], lesson['content'], lesson['video_url'],
            lesson['lesson_type'], lesson['duration_minutes'], lesson['lesson_order']
        ))
    
    # Course 2: Web Development Bootcamp
    cursor.execute("""
        INSERT INTO courses (
            title, description, thumbnail_url, instructor_name,
            instructor_title, duration_hours, level, category
        ) VALUES (
            'Complete Web Development Bootcamp',
            'Master modern web development with HTML, CSS, JavaScript, React, and Node.js. Build real-world projects!',
            'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=400',
            'Prof. Michael Chen',
            'Full Stack Developer',
            40,
            'Intermediate',
            'Web Development'
        )
    """)
    
    course2_id = cursor.lastrowid
    
    # Lessons for Course 2
    course2_lessons = [
        {
            'title': 'HTML & CSS Basics',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/HGTJBPNC-Gw',
            'lesson_type': 'video',
            'duration_minutes': 30,
            'lesson_order': 1
        },
        {
            'title': 'JavaScript Fundamentals',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/W6NZfCO5SIk',
            'lesson_type': 'video',
            'duration_minutes': 35,
            'lesson_order': 2
        },
        {
            'title': 'React: Building Modern UIs',
            'content': '''
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
            ''',
            'video_url': 'https://www.youtube.com/embed/DLX62G4lc44',
            'lesson_type': 'video',
            'duration_minutes': 40,
            'lesson_order': 3
        },
        {
            'title': 'Node.js & Backend Development',
            'content': '''
# Node.js & Backend Development

Node.js allows you to build server-side applications with JavaScript.

## Creating a Server:

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Hello, World!');
});

server.listen(3000);
```

## Express Framework:

- Routing
- Middleware
- RESTful APIs
- Database integration

Build powerful backend services!
            ''',
            'video_url': 'https://www.youtube.com/embed/TlB_eWDSMt4',
            'lesson_type': 'video',
            'duration_minutes': 45,
            'lesson_order': 4
        }
    ]
    
    for lesson in course2_lessons:
        cursor.execute("""
            INSERT INTO lessons (
                course_id, title, content, video_url, lesson_type,
                duration_minutes, lesson_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            course2_id, lesson['title'], lesson['content'], lesson['video_url'],
            lesson['lesson_type'], lesson['duration_minutes'], lesson['lesson_order']
        ))
    
    conn.commit()
    print("✅ Demo courses seeded successfully!")
    print(f"   - Course 1: Machine Learning Fundamentals ({len(course1_lessons)} lessons)")
    print(f"   - Course 2: Complete Web Development Bootcamp ({len(course2_lessons)} lessons)")


if __name__ == "__main__":
    seed_demo_courses()
