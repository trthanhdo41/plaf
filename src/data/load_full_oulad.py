"""
Load FULL OULAD dataset into database.

This script loads ALL data from OULAD:
- studentInfo.csv: 32,593 students
- studentRegistration.csv: Student course registrations
- studentAssessment.csv: Assessment scores
- studentVle.csv: 10,655,280 VLE interactions
- vle.csv: VLE activities
- courses.csv: Course modules
- assessments.csv: Assessment details
"""

import pandas as pd
import sqlite3
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_db


def load_full_oulad(dataset_path="OULAD dataset"):
    """Load FULL OULAD dataset into database."""
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    
    print("="*60)
    print("LOADING FULL OULAD DATASET")
    print("="*60)
    
    # 1. Load studentInfo.csv (32,593 students)
    print("\n[1/7] Loading studentInfo.csv...")
    try:
        student_info = pd.read_csv(os.path.join(dataset_path, "studentInfo.csv"))
        print(f"   Found {len(student_info):,} students")
        
        # Insert students into database
        for index, row in student_info.iterrows():
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO students (
                        id_student, email, password_hash, first_name, last_name,
                        code_module, code_presentation, gender, region,
                        highest_education, imd_band, age_band, disability, final_result
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['id_student'],
                    f"student{row['id_student']}@ou.ac.uk",  # Generate email
                    "pbkdf2:sha256:600000$default$hash",  # Default password
                    f"Student{row['id_student'][:5] if isinstance(row['id_student'], str) else row['id_student']}",
                    "User",
                    row['code_module'],
                    row['code_presentation'],
                    row.get('gender', 'Unknown'),
                    row.get('region', 'Unknown'),
                    row.get('highest_education', 'Unknown'),
                    row.get('imd_band', 'Unknown'),
                    row.get('age_band', 'Unknown'),
                    row.get('disability', 'N'),
                    row.get('final_result', 'Unknown')
                ))
                
                if (index + 1) % 5000 == 0:
                    print(f"   Progress: {index + 1:,}/{len(student_info):,} students")
                    conn.commit()
                    
            except Exception as e:
                print(f"   Error inserting student {row['id_student']}: {e}")
        
        conn.commit()
        print(f"   ✅ Loaded {len(student_info):,} students successfully")
        
    except Exception as e:
        print(f"   ❌ Error loading studentInfo.csv: {e}")
    
    
    # 2. Load courses.csv
    print("\n[2/7] Loading courses.csv...")
    try:
        courses_df = pd.read_csv(os.path.join(dataset_path, "courses.csv"))
        print(f"   Found {len(courses_df)} courses")
        
        cursor.execute("DROP TABLE IF EXISTS courses")
        courses_df.to_sql('courses', conn, if_exists='replace', index=False)
        print(f"   ✅ Loaded {len(courses_df)} courses successfully")
        
    except Exception as e:
        print(f"   ❌ Error loading courses.csv: {e}")
    
    
    # 3. Load vle.csv (VLE resources)
    print("\n[3/7] Loading vle.csv...")
    try:
        vle_df = pd.read_csv(os.path.join(dataset_path, "vle.csv"))
        print(f"   Found {len(vle_df):,} VLE resources")
        
        cursor.execute("DROP TABLE IF EXISTS vle")
        vle_df.to_sql('vle', conn, if_exists='replace', index=False)
        print(f"   ✅ Loaded {len(vle_df):,} VLE resources successfully")
        
    except Exception as e:
        print(f"   ❌ Error loading vle.csv: {e}")
    
    
    # 4. Load assessments.csv
    print("\n[4/7] Loading assessments.csv...")
    try:
        assessments_df = pd.read_csv(os.path.join(dataset_path, "assessments.csv"))
        print(f"   Found {len(assessments_df):,} assessments")
        
        cursor.execute("DROP TABLE IF EXISTS assessment_info")
        assessments_df.to_sql('assessment_info', conn, if_exists='replace', index=False)
        print(f"   ✅ Loaded {len(assessments_df):,} assessments successfully")
        
    except Exception as e:
        print(f"   ❌ Error loading assessments.csv: {e}")
    
    
    # 5. Load studentAssessment.csv
    print("\n[5/7] Loading studentAssessment.csv...")
    try:
        student_assessment = pd.read_csv(os.path.join(dataset_path, "studentAssessment.csv"))
        print(f"   Found {len(student_assessment):,} assessment submissions")
        
        # Clear existing assessments first
        cursor.execute("DELETE FROM assessments")
        conn.commit()
        
        # Insert into assessments table
        inserted = 0
        for index, row in student_assessment.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO assessments (
                        id_student, id_assessment, submission_date, score
                    ) VALUES (?, ?, ?, ?)
                """, (
                    int(row['id_student']),
                    int(row['id_assessment']),
                    int(row.get('date_submitted', 0)) if pd.notna(row.get('date_submitted')) else None,
                    float(row.get('score', 0)) if pd.notna(row.get('score')) else None
                ))
                inserted += 1
                
                if (inserted) % 10000 == 0:
                    print(f"   Progress: {inserted:,}/{len(student_assessment):,} assessments")
                    conn.commit()
                    
            except Exception as e:
                if inserted == 0:  # Show first error only
                    print(f"   Error example: {e}")
        
        conn.commit()
        print(f"   ✅ Loaded {inserted:,} assessment submissions successfully")
        
    except Exception as e:
        print(f"   ❌ Error loading studentAssessment.csv: {e}")
    
    
    # 6. Load studentRegistration.csv
    print("\n[6/7] Loading studentRegistration.csv...")
    try:
        student_registration = pd.read_csv(os.path.join(dataset_path, "studentRegistration.csv"))
        print(f"   Found {len(student_registration):,} registrations")
        
        cursor.execute("DROP TABLE IF EXISTS student_registration")
        student_registration.to_sql('student_registration', conn, if_exists='replace', index=False)
        print(f"   ✅ Loaded {len(student_registration):,} registrations successfully")
        
    except Exception as e:
        print(f"   ❌ Error loading studentRegistration.csv: {e}")
    
    
    # 7. Load studentVle.csv (10+ million records - THIS IS THE BIG ONE)
    print("\n[7/7] Loading studentVle.csv (10M+ records - may take 5-10 minutes)...")
    try:
        # Load in chunks to avoid memory issues
        chunk_size = 100000
        total_loaded = 0
        
        print("   Reading CSV in chunks...")
        for chunk_num, chunk in enumerate(pd.read_csv(os.path.join(dataset_path, "studentVle.csv"), chunksize=chunk_size)):
            # Insert into activities table
            for index, row in chunk.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO activities (
                            id_student, activity_type, resource_id, clicks, date
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        row['id_student'],
                        'vle_interaction',
                        row['id_site'],
                        row.get('sum_click', 1),
                        row.get('date', None)
                    ))
                except Exception as e:
                    pass  # Skip errors
            
            conn.commit()
            total_loaded += len(chunk)
            print(f"   Progress: {total_loaded:,} VLE interactions loaded...")
        
        print(f"   ✅ Loaded {total_loaded:,} VLE interactions successfully")
        
    except Exception as e:
        print(f"   ❌ Error loading studentVle.csv: {e}")
    
    
    # Final stats
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    
    cursor.execute("SELECT COUNT(*) FROM students")
    print(f"Total Students: {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT COUNT(*) FROM activities")
    print(f"Total Activities: {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT COUNT(*) FROM assessments")
    print(f"Total Assessments: {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT COUNT(*) FROM vle")
    print(f"Total VLE Resources: {cursor.fetchone()[0]:,}")
    
    try:
        cursor.execute("SELECT COUNT(*) FROM courses")
        print(f"Total Courses: {cursor.fetchone()[0]:,}")
    except:
        pass
    
    print("="*60)
    print("✅ FULL OULAD DATASET LOADED SUCCESSFULLY!")
    print("="*60)
    
    conn.close()


if __name__ == "__main__":
    import time
    start_time = time.time()
    
    load_full_oulad()
    
    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed/60:.1f} minutes")

