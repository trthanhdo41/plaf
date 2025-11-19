#!/usr/bin/env python3
"""
PLAF Database Setup Script
Automatically sets up the database with all required tables and demo data
"""

import sqlite3
import os
import sys
import subprocess

def setup_database():
    """Setup PLAF database from SQL export"""
    
    print("🚀 PLAF Database Setup")
    print("=" * 50)
    
    # Check if SQL file exists
    sql_file = "plaf_complete_database.sql"
    if not os.path.exists(sql_file):
        print(f"❌ Error: {sql_file} not found!")
        print("Please ensure the SQL export file is in the same directory.")
        return False
    
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"📁 Created directory: {data_dir}")
    
    # Database path
    db_path = os.path.join(data_dir, "lms.db")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        print(f"🗑️  Removing existing database: {db_path}")
        os.remove(db_path)
    
    # Also remove journal files
    for ext in ['-journal', '-wal', '-shm']:
        journal_path = db_path + ext
        if os.path.exists(journal_path):
            os.remove(journal_path)
    
    try:
        # Create new database
        print(f"📊 Creating new database: {db_path}")
        
        # Use sqlite3 command-line tool to import large SQL file
        # This handles large files better than Python's executescript
        print(f"📥 Loading data from: {sql_file}")
        print("   (This may take a few minutes for large files...)")
        
        # Use sqlite3 CLI tool to execute the SQL file
        # sqlite3 db_path < sql_file
        with open(sql_file, 'r', encoding='utf-8') as sql_file_handle:
            result = subprocess.run(
                ['sqlite3', db_path],
                stdin=sql_file_handle,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        if result.returncode != 0:
            print(f"❌ Error executing SQL file: {result.stderr}")
            return False
        
        print("✅ SQL file executed successfully")
        
        # Verify setup using Python connection
        print("\n📋 Verifying database setup...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"✅ Database setup complete!")
        print(f"📋 Created {len(tables)} tables:")
        
        # Show table counts
        important_tables = ['students', 'courses', 'lessons', 'intervention_logs', 'intervention_feedback']
        for table_name in important_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   - {table_name}: {count:,} records")
            except:
                print(f"   - {table_name}: table not found")
        
        # Show demo credentials
        try:
            cursor.execute("SELECT email, first_name, last_name FROM students LIMIT 3")
            demo_users = cursor.fetchall()
            
            if demo_users:
                print(f"\n🔑 Demo Login Credentials:")
                for user in demo_users:
                    print(f"   - Email: {user[0]}")
                    print(f"     Name: {user[1]} {user[2]}")
                    print(f"     Password: demo123")
                    print()
        except:
            print("   (No demo users found)")
        
        conn.close()
        
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: ./start_plaf.sh")
        print("2. Open: http://localhost:3000")
        print("3. Login with demo credentials above")
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: sqlite3 command-line tool not found!")
        print("Please install SQLite3: sudo apt-get install sqlite3")
        return False
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)