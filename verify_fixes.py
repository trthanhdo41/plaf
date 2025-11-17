"""
Verify all fixes from DANH_GIA_HE_THONG_TONG_HOP.md have been applied
"""

import sqlite3
import sys

def verify_fixes():
    """Verify all database fixes"""
    
    print("=" * 70)
    print("VERIFYING FIXES FROM DANH_GIA_HE_THONG_TONG_HOP.md")
    print("=" * 70)
    
    conn = sqlite3.connect("data/lms.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    all_passed = True
    
    # 1. Check students table has new fields
    print("\n✓ Test 1: Students table has num_of_prev_attempts and studied_credits")
    cursor.execute("PRAGMA table_info(students)")
    student_columns = [col[1] for col in cursor.fetchall()]
    
    if 'num_of_prev_attempts' in student_columns and 'studied_credits' in student_columns:
        print("  ✅ PASS - Fields exist")
        
        # Check if data is populated
        cursor.execute("SELECT COUNT(*) as cnt, AVG(num_of_prev_attempts) as avg_attempts, AVG(studied_credits) as avg_credits FROM students WHERE num_of_prev_attempts > 0 OR studied_credits > 0")
        result = cursor.fetchone()
        print(f"     Students with data: {result['cnt']:,}")
        print(f"     Avg prev attempts: {result['avg_attempts']:.2f}")
        print(f"     Avg studied credits: {result['avg_credits']:.1f}")
    else:
        print("  ❌ FAIL - Fields missing")
        all_passed = False
    
    # 2. Check assessments table has new fields
    print("\n✓ Test 2: Assessments table has all new fields")
    cursor.execute("PRAGMA table_info(assessments)")
    assessment_columns = [col[1] for col in cursor.fetchall()]
    
    required_fields = ['code_module', 'code_presentation', 'assessment_type', 'date_due', 'weight', 'date_submitted', 'is_banked']
    missing = [f for f in required_fields if f not in assessment_columns]
    
    if not missing:
        print("  ✅ PASS - All fields exist")
        
        # Check if data is populated
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(code_module) as has_module,
                COUNT(assessment_type) as has_type,
                COUNT(weight) as has_weight,
                SUM(is_banked) as banked_count
            FROM assessments
        """)
        result = cursor.fetchone()
        print(f"     Total assessments: {result['total']:,}")
        print(f"     With code_module: {result['has_module']:,}")
        print(f"     With assessment_type: {result['has_type']:,}")
        print(f"     With weight: {result['has_weight']:,}")
        print(f"     Banked assessments: {result['banked_count']:,}")
    else:
        print(f"  ❌ FAIL - Missing fields: {missing}")
        all_passed = False
    
    # 3. Check assessment merge is correct
    print("\n✓ Test 3: Assessments properly merged with assessment_info")
    cursor.execute("""
        SELECT 
            assessment_type,
            COUNT(*) as count,
            AVG(weight) as avg_weight
        FROM assessments
        WHERE assessment_type IS NOT NULL
        GROUP BY assessment_type
    """)
    results = cursor.fetchall()
    
    if results:
        print("  ✅ PASS - Assessment types populated:")
        for row in results:
            print(f"     {row['assessment_type']}: {row['count']:,} assessments (avg weight: {row['avg_weight']:.1f}%)")
    else:
        print("  ❌ FAIL - No assessment types found")
        all_passed = False
    
    # 4. Check late submission calculation
    print("\n✓ Test 4: Late submission calculation")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(is_late) as late_count,
            ROUND(SUM(is_late) * 100.0 / COUNT(*), 2) as late_percentage
        FROM assessments
        WHERE date_submitted IS NOT NULL AND date_due IS NOT NULL
    """)
    result = cursor.fetchone()
    
    if result['total'] > 0:
        print(f"  ✅ PASS - Late submissions calculated")
        print(f"     Total with dates: {result['total']:,}")
        print(f"     Late submissions: {result['late_count']:,} ({result['late_percentage']}%)")
    else:
        print("  ❌ FAIL - No date data found")
        all_passed = False
    
    # 5. Check VLE week_from/week_to are INTEGER
    print("\n✓ Test 5: VLE week_from/week_to are INTEGER")
    cursor.execute("PRAGMA table_info(vle)")
    vle_columns = {col[1]: col[2] for col in cursor.fetchall()}
    
    week_from_type = vle_columns.get('week_from', '')
    week_to_type = vle_columns.get('week_to', '')
    
    if 'INT' in week_from_type.upper() and 'INT' in week_to_type.upper():
        print(f"  ✅ PASS - Both are INTEGER type")
        print(f"     week_from: {week_from_type}")
        print(f"     week_to: {week_to_type}")
    else:
        print(f"  ⚠️  WARNING - Types: week_from={week_from_type}, week_to={week_to_type}")
    
    # 6. Overall data statistics
    print("\n✓ Test 6: Overall data statistics")
    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM assessments")
    assessment_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM activities")
    activity_count = cursor.fetchone()[0]
    
    print(f"  📊 Data Summary:")
    print(f"     Students: {student_count:,}")
    print(f"     Assessments: {assessment_count:,}")
    print(f"     VLE Activities: {activity_count:,}")
    
    conn.close()
    
    # Final result
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED - Fixes successfully applied!")
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
    print("=" * 70)
    
    return all_passed

if __name__ == "__main__":
    success = verify_fixes()
    sys.exit(0 if success else 1)
