"""
Migration script to add missing fields to existing database
Based on DANH_GIA_HE_THONG_TONG_HOP.md requirements
"""

import sqlite3
import os

def migrate_database():
    """Add missing fields to existing database"""
    
    db_path = "data/lms.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    print("=" * 60)
    print("DATABASE MIGRATION - Adding Missing Fields")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(students)")
    student_columns = [col[1] for col in cursor.fetchall()]
    
    cursor.execute("PRAGMA table_info(assessments)")
    assessment_columns = [col[1] for col in cursor.fetchall()]
    
    print("\n📊 Current Schema:")
    print(f"  Students columns: {len(student_columns)}")
    print(f"  Assessments columns: {len(assessment_columns)}")
    
    # Add missing fields to students table
    print("\n🔧 Migrating students table...")
    
    if 'num_of_prev_attempts' not in student_columns:
        print("  ➕ Adding num_of_prev_attempts...")
        cursor.execute("ALTER TABLE students ADD COLUMN num_of_prev_attempts INTEGER DEFAULT 0")
        print("     ✅ Added")
    else:
        print("  ✓ num_of_prev_attempts already exists")
    
    if 'studied_credits' not in student_columns:
        print("  ➕ Adding studied_credits...")
        cursor.execute("ALTER TABLE students ADD COLUMN studied_credits INTEGER DEFAULT 0")
        print("     ✅ Added")
    else:
        print("  ✓ studied_credits already exists")
    
    # Add missing fields to assessments table
    print("\n🔧 Migrating assessments table...")
    
    fields_to_add = [
        ('code_module', 'TEXT'),
        ('code_presentation', 'TEXT'),
        ('assessment_type', 'TEXT'),
        ('date_due', 'INTEGER'),
        ('weight', 'REAL'),
        ('date_submitted', 'INTEGER'),
        ('is_banked', 'INTEGER DEFAULT 0')
    ]
    
    for field_name, field_type in fields_to_add:
        if field_name not in assessment_columns:
            print(f"  ➕ Adding {field_name}...")
            cursor.execute(f"ALTER TABLE assessments ADD COLUMN {field_name} {field_type}")
            print(f"     ✅ Added")
        else:
            print(f"  ✓ {field_name} already exists")
    
    conn.commit()
    
    # Verify changes
    print("\n✅ Verification:")
    cursor.execute("PRAGMA table_info(students)")
    new_student_columns = [col[1] for col in cursor.fetchall()]
    
    cursor.execute("PRAGMA table_info(assessments)")
    new_assessment_columns = [col[1] for col in cursor.fetchall()]
    
    print(f"  Students columns: {len(student_columns)} → {len(new_student_columns)}")
    print(f"  Assessments columns: {len(assessment_columns)} → {len(new_assessment_columns)}")
    
    # Show new fields
    print("\n📋 New Fields Added:")
    print("  Students:")
    print("    - num_of_prev_attempts (INTEGER)")
    print("    - studied_credits (INTEGER)")
    print("  Assessments:")
    print("    - code_module (TEXT)")
    print("    - code_presentation (TEXT)")
    print("    - assessment_type (TEXT)")
    print("    - date_due (INTEGER)")
    print("    - weight (REAL)")
    print("    - date_submitted (INTEGER)")
    print("    - is_banked (INTEGER)")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETE")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    migrate_database()
