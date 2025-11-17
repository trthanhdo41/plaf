"""
Reload OULAD data with all fixes from DANH_GIA_HE_THONG_TONG_HOP.md
"""

import subprocess
import sys

print("=" * 70)
print("RELOADING OULAD DATA WITH FIXES")
print("=" * 70)

print("\n📋 Fixes Applied:")
print("  ✅ Added num_of_prev_attempts to students")
print("  ✅ Added studied_credits to students")
print("  ✅ Added is_banked to assessments")
print("  ✅ Added code_module, code_presentation, assessment_type to assessments")
print("  ✅ Added date_due, weight to assessments")
print("  ✅ Fixed assessment merge (proper join on id_assessment)")
print("  ✅ Fixed late submission calculation")
print("  ✅ Fixed week_from/week_to to INTEGER")

print("\n⚠️  This will reload all OULAD data from scratch")
response = input("Continue? (yes/no): ")

if response.lower() != 'yes':
    print("Cancelled.")
    sys.exit(0)

print("\n🚀 Starting data reload...")
print("-" * 70)

# Run the load script
result = subprocess.run(
    [sys.executable, "src/data/load_full_oulad.py"],
    capture_output=False
)

if result.returncode == 0:
    print("\n" + "=" * 70)
    print("✅ DATA RELOAD COMPLETE")
    print("=" * 70)
    print("\n📊 All fixes from DANH_GIA_HE_THONG_TONG_HOP.md have been applied!")
else:
    print("\n❌ Error during reload")
    sys.exit(1)
