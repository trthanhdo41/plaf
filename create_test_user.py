import sqlite3
from werkzeug.security import generate_password_hash

# Wait for database to be unlocked
import time
max_attempts = 10
for attempt in range(max_attempts):
    try:
        conn = sqlite3.connect('data/lms.db', timeout=30)
        cursor = conn.cursor()
        
        # Create test user with proper password hash
        email = "test@student.com"
        password = "password123"
        password_hash = generate_password_hash(password)
        
        # Delete if exists
        cursor.execute("DELETE FROM students WHERE email = ?", (email,))
        
        # Insert test user
        cursor.execute("""
            INSERT INTO students (
                id_student, email, password_hash, first_name, last_name,
                code_module, code_presentation, gender, region,
                highest_education, imd_band, age_band, disability, final_result,
                is_at_risk, risk_probability
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            99999, email, password_hash, "Test", "Student",
            "AAA", "2013J", "M", "East Anglian Region",
            "HE Qualification", "10-20%", "0-35", "N", "Pass",
            0, 0.15
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Test user created!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        break
        
    except sqlite3.OperationalError as e:
        if "locked" in str(e) and attempt < max_attempts - 1:
            print(f"Database locked, waiting... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(2)
        else:
            print(f"Error: {e}")
            break
