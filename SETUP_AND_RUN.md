# QUY TRÌNH CHẠY ĐẦY ĐỦ PLAF SYSTEM

Hướng dẫn này giúp bạn chạy toàn bộ hệ thống PLAF từ đầu đến cuối trên Ubuntu/Linux.

---

## BƯỚC 1: CÀI ĐẶT MÔI TRƯỜNG

### 1.1. Clone repository

```bash
git clone https://github.com/trthanhdo41/plaf.git
cd plaf
```

### 1.2. Tạo virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 1.4. Cấu hình API key (TÙY CHỌN - chỉ cần nếu muốn dùng chatbot)

Tạo file `.env`:

```bash
nano .env
```

Thêm nội dung (nếu có API key):

```
GEMINI_API_KEY=your_api_key_here
```

Lưu và thoát (Ctrl+O, Enter, Ctrl+X).

**LƯU Ý:** Nếu không có API key, bạn vẫn có thể chạy toàn bộ hệ thống, chỉ chatbot sẽ không hoạt động.

---

## BƯỚC 2: CHẠY PIPELINE (Train model và tạo predictions)

### 2.1. Chạy pipeline đầy đủ

```bash
python run_pipeline.py
```

**Thời gian:** ~2-3 phút

**Kết quả mong đợi:**
- Model được train (Random Forest, Logistic Regression, SVM)
- File predictions: `data/processed/student_predictions.csv`
- Best model: `models/best_model.pkl`
- Test AUC: ~98%

**Kiểm tra kết quả:**

```bash
ls -lh data/processed/student_predictions.csv
ls -lh models/best_model.pkl
```

---

## BƯỚC 3: TẠO DEMO ACCOUNTS

### 3.1. Chạy script tạo accounts

```bash
python src/data/create_demo_accounts.py
```

**Kết quả:**
- Tạo 8 demo accounts (5 at-risk + 3 safe)
- File danh sách: `data/demo_accounts.csv`
- Database: `data/lms.db`

### 3.2. Xem danh sách accounts

```bash
cat data/demo_accounts.csv
```

Hoặc xem file `DEMO_ACCOUNTS.md` để biết chi tiết.

**Ví dụ accounts:**
- Email: `student650515@ou.ac.uk`, Password: `demo123` (AT-RISK 99.9%)
- Email: `student2634238@ou.ac.uk`, Password: `demo123` (AT-RISK 100%)
- Email: `student588524@ou.ac.uk`, Password: `demo123` (SAFE 1.7%)

---

## BƯỚC 4: CHẠY STUDENT PORTAL

### 4.1. Khởi động Student Portal

```bash
streamlit run src/lms_portal/student_app.py --server.port 8501
```

### 4.2. Mở trình duyệt

Truy cập: **http://localhost:8501**

### 4.3. Login

1. Click tab **"Login"**
2. Nhập:
   - Email: `student650515@ou.ac.uk`
   - Password: `demo123`
3. Click **"Login"**

**Nếu gặp lỗi "Invalid email or password":**

Chạy lại script tạo accounts:

```bash
# Xóa database cũ
rm -f data/lms.db*

# Tạo lại accounts
python src/data/create_demo_accounts.py
```

---

## BƯỚC 5: TEST CÁC TÍNH NĂNG

### 5.1. Dashboard

Sau khi login, bạn sẽ thấy:
- **Risk Gauge** (đồng hồ đo rủi ro)
- **Warning box** (nếu at-risk)
- **Engagement metrics**

### 5.2. Course Materials + AI Study Assistant

1. Click sidebar → **"Course Materials"**
2. Xem VLE activities từ OULAD dataset
3. **Chat với AI** (cột bên phải):
   - "What activities should I focus on?"
   - "How can I improve my grade?"

### 5.3. AI Advisor (Chatbot chính)

1. Click sidebar → **"AI Advisor"**
2. Chat với AI advisor:
   - "I'm at risk of failing. What should I do?"
   - "How can I improve my engagement?"
3. Click **Suggested Questions** để test nhanh

### 5.4. Profile

Click sidebar → **"Profile"** để xem thông tin cá nhân và risk status.

---

## BƯỚC 6: CHẠY ADVISOR DASHBOARD (TÙY CHỌN)

### 6.1. Khởi động Advisor Dashboard

Mở terminal mới:

```bash
cd plaf
source venv/bin/activate
streamlit run src/dashboard/app.py --server.port 8502
```

### 6.2. Mở trình duyệt

Truy cập: **http://localhost:8502**

### 6.3. Chức năng

- Xem danh sách tất cả students
- Filter by risk level, module, presentation
- Xem chi tiết predictions và feature importance

---

## BƯỚC 7: CHẠY BENCHMARK (TÙY CHỌN)

### 7.1. Benchmark RAG System

```bash
python tests/benchmark_rag.py
```

**Yêu cầu:** Cần GEMINI_API_KEY trong `.env`

### 7.2. Benchmark LLM Advisor

```bash
python tests/benchmark_llm.py
```

**Yêu cầu:** Cần GEMINI_API_KEY trong `.env`

---

## TÓM TẮT QUY TRÌNH NHANH

```bash
# 1. Clone và setup
git clone https://github.com/trthanhdo41/plaf.git
cd plaf
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Chạy pipeline
python run_pipeline.py

# 3. Tạo demo accounts
python src/data/create_demo_accounts.py

# 4. Chạy Student Portal
streamlit run src/lms_portal/student_app.py --server.port 8501

# 5. Mở browser: http://localhost:8501
# Login: student650515@ou.ac.uk / demo123
```

---

## TROUBLESHOOTING

### Lỗi "Invalid email or password"

```bash
rm -f data/lms.db*
python src/data/create_demo_accounts.py
```

### Lỗi "database is locked"

```bash
pkill -f streamlit
rm -f data/lms.db-journal data/lms.db-wal data/lms.db-shm
```

### Lỗi "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### Chatbot không hoạt động

Kiểm tra:
1. File `.env` có `GEMINI_API_KEY`
2. API key còn valid không
3. Xem logs trong terminal

**LƯU Ý:** Nếu không có API key, toàn bộ hệ thống vẫn chạy được, chỉ chatbot báo lỗi.

---

## KẾT QUẢ MONG ĐỢI

Sau khi hoàn thành, bạn sẽ có:

1. ✅ Model được train với AUC ~98%
2. ✅ 8 demo accounts để test
3. ✅ Student Portal chạy tại http://localhost:8501
4. ✅ Dashboard hiển thị risk gauge và warnings
5. ✅ Chatbot hoạt động (nếu có API key)
6. ✅ VLE activities từ OULAD dataset

---

## HỖ TRỢ

Nếu gặp vấn đề:
1. Xem file `DEMO_ACCOUNTS.md` cho danh sách tài khoản
2. Xem logs trong terminal
3. Kiểm tra file `data/demo_accounts.csv`

---

**Cập nhật:** October 18, 2025  
**Version:** PLAF v1.0

