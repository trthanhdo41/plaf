#!/bin/bash

# PLAF Complete System Reset Script
# Resets everything and runs the full pipeline from scratch:
# 1. Clear cache and database
# 2. Setup database schema
# 3. Load OULAD data
# 4. Run ML pipeline (predictions)
# 5. Create demo accounts with risk data
# 6. Fix passwords
# 7. Seed courses/lessons (optional)

set -e

echo "========================================"
echo "🔄 PLAF - Complete System Reset"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Confirmation
echo -e "${YELLOW}⚠️  WARNING: This will delete all cache, database, and models!${NC}"
echo ""
echo "This script will:"
echo "  1. Clear all cache (Python, RAG index, etc.)"
echo "  2. Delete database and models"
echo "  3. Setup fresh database schema"
echo "  4. Load OULAD data (students, VLE, assessments, activities)"
echo "  5. Run ML pipeline to generate risk predictions"
echo "  6. Update student risk predictions in database"
echo "  7. Create demo accounts"
echo "  8. Fix passwords"
echo "  9. Load VLE data"
echo "  10. (Optional) Seed demo courses"
echo ""
read -p "Continue? (y/N): " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "❌ Reset cancelled"
    exit 0
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please run quick_start.sh first to setup the system."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo ""
echo "========================================"
echo "STEP 1: Clearing Cache"
echo "========================================"
echo ""

# Remove Python cache
find . -type d -name "__pycache__" -not -path "./venv/*" -not -path "./node_modules/*" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -not -path "./venv/*" -not -path "./node_modules/*" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -not -path "./venv/*" -not -path "./node_modules/*" -delete 2>/dev/null || true

# Remove RAG index files
rm -f data/rag_index.pkl
rm -f data/rag_index.faiss
rm -f data/faiss_index.faiss
rm -f data/knowledge_base.pkl

# Remove other cache
find . -type f -name "*.cache" -not -path "./venv/*" -not -path "./node_modules/*" -delete 2>/dev/null || true
find . -type d -name ".cache" -not -path "./venv/*" -not -path "./node_modules/*" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -not -path "./venv/*" -not -path "./node_modules/*" -exec rm -rf {} + 2>/dev/null || true

echo -e "${GREEN}✅ Cache cleared${NC}"

echo ""
echo "========================================"
echo "STEP 2: Clearing Database and Models"
echo "========================================"
echo ""

# Remove database files
rm -f data/lms.db
rm -f data/lms.db-journal
rm -f data/lms.db-wal
rm -f data/lms.db-shm
rm -f data/*.db
rm -f data/*.db-journal
rm -f data/*.db-wal
rm -f data/*.db-shm
rm -f plaf_lms.db
rm -f src/data/lms.db

# Remove models
rm -f models/*.pkl
rm -f models/*.joblib

# Remove processed data (will be regenerated)
rm -f data/processed/*.csv
rm -f data/features/*.csv

echo -e "${GREEN}✅ Database and models cleared${NC}"

echo ""
echo "========================================"
echo "STEP 3: Setting Up Database Schema"
echo "========================================"
echo ""

# Initialize database with schema only (no data)
python -c "
from src.database.models import get_db
db = get_db()
print('✅ Database schema created')
"

echo -e "${GREEN}✅ Database schema created${NC}"

echo ""
echo "========================================"
echo "STEP 4: Loading OULAD Data"
echo "========================================"
echo ""

# Load full OULAD dataset
echo "Loading OULAD dataset (this may take a few minutes)..."
python src/data/load_full_oulad.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ OULAD data loaded${NC}"
else
    echo -e "${RED}❌ Failed to load OULAD data${NC}"
    exit 1
fi

echo ""
echo "========================================"
echo "STEP 5: Loading VLE Data"
echo "========================================"
echo ""

# Load VLE data
python src/data/load_vle_data.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ VLE data loaded${NC}"
else
    echo -e "${YELLOW}⚠️  VLE data loading had warnings (continuing...)${NC}"
fi

echo ""
echo "========================================"
echo "STEP 6: Running ML Pipeline"
echo "========================================"
echo ""

# Check if OULAD dataset exists
if [ ! -d "OULAD dataset" ]; then
    echo -e "${RED}❌ Error: OULAD dataset directory not found!${NC}"
    echo "Please ensure 'OULAD dataset' directory exists with CSV files."
    exit 1
fi

# Run ML pipeline to generate predictions
echo "Running ML pipeline (this will take several minutes)..."
echo "This will:"
echo "  - Load and preprocess data"
echo "  - Engineer features"
echo "  - Train ML models"
echo "  - Generate risk predictions"
echo ""

python run_pipeline.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ ML pipeline completed${NC}"
else
    echo -e "${RED}❌ ML pipeline failed!${NC}"
    exit 1
fi

# Check if predictions file was created
if [ ! -f "data/processed/student_predictions.csv" ]; then
    echo -e "${RED}❌ Error: student_predictions.csv not found!${NC}"
    echo "Pipeline may have failed silently."
    exit 1
fi

echo ""
echo "========================================"
echo "STEP 7: Updating Student Risk Predictions"
echo "========================================"
echo ""

# Update risk predictions in database
python -c "
import pandas as pd
import sqlite3
import sys
import os

project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.append(project_root)
from src.database.models import get_db

print('Loading predictions...')
df = pd.read_csv('data/processed/student_predictions.csv')

print(f'Found {len(df):,} student predictions')

db = get_db()
conn = db.connect()
cursor = conn.cursor()

updated = 0
for idx, row in df.iterrows():
    try:
        student_id = int(row['id_student'])
        is_at_risk = int(row.get('is_at_risk', row.get('predicted_at_risk', 0)))
        risk_prob = float(row.get('risk_probability', 0.0))
        
        cursor.execute('''
            UPDATE students 
            SET is_at_risk = ?, risk_probability = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id_student = ?
        ''', (is_at_risk, risk_prob, student_id))
        
        if cursor.rowcount > 0:
            updated += 1
        
        if (idx + 1) % 5000 == 0:
            print(f'  Progress: {idx + 1:,}/{len(df):,} students updated')
            conn.commit()
    except Exception as e:
        print(f'  Error updating student {student_id}: {e}')

conn.commit()
conn.close()

print(f'✅ Updated risk predictions for {updated:,} students')
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Risk predictions updated${NC}"
else
    echo -e "${YELLOW}⚠️  Some errors occurred updating predictions (continuing...)${NC}"
fi

echo ""
echo "========================================"
echo "STEP 8: Creating Demo Accounts"
echo "========================================"
echo ""

# Create demo accounts
python src/data/create_demo_accounts.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Demo accounts created${NC}"
else
    echo -e "${YELLOW}⚠️  Demo account creation had issues (continuing...)${NC}"
fi

echo ""
echo "========================================"
echo "STEP 9: Fixing Passwords"
echo "========================================"
echo ""

# Fix passwords
python fix_demo_passwords.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Passwords fixed${NC}"
else
    echo -e "${YELLOW}⚠️  Password fix had issues (continuing...)${NC}"
fi

echo ""
echo "========================================"
echo "STEP 10: Seeding Demo Courses (Optional)"
echo "========================================"
echo ""

read -p "Seed demo courses with lessons? (y/N): " seed_courses

if [[ "$seed_courses" =~ ^[Yy]$ ]]; then
    if [ -f "src/data/seed_demo_courses.py" ]; then
        python src/data/seed_demo_courses.py
        echo -e "${GREEN}✅ Demo courses seeded${NC}"
    else
        echo -e "${YELLOW}⚠️  seed_demo_courses.py not found, skipping${NC}"
    fi
else
    echo "Skipping course seeding"
fi

echo ""
echo "========================================"
echo "✨ System Reset Complete!"
echo "========================================"
echo ""
echo -e "${GREEN}All systems have been reset and rebuilt!${NC}"
echo ""
echo "Summary:"
echo "  ✅ Cache cleared"
echo "  ✅ Database recreated with schema"
echo "  ✅ OULAD data loaded"
echo "  ✅ ML pipeline executed"
echo "  ✅ Risk predictions updated"
echo "  ✅ Demo accounts created"
echo "  ✅ Passwords fixed"
if [[ "$seed_courses" =~ ^[Yy]$ ]]; then
    echo "  ✅ Demo courses seeded"
fi
echo ""
echo "Next steps:"
echo "  1. Run: ./start_plaf.sh"
echo "  2. Open: http://localhost:3000"
echo "  3. Login with demo credentials:"
echo "     Email: student650515@ou.ac.uk"
echo "     Password: demo123"
echo ""
echo -e "${BLUE}📊 Database Statistics:${NC}"
echo ""

# Show database stats
python -c "
from src.database.models import get_db
import sqlite3

db = get_db()
conn = db.connect()
cursor = conn.cursor()

# Count students
cursor.execute('SELECT COUNT(*) FROM students')
student_count = cursor.fetchone()[0]

# Count at-risk students
cursor.execute('SELECT COUNT(*) FROM students WHERE is_at_risk = 1')
at_risk_count = cursor.fetchone()[0]

# Count activities
cursor.execute('SELECT COUNT(*) FROM activities')
activity_count = cursor.fetchone()[0]

# Count assessments
cursor.execute('SELECT COUNT(*) FROM assessments')
assessment_count = cursor.fetchone()[0]

# Count courses
cursor.execute('SELECT COUNT(*) FROM courses')
course_count = cursor.fetchone()[0]

print(f'  Students: {student_count:,}')
print(f'  At-risk students: {at_risk_count:,}')
print(f'  Activities: {activity_count:,}')
print(f'  Assessments: {assessment_count:,}')
print(f'  Courses: {course_count:,}')

conn.close()
"

echo ""
echo -e "${GREEN}🎉 System is ready to use!${NC}"
echo ""

