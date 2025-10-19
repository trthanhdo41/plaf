#1. Setup
python3 -m venv venv
source venv/bin/activate
pip install streamlit sqlalchemy google-generativeai scikit-learn plotly python-dotenv scipy joblib threadpoolctl

#2. Load VLE data từ OULAD (chạy 1 lần đầu)
python src/data/load_vle_data.py

#3. Chạy Student Portal
export GEMINI_API_KEY=AIzaSyAyUJgplnBnutMJMbpHhlAvEaBDeo4jXUU
streamlit run src/lms_portal/student_app.py

# Hoặc chạy 1 lệnh:
cd /Users/mac/Desktop/plaf && source venv/bin/activate && GEMINI_API_KEY=AIzaSyAyUJgplnBnutMJMbpHhlAvEaBDeo4jXUU streamlit run src/lms_portal/student_app.py --server.port 8501

# Mở web: http://localhost:8501