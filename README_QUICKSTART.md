# PLAF - Quick Start Guide

## Chọn script theo hệ điều hành

### Windows

```cmd
quick_start_windows.bat
```

### Ubuntu/Linux

```bash
./quick_start.sh
```

### macOS

```bash
./quick_start.sh
```

---

## Script sẽ tự động:

1. ✅ Tạo virtual environment
2. ✅ Cài đặt dependencies
3. ✅ Chạy ML pipeline (train models)
4. ✅ Tạo 8 demo accounts
5. ✅ Khởi động Student Portal

---

## Sau khi script chạy xong:

**Mở browser:** http://localhost:8501

**Login:**
- Email: `student650515@ou.ac.uk`
- Password: `demo123`

---

## Xem hướng dẫn chi tiết:

- **Hướng dẫn đầy đủ:** [SETUP_AND_RUN.md](SETUP_AND_RUN.md)
- **Danh sách accounts:** [DEMO_ACCOUNTS.md](DEMO_ACCOUNTS.md)

---

## Nếu gặp lỗi:

**Windows:**
```cmd
REM Xóa database và tạo lại
del data\lms.db*
python src/data/create_demo_accounts.py
```

**Ubuntu/Linux:**
```bash
# Xóa database và tạo lại
rm -f data/lms.db*
python src/data/create_demo_accounts.py
```

