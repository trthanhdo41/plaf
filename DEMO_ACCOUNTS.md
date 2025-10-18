Đây là danh sách tài khoản demo để test Student Portal với students có data thật từ OULAD dataset.

## DANH SÁCH TÀI KHOẢN

| Student ID | Email | Password | Status | Risk Level |
|------------|-------|----------|--------|------------|
| **432862** | student432862@ou.ac.uk | demo123 | AT-RISK | 21.4% |
| **650515** | student650515@ou.ac.uk | demo123 | AT-RISK | 99.9% |
| **2634238** | student2634238@ou.ac.uk | demo123 | AT-RISK | 100.0% |
| **604655** | student604655@ou.ac.uk | demo123 | AT-RISK | 98.2% |
| **595262** | student595262@ou.ac.uk | demo123 | AT-RISK | 86.4% |
| 513428 | student513428@ou.ac.uk | demo123 | SAFE | 6.6% |
| 588524 | student588524@ou.ac.uk | demo123 | SAFE | 1.7% |
| 348717 | student348717@ou.ac.uk | demo123 | SAFE | 19.7% |

---

## HƯỚNG DẪN SỬ DỤNG

### Bước 1: Chạy Student Portal

```bash
streamlit run src/lms_portal/student_app.py --server.port 8501
```

### Bước 2: Login

1. Mở trình duyệt: http://localhost:8501
2. Click tab **"Login"**
3. Nhập:
   - **Email:** `student650515@ou.ac.uk` (hoặc bất kỳ email nào ở trên)
   - **Password:** `demo123`
4. Click **"Login"**

### Bước 3: Test các tính năng

#### Dashboard 
- Xem tổng quan engagement (VLE clicks, assessments, etc.)
- Xem risk gauge (mức độ rủi ro)
- Nếu là AT-RISK student → có warning đỏ + recommendations

#### Course Materials
- Xem danh sách VLE activities từ OULAD dataset
- Filter theo activity type (resource, quiz, forum, etc.)
- Click "View" để log activity
- **Chat với AI Study Assistant** (cột bên phải)

#### AI Advisor 
- Chat với AI advisor để hỏi về học tập
- Suggested questions có sẵn
- AI sẽ trả lời dựa trên knowledge base
- **Dành cho AT-RISK students:** Advice cá nhân hóa dựa trên predictions

#### Profile
- Xem thông tin cá nhân
- Xem risk status

---

## TEST CASES

### Test 1: AT-RISK Student với risk cao (99.9%)
```
Email: student650515@ou.ac.uk
Password: demo123
```
**Kỳ vọng:**
- Dashboard hiển thị warning đỏ
- Risk gauge ~100%
- AI Advisor đưa ra advice cụ thể để cải thiện

### Test 2: SAFE Student với risk thấp (1.7%)
```
Email: student588524@ou.ac.uk
Password: demo123
```
**Kỳ vọng:**
- Dashboard hiển thị "You're On Track" màu xanh
- Risk gauge ~2%
- Encouragement messages

### Test 3: Chat với AI Study Assistant
1. Login bất kỳ account nào
2. Vào **Course Materials**
3. Hỏi AI ở cột bên phải:
   - "What activities should I focus on?"
   - "How can I improve my grade?"
   - "What resources are most important?"

---

## TẠO LẠI TÀI KHOẢN

Nếu cần tạo lại accounts mới:

```bash
# Xóa database cũ
rm data/lms.db*

# Tạo lại accounts
python src/data/create_demo_accounts.py
```

Script sẽ tự động:
- Load student_predictions.csv
- Chọn ngẫu nhiên 5 at-risk + 3 safe students
- Tạo accounts với email format: `student{ID}@ou.ac.uk`
- Password mặc định: `demo123`

---

## LƯU Ý

1. **Database:** Tài khoản lưu trong `data/lms.db` (SQLite)
2. **Data thật:** Students có data từ OULAD dataset (scores, VLE clicks, etc.)
3. **AI Chatbot:** Cần `GEMINI_API_KEY` trong `.env` để chatbot hoạt động
4. **At-risk status:** Dựa trên ML predictions từ Random Forest model

---

## TROUBLESHOOTING

### Lỗi "Invalid email or password"
- Kiểm tra email đúng format: `student{ID}@ou.ac.uk`
- Password: `demo123` (lowercase)
- Chạy lại `python src/data/create_demo_accounts.py` nếu cần

### Database locked
```bash
rm data/lms.db-journal data/lms.db-wal data/lms.db-shm
```

### Chatbot không hoạt động
- Kiểm tra `GEMINI_API_KEY` trong `.env`
- Xem logs trong terminal

---