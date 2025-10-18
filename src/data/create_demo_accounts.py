"""
Create demo accounts for testing Student Portal.

This script creates login accounts for real students from OULAD dataset,
including at-risk students so users can test the chatbot and personalized advice.
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import get_db


def create_demo_accounts():
    """Create demo accounts for testing."""
    print("="*70)
    print("CREATING DEMO ACCOUNTS FOR STUDENT PORTAL")
    print("="*70)
    
    db = get_db()
    conn = db.connect()
    conn.execute("PRAGMA journal_mode=DELETE;")  # Disable WAL mode
    conn.commit()
    conn.close()
    
    # Check if predictions exist
    predictions_file = "data/processed/student_predictions.csv"
    if not os.path.exists(predictions_file):
        print("\n❌ Error: student_predictions.csv not found!")
        print("Please run the pipeline first: python run_pipeline.py")
        return
    
    # Load predictions
    print(f"\n[1/3] Loading student predictions...")
    df = pd.read_csv(predictions_file)
    print(f"   Found {len(df):,} students")
    
    # Get at-risk students
    at_risk = df[df['is_at_risk'] == 1].copy()
    safe = df[df['is_at_risk'] == 0].copy()
    
    print(f"   - At-risk: {len(at_risk):,} students")
    print(f"   - Safe: {len(safe):,} students")
    
    # Select demo students: 5 at-risk + 3 safe
    print(f"\n[2/3] Selecting demo students...")
    
    demo_at_risk = at_risk.sample(min(5, len(at_risk)), random_state=42)
    demo_safe = safe.sample(min(3, len(safe)), random_state=42)
    
    demo_students = pd.concat([demo_at_risk, demo_safe])
    
    print(f"   Selected {len(demo_students)} students for demo accounts:")
    print(f"   - {len(demo_at_risk)} at-risk")
    print(f"   - {len(demo_safe)} safe")
    
    # Create accounts
    print(f"\n[3/3] Creating accounts...")
    print()
    
    created = []
    
    for idx, row in demo_students.iterrows():
        student_id = int(row['id_student'])
        is_at_risk = int(row['is_at_risk'])
        risk_prob = float(row['risk_probability'])
        
        # Create account details
        email = f"student{student_id}@ou.ac.uk"
        password = "demo123"  # Simple password for demo
        first_name = f"Student{student_id}"
        last_name = "Demo"
        
        try:
            # Check if account already exists
            existing = db.authenticate_student(email, password)
            
            if existing:
                print(f"   ✓ Student {student_id} already has account")
            else:
                # Create new account
                new_id = db.create_student(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    code_module=row.get('code_module', 'AAA'),
                    code_presentation=row.get('code_presentation', '2013J'),
                    gender=row.get('gender', 'M'),
                    region=row.get('region', 'Unknown'),
                    highest_education=row.get('highest_education', 'Unknown'),
                    imd_band=str(row.get('imd_band', '10-20%')),
                    age_band=row.get('age_band', '35-55'),
                    disability=row.get('disability', 'N')
                )
                
                if new_id:
                    # Update risk prediction
                    db.update_student_risk(new_id, is_at_risk, risk_prob)
                    print(f"   ✓ Created: Student {student_id} ({'AT-RISK' if is_at_risk else 'SAFE'})")
                else:
                    print(f"   ✗ Failed: Student {student_id}")
                    continue
            
            # Add to created list
            created.append({
                'student_id': student_id,
                'email': email,
                'password': password,
                'is_at_risk': is_at_risk,
                'risk_probability': f"{risk_prob*100:.1f}%"
            })
            
        except Exception as e:
            print(f"   ✗ Error for student {student_id}: {e}")
    
    # Print summary
    print()
    print("="*70)
    print("DEMO ACCOUNTS CREATED SUCCESSFULLY")
    print("="*70)
    print()
    print("You can now login to Student Portal with these accounts:")
    print()
    print(f"{'Student ID':<15} {'Email':<35} {'Password':<12} {'Status':<15} {'Risk':<10}")
    print("-"*90)
    
    for account in created:
        status = "🔴 AT-RISK" if account['is_at_risk'] else "🟢 SAFE"
        print(f"{account['student_id']:<15} {account['email']:<35} {account['password']:<12} {status:<15} {account['risk_probability']:<10}")
    
    print()
    print("="*70)
    print("USAGE:")
    print("="*70)
    print()
    print("1. Start Student Portal:")
    print("   streamlit run src/lms_portal/student_app.py --server.port 8501")
    print()
    print("2. Login with any email above and password: demo123")
    print()
    print("3. Test chatbot for at-risk students (🔴) to see personalized advice")
    print()
    
    # Save to file
    output_file = "data/demo_accounts.csv"
    pd.DataFrame(created).to_csv(output_file, index=False)
    print(f"Account list saved to: {output_file}")
    print()


if __name__ == "__main__":
    create_demo_accounts()

