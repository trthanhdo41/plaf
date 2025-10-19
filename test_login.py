"""
Test login for demo accounts.

This script tests if the demo accounts can login successfully.
Run this after creating demo accounts to verify login works.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from database.models import get_db


def test_login():
    """Test login for demo accounts."""
    print("="*70)
    print("TESTING LOGIN FOR DEMO ACCOUNTS")
    print("="*70)
    print()
    
    db = get_db()
    
    # Test accounts
    test_accounts = [
        ("student650515@ou.ac.uk", "demo123", "AT-RISK 99.9%"),
        ("student2634238@ou.ac.uk", "demo123", "AT-RISK 100%"),
        ("student588524@ou.ac.uk", "demo123", "SAFE 1.7%"),
    ]
    
    success_count = 0
    fail_count = 0
    
    for email, password, description in test_accounts:
        result = db.authenticate_student(email, password)
        
        if result:
            print(f"✓ LOGIN SUCCESS: {email}")
            print(f"  Student ID: {result['id_student']}")
            print(f"  Name: {result['first_name']} {result['last_name']}")
            print(f"  Risk: {result.get('is_at_risk', 0)} ({result.get('risk_probability', 0)*100:.1f}%)")
            print(f"  Description: {description}")
            success_count += 1
        else:
            print(f"✗ LOGIN FAILED: {email}")
            print(f"  Password: {password}")
            print(f"  Description: {description}")
            fail_count += 1
        
        print()
    
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total: {len(test_accounts)} accounts")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")
    print()
    
    if fail_count == 0:
        print("✓ ALL TESTS PASSED!")
        print()
        print("You can now login to Student Portal:")
        print("  → http://localhost:8501")
        print("  → Use any email above with password: demo123")
    else:
        print("✗ SOME TESTS FAILED!")
        print()
        print("To fix login issues:")
        print("  1. Make sure you ran: python src/data/create_demo_accounts.py")
        print("  2. Or try: rm -f data/lms.db* && python src/data/create_demo_accounts.py")
    
    print("="*70)


if __name__ == "__main__":
    test_login()

