import sqlite3
import hashlib

# Simple password hash (MD5 for testing)
password = "123456"
password_hash = hashlib.md5(password.encode()).hexdigest()

conn = sqlite3.connect('data/lms.db')
cursor = conn.cursor()

# Delete if exists
cursor.execute("DELETE FROM students WHERE email = ?", ("simple@test.com",))

# Insert simple user
cursor.execute("""
    INSERT INTO students (
        id_student, email, password_hash, first_name, last_name,
        code_module, code_presentation, gender, region,
        highest_education, imd_band, age_band, disability, final_result,
        is_at_risk, risk_probability
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    99998, "simple@test.com", password_hash, "Simple", "User",
    "CCC", "2014J", "M", "East Anglian Region",
    "HE Qualification", "10-20%", "0-35", "N", "Pass",
    0, 0.15
))

conn.commit()
conn.close()

print(f"✅ Simple user created!")
print(f"Email: simple@test.com")
print(f"Password: {password}")
