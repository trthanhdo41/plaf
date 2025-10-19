# HƯỚNG DẪN CHẠY PLAF SYSTEM (Ubuntu/Linux)

## CÁCH NHANH NHẤT - CHẠY SCRIPT TỰ ĐỘNG

```bash
./quick_start.sh
```

Script sẽ tự động:
1. Tạo virtual environment
2. Cài đặt dependencies
3. Chạy pipeline (train models)
4. Tạo demo accounts
5. Khởi động Student Portal

---

## HƯỚNG DẪN CHI TIẾT (Chạy thủ công)

### Bước 1: Clone repository

```bash
git clone https://github.com/trthanhdo41/plaf.git
cd plaf
```

### Bước 2: Tạo virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 3.5: Cấu hình API Key (TÙY CHỌN)

**Lưu ý:** API key chỉ cần cho AI features (chatbot, AI advisor). Không có API key thì AI features sẽ bị vô hiệu hóa.

#### Cách 1: Script tự động (KHUYẾN NGHỊ)
Khi chạy `./quick_start.sh`, script sẽ tự động hỏi API key:
1. Script hiển thị hướng dẫn lấy API key
2. Nhập API key khi được yêu cầu
3. Script tự động test và cấu hình

#### Cách 2: Thiết lập thủ công
```bash
export GEMINI_API_KEY=YOUR_API_KEY_HERE
```

#### Lấy API key miễn phí:
1. Truy cập: https://aistudio.google.com/app/apikey
2. Đăng nhập Google account
3. Click "Create API Key"
4. Copy và sử dụng

### Bước 4: Chạy pipeline

```bash
python run_pipeline.py
```

Kết quả:
- Model được train (Random Forest ~98% AUC)
- File predictions: `data/processed/student_predictions.csv`
- Best model: `models/best_model.pkl`

### Bước 5: Tạo demo accounts

```bash
python src/data/create_demo_accounts.py
```

Kết quả:
- 8 demo accounts (5 at-risk + 3 safe)
- File: `data/demo_accounts.csv`

### Bước 6: Test login (TÙY CHỌN)

Test xem accounts có login được không:

```bash
python test_login.py
```

Nếu tất cả test PASSED → Accounts sẵn sàng!

### Bước 7: Chạy Student Portal

```bash
streamlit run src/lms_portal/student_app.py --server.port 8501
```

### Bước 8: Login

Mở browser: **http://localhost:8501**

**Tài khoản at-risk (để test chatbot):**
- Email: `student650515@ou.ac.uk`
- Password: `demo123`
- Risk: 99.9%

**Tài khoản safe:**
- Email: `student588524@ou.ac.uk`
- Password: `demo123`
- Risk: 1.7%

---

## DANH SÁCH TÀI KHOẢN ĐẦY ĐỦ

Sau khi chạy script tạo accounts, xem file:

```bash
cat data/demo_accounts.csv
```

Hoặc:

| Student ID | Email | Password | Status | Risk |
|------------|-------|----------|--------|------|
| 432862 | student432862@ou.ac.uk | demo123 | AT-RISK | 21.4% |
| 650515 | student650515@ou.ac.uk | demo123 | AT-RISK | 99.9% |
| 2634238 | student2634238@ou.ac.uk | demo123 | AT-RISK | 100.0% |
| 604655 | student604655@ou.ac.uk | demo123 | AT-RISK | 98.2% |
| 595262 | student595262@ou.ac.uk | demo123 | AT-RISK | 86.4% |
| 513428 | student513428@ou.ac.uk | demo123 | SAFE | 6.6% |
| 588524 | student588524@ou.ac.uk | demo123 | SAFE | 1.7% |
| 348717 | student348717@ou.ac.uk | demo123 | SAFE | 19.7% |

---

## TEST CÁC TÍNH NĂNG

### 1. Dashboard
- Xem risk gauge
- Warning box (nếu at-risk)
- Engagement metrics

### 2. Course Materials + AI Study Assistant
- Xem VLE activities
- Chat với AI (cột bên phải)

### 3. AI Advisor
- Chat với AI advisor
- Nhận personalized advice

### 4. Profile
- Xem thông tin cá nhân
- Risk status

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

Kiểm tra file `.env` có `GEMINI_API_KEY`

Nếu không có API key, toàn bộ hệ thống vẫn chạy được, chỉ chatbot báo lỗi.

---

**Cập nhật:** October 19, 2025
