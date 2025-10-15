# PLAF - Prescriptive Learning Analytics Framework

Hệ thống phân tích học tập và dự đoán sinh viên có nguy cơ không hoàn thành khóa học, kèm theo chatbot AI hỗ trợ học tập.

## Cài đặt

Yêu cầu: Python 3.8+

```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # MacOS/Linux
# hoặc: venv\Scripts\activate  # Windows

# Cài đặt packages
pip install streamlit sqlalchemy google-generativeai faiss-cpu plotly python-dotenv
pip install numpy pandas scikit-learn
```

## Chạy hệ thống

### 1. Student Portal (LMS)

Portal cho sinh viên với dashboard, course materials, và AI chatbot.

```bash
export GEMINI_API_KEY=your_api_key_here
streamlit run src/lms_portal/student_app.py
```

Mở browser: http://localhost:8501

Tính năng:
- Đăng ký/đăng nhập
- Xem dashboard với risk level
- Truy cập course materials
- Chat với AI để nhận tư vấn học tập
- Hệ thống tự động track activity khi xem materials

### 2. Advisor Dashboard

Dashboard cho giảng viên/advisor để theo dõi sinh viên at-risk.

```bash
streamlit run src/dashboard/app.py
```

Tính năng:
- Xem danh sách sinh viên at-risk
- Phân tích SHAP để hiểu lý do dự đoán
- Tạo interventions cho sinh viên
- Xem lịch sử chat và activities

## Cấu trúc project

```
plaf/
├── src/
│   ├── data/              # Data loading và preprocessing
│   ├── models/            # ML models (CatBoost, RF, XGBoost, SVM, LR)
│   ├── explainability/    # SHAP, Anchors
│   ├── prescriptive/      # DiCE, LLM advisor
│   ├── dashboard/         # Advisor dashboard
│   ├── database/          # SQLite database models
│   ├── chatbot/           # RAG system với FAISS
│   └── lms_portal/        # Student portal
├── data/                  # OULAD dataset
├── models/                # Trained models
└── requirements.txt
```

## Database

Hệ thống dùng SQLite với các tables:

- students: Thông tin sinh viên
- activities: Log activities khi xem materials
- assessments: Điểm thi và assignments
- chat_history: Lịch sử chat với AI
- interventions: Các can thiệp của advisor
- course_materials: Danh sách materials

Database tự động tạo khi chạy lần đầu.

## AI Chatbot

Chatbot dùng RAG (Retrieval-Augmented Generation) với:
- FAISS vector database để search knowledge base
- Google Gemini 2.5 Flash để generate responses
- Personalized advice dựa trên student data

Chatbot có thể trả lời câu hỏi về:
- Cách cải thiện điểm số
- Time management
- Study strategies
- Cách sử dụng VLE hiệu quả

## ML Pipeline

Pipeline phân tích gồm 8 bước:

1. Data ingestion từ OULAD dataset
2. Feature engineering với z-score standardization
3. Train models với k-fold cross-validation
4. Global interpretability với SHAP
5. Local explainability cho từng prediction
6. Counterfactual explanations với DiCE
7. Generate advice bằng LLM
8. Dashboard để advisors can thiệp

Để chạy full pipeline:

```bash
python run_pipeline.py
```

## Dataset

Project dùng OULAD (Open University Learning Analytics Dataset).

Download tại: https://analyse.kmi.open.ac.uk/open_dataset

Giải nén vào folder `data/`:
```
data/
├── studentInfo.csv
├── studentVle.csv
├── studentAssessment.csv
├── courses.csv
├── vle.csv
└── assessments.csv
```

## API Keys

Cần Gemini API key để chạy chatbot. Đăng ký tại: https://makersuite.google.com/app/apikey

Có thể set qua environment variable:
```bash
export GEMINI_API_KEY=your_key_here
```

Hoặc tạo file `.env`:
```
GEMINI_API_KEY=your_key_here
```

## Testing

Đã test các components chính:
- Database operations: Tạo student, login, log activity
- RAG system: Vector search và Gemini integration
- Student portal: UI và chatbot
- Real-time data updates

## Notes

- Lần đầu chạy sẽ khởi tạo database và load FAISS index
- Streamlit có thể hỏi email lần đầu, có thể skip
- Port mặc định: 8501 (student portal), 8502 (advisor dashboard)
- Nếu port bị chiếm, dùng: `--server.port 8503`

## Troubleshooting

Nếu gặp lỗi "No module named X":
```bash
pip install X
```

Nếu port bị chiếm:
```bash
lsof -ti:8501 | xargs kill -9
```

Nếu database bị lỗi, xóa và tạo lại:
```bash
rm data/*.db
# Chạy lại app để tự động tạo database mới
```

## Repository

https://github.com/trthanhdo41/plaf

