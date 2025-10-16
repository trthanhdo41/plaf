import sqlite3
import hashlib

# Use SHA256 to match the code
password = "123456"
password_hash = hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect('data/lms.db')
cursor = conn.cursor()

# Update simple user with correct hash
cursor.execute("""
    UPDATE students 
    SET password_hash = ? 
    WHERE email = 'simple@test.com'
""", (password_hash,))

# Also update test user
password2 = "password123"
password_hash2 = hashlib.sha256(password2.encode()).hexdigest()

cursor.execute("""
    UPDATE students 
    SET password_hash = ? 
    WHERE email = 'test@student.com'
""", (password_hash2,))

conn.commit()
conn.close()

print(f"✅ Fixed password hashes!")
print(f"simple@test.com / 123456")
print(f"test@student.com / password123")
