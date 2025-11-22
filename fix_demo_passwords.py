import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def fix_demo_passwords():
    db_path = "data/lms.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    demo_accounts = [
        "student650515@ou.ac.uk",
        "student2634238@ou.ac.uk",
        "student588524@ou.ac.uk"
    ]
    
    new_password = "demo123"
    hashed_password = hash_password(new_password)
    
    print(f"Updating passwords for {len(demo_accounts)} demo accounts...")
    
    for email in demo_accounts:
        cursor.execute("UPDATE students SET password_hash = ? WHERE email = ?", (hashed_password, email))
        if cursor.rowcount > 0:
            print(f"✅ Updated password for {email}")
        else:
            print(f"⚠️ User {email} not found")
            
    conn.commit()
    conn.close()
    print("\nPassword update complete.")

if __name__ == "__main__":
    fix_demo_passwords()
