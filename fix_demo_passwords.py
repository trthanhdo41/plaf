#!/usr/bin/env python3
"""
Fix demo account passwords in database.

The SQL file may have incorrect password hashes. This script updates
all demo account passwords to use the correct SHA256 hash format.
"""

import sqlite3
import hashlib
import sys
import os

def fix_demo_passwords():
    """Fix password hashes for all demo accounts."""
    
    print("="*70)
    print("FIXING DEMO ACCOUNT PASSWORDS")
    print("="*70)
    print()
    
    db_path = "data/lms.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Error: {db_path} not found!")
        print("Please run reset_plaf.sh first to create the database.")
        return False
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Calculate correct SHA256 hash for "demo123"
    password = "demo123"
    correct_hash = hashlib.sha256(password.encode()).hexdigest()
    print(f"Correct SHA256 hash for 'demo123': {correct_hash}")
    print()
    
    # Find all demo accounts (students with @ou.ac.uk emails)
    cursor.execute("""
        SELECT id_student, email, substr(password_hash, 1, 20) as hash_preview
        FROM students 
        WHERE email LIKE '%@ou.ac.uk' OR email LIKE 'student%@ou.ac.uk'
        ORDER BY id_student
    """)
    
    students = cursor.fetchall()
    print(f"Found {len(students)} demo accounts to check")
    print()
    
    fixed_count = 0
    already_correct = 0
    
    for student_id, email, hash_preview in students:
        # Check current hash
        cursor.execute("SELECT password_hash FROM students WHERE id_student = ?", (student_id,))
        current_hash = cursor.fetchone()[0]
        
        # Check if hash is already correct
        if current_hash == correct_hash:
            print(f"✓ {email} - Already has correct hash")
            already_correct += 1
            continue
        
        # Check if hash looks like PBKDF2 or invalid format
        if current_hash.startswith('pbkdf2:') or len(current_hash) != 64:
            # Update to correct hash
            cursor.execute("""
                UPDATE students 
                SET password_hash = ? 
                WHERE id_student = ?
            """, (correct_hash, student_id))
            
            print(f"✓ {email} - Fixed (was: {hash_preview}...)")
            fixed_count += 1
        else:
            print(f"⚠ {email} - Has different hash format, skipping")
    
    # Commit changes
    conn.commit()
    
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total accounts: {len(students)}")
    print(f"Fixed: {fixed_count}")
    print(f"Already correct: {already_correct}")
    print()
    
    if fixed_count > 0:
        print("✅ Password hashes updated successfully!")
        print()
        print("Demo login credentials:")
        print("  Email: student650515@ou.ac.uk (or any student@ou.ac.uk email)")
        print("  Password: demo123")
        print()
        print("You can now login with these credentials.")
    else:
        print("✅ All passwords are already correct!")
    
    conn.close()
    return True

if __name__ == "__main__":
    success = fix_demo_passwords()
    sys.exit(0 if success else 1)

