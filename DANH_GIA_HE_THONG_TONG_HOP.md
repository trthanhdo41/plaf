# Đánh Giá Hệ Thống Tổng Hợp - PLAF System

## Tóm Tắt Điều Hành

Tài liệu này cung cấp đánh giá kỹ thuật toàn diện về hệ thống dự đoán sinh viên có nguy cơ (at-risk prediction), bao gồm:
- **Mô tả Dataset OULAD**: Giải thích chi tiết 7 file CSV và cấu trúc dữ liệu
- **Xử lý dữ liệu OULAD**: Đánh giá cách hệ thống xử lý dữ liệu
- **Kiến trúc hệ thống**: Đánh giá các component SHAP, DiCE, RAG và tích hợp
- **Khoảng trống tích hợp**: Xác định các vấn đề tích hợp quan trọng

**Đánh Giá Tổng Thể**: ⚠️ **Kiến Trúc Tốt, Nhưng Thiếu Tích Hợp và Một Số Trường Dữ Liệu**

- ✅ **Điểm Mạnh**: Component được cấu trúc tốt, xử lý dữ liệu cơ bản đúng
- ❌ **Khoảng Trống Nghiêm Trọng**: SHAP/DiCE chưa được tích hợp với RAG; Thiếu nhiều trường dữ liệu quan trọng
- ⚠️ **Tác Động**: Can thiệp còn chung chung thay vì nhắm vào các yếu tố rủi ro cụ thể

---

## Phần 1: Mô Tả Dataset OULAD

### 1.1 Tổng Quan Dataset

OULAD (Open University Learning Analytics Dataset) là dataset về hoạt động học tập trực tuyến, bao gồm 7 file CSV chứa thông tin về sinh viên, khóa học, đánh giá và tương tác VLE.

### 1.2 Chi Tiết Từng File

#### 1. courses.csv

**Mô tả:** File chứa danh sách tất cả các module và presentation có sẵn.

**Các cột:**
- `code_module` - Mã định danh của module
- `code_presentation` - Mã định danh của presentation (gồm năm + "B" cho presentation bắt đầu tháng 2, "J" cho presentation bắt đầu tháng 10)
- `length` - Độ dài của module-presentation tính bằng **ngày**

**Lưu ý quan trọng:**
- Cấu trúc của presentation B và J có thể khác nhau, nên **phân tích riêng** là tốt nhất
- Đối với một số module (CCC, EEE, GGG), presentation tương ứng B/J không tồn tại, do đó phải sử dụng J để thông tin cho B hoặc ngược lại

---

#### 2. assessments.csv

**Mô tả:** File chứa thông tin về các đánh giá trong module-presentation. Thông thường, mỗi presentation có một số đánh giá theo sau bởi kỳ thi cuối.

**Các cột:**
- `code_module` - Mã định danh của module mà đánh giá thuộc về
- `code_presentation` - Mã định danh của presentation mà đánh giá thuộc về
- `id_assessment` - Số định danh của đánh giá
- `assessment_type` - Loại đánh giá. Có 3 loại: **TMA** (Tutor Marked Assessment), **CMA** (Computer Marked Assessment) và **Exam** (Final Exam)
- `date` - Thông tin về ngày nộp cuối cùng của đánh giá, được tính bằng số ngày kể từ khi module-presentation bắt đầu. Ngày bắt đầu presentation có số 0 (zero)
- `weight` - Trọng số của đánh giá tính bằng %. Thông thường, **Exam được xử lý riêng và có trọng số 100%**; tổng của tất cả các đánh giá khác là 100%

**Lưu ý:**
- Nếu thông tin về ngày thi cuối cùng bị thiếu, nó nằm ở cuối tuần presentation cuối cùng

---

#### 3. vle.csv

**Mô tả:** File chứa thông tin về các tài liệu có sẵn trong VLE (Virtual Learning Environment). Thông thường, đây là các trang HTML, file PDF, v.v. Sinh viên có quyền truy cập các tài liệu này trực tuyến và các tương tác của họ với tài liệu được ghi lại.

**Các cột:**
- `id_site` - Số định danh của tài liệu
- `code_module` - Mã định danh cho module
- `code_presentation` - Mã định danh của presentation
- `activity_type` - Vai trò liên quan đến tài liệu module
- `week_from` - Tuần từ đó tài liệu được lên kế hoạch sử dụng
- `week_to` - Tuần đến đó tài liệu được lên kế hoạch sử dụng

---

#### 4. studentInfo.csv

**Mô tả:** File chứa thông tin nhân khẩu học về sinh viên cùng với kết quả của họ.

**Các cột:**
- `code_module` - Mã định danh cho module mà sinh viên đã đăng ký
- `code_presentation` - Mã định danh của presentation trong thời gian sinh viên đăng ký module
- `id_student` - Số định danh duy nhất cho sinh viên
- `gender` - Giới tính của sinh viên
- `region` - Xác định vùng địa lý, nơi sinh viên sống khi tham gia module-presentation
- `highest_education` - Trình độ giáo dục cao nhất của sinh viên khi vào module presentation
- `imd_band` - Chỉ định Index of Multiple Deprivation band của nơi sinh viên sống trong thời gian module-presentation
- `age_band` - Nhóm tuổi của sinh viên
- `num_of_prev_attempts` - **Số lần sinh viên đã thử module này** ⚠️
- `studied_credits` - **Tổng số tín chỉ cho các module sinh viên đang học** ⚠️
- `disability` - Cho biết sinh viên có khai báo khuyết tật hay không
- `final_result` - Kết quả cuối cùng của sinh viên trong module-presentation (Pass/Fail/Withdrawn/Distinction)

---

#### 5. studentRegistration.csv

**Mô tả:** File chứa thông tin về thời điểm sinh viên đăng ký cho module presentation. Đối với sinh viên đã hủy đăng ký, ngày hủy đăng ký cũng được ghi lại.

**Các cột:**
- `code_module` - Mã định danh cho module
- `code_presentation` - Mã định danh của presentation
- `id_student` - Số định danh duy nhất cho sinh viên
- `date_registration` - Ngày đăng ký của sinh viên cho module presentation, đây là số ngày được đo tương đối so với khi module-presentation bắt đầu (ví dụ: giá trị âm -30 có nghĩa là sinh viên đã đăng ký module presentation 30 ngày trước khi nó bắt đầu)
- `date_unregistration` - Ngày hủy đăng ký của sinh viên từ module presentation, đây là số ngày được đo tương đối so với khi module-presentation bắt đầu. Sinh viên đã hoàn thành khóa học có trường này **rỗng**. Sinh viên đã hủy đăng ký có giá trị **Withdrawal** trong cột `final_result` của file studentInfo.csv

---

#### 6. studentAssessment.csv

**Mô tả:** File chứa kết quả đánh giá của sinh viên. Nếu sinh viên không nộp đánh giá, không có kết quả được ghi lại. Kết quả thi cuối cùng bị thiếu nếu kết quả đánh giá không được lưu trong hệ thống.

**Các cột:**
- `id_assessment` - Số định danh của đánh giá
- `id_student` - Số định danh duy nhất cho sinh viên
- `date_submitted` - Ngày sinh viên nộp bài, được đo bằng số ngày kể từ khi module presentation bắt đầu
- `is_banked` - **Cờ trạng thái cho biết kết quả đánh giá đã được chuyển từ presentation trước** ⚠️
- `score` - Điểm của sinh viên trong đánh giá này. Phạm vi từ 0 đến 100. **Điểm thấp hơn 40 được hiểu là Fail**. Điểm trong phạm vi từ 0 đến 100

---

#### 7. studentVle.csv

**Mô tả:** File chứa thông tin về tương tác của mỗi sinh viên với các tài liệu trong VLE.

**Các cột:**
- `code_module` - Mã định danh cho module
- `code_presentation` - Mã định danh của module presentation
- `id_student` - Số định danh duy nhất cho sinh viên
- `id_site` - Số định danh cho tài liệu VLE
- `date` - Ngày sinh viên tương tác với tài liệu, được đo bằng số ngày kể từ khi module-presentation bắt đầu
- `sum_click` - **Số lần sinh viên tương tác với tài liệu trong ngày đó**

---

## Phần 2: Đánh Giá Xử Lý Dữ Liệu OULAD

### 2.1 Tóm Tắt

#### ✅ **Xử Lý Đúng:**
- Tải cơ bản cho tất cả 7 file CSV
- Tương tác VLE (studentVle.csv) với `sum_click` được xử lý chính xác
- Tính toán điểm đánh giá cơ bản

#### ⚠️ **Vấn Đề Nghiêm Trọng:**

| File | Vấn Đề | Trạng Thái |
|------|--------|-----------|
| **studentInfo.csv** | Thiếu `num_of_prev_attempts`, `studied_credits` | ❌ |
| **studentAssessment.csv** | Thiếu `is_banked` | ❌ |
| **assessments.csv** | Merge sai (chỉ trên `id_assessment`), không dùng `type`/`weight`/`date` | ⚠️ |
| **studentRegistration.csv** | Không tính toán đúng `date_registration` | ⚠️ |
| **courses.csv** | Không sử dụng `length` | ⚠️ |
| **vle.csv** | `week_from`/`week_to` là TEXT thay vì INTEGER | ⚠️ |
| **studentVle.csv** | Không có vấn đề | ✅ |

### 2.2 Vấn Đề Schema Database

**Bảng `students` - Thiếu:**
- `num_of_prev_attempts` (INTEGER)
- `studied_credits` (INTEGER)

**Bảng `assessments` - Thiếu:**
- `is_banked` (INTEGER)

---

## Phần 3: Kiến Trúc Hệ Thống và Tích Hợp

### 3.1 Luồng Dữ Liệu Hiện Tại

```
[OULAD Dataset] → [Preprocessing] → [Feature Engineering] → [ML Model]
    ↓
[SHAP + DiCE] → [❌ THIẾU KẾT NỐI ❌] → [RAG] → [Generic Interventions]
```

### 3.2 Khoảng Trống Tích Hợp

| Component | Trạng Thái | Tích Hợp với RAG |
|-----------|--------|-----------------|
| **SHAP Explainer** | ✅ Hoạt động | ❌ **CHƯA** |
| **DiCE Counterfactuals** | ✅ Hoạt động | ❌ **CHƯA** |
| **RAG System** | ✅ Hoạt động | ⚠️ Thiếu input SHAP/DiCE |

**Vấn đề:**
- SHAP/DiCE tạo explanations nhưng **không được truyền đến RAG**
- RAG tạo lời khuyên chung chung thay vì nhắm đích vào yếu tố rủi ro cụ thể

### 3.3 Luồng Dữ Liệu Đề Xuất

```
[Student Query] → [Fetch Context] → [Fetch SHAP] → [Fetch DiCE]
    ↓
[Enhanced RAG Query] → [Targeted Retrieval] → [Personalized Intervention]
```

---

## Phần 4: Ưu Tiên Sửa Lỗi

### 🔴 **Nghiêm Trọng** (Tuần 1)

1. **Thêm `num_of_prev_attempts` và `studied_credits`** vào database
2. **Thêm `is_banked`** vào assessments table
3. **Sửa merge assessments** - bao gồm `code_module` và `code_presentation`
4. **Sửa tính toán nộp muộn** - so sánh `date_submitted` với `date` (due date)
5. **Tích hợp SHAP với RAG** - Thêm endpoint, truyền SHAP data
6. **Tích hợp DiCE với RAG** - Thêm endpoint, truyền DiCE data

### 🟡 **Quan Trọng** (Tuần 2)

7. Sử dụng `assessment_type` để phân biệt TMA/CMA/Exam
8. Sử dụng `weight` cho điểm trung bình có trọng số
9. Sử dụng đúng `date_registration` cho đặc trưng đăng ký sớm
10. Đổi `week_from`/`week_to` sang INTEGER

### 🟢 **Cải Thiện** (Tuần 3-4)

11. Sử dụng `length` từ courses.csv
12. Nâng cao knowledge base với nội dung dựa trên SHAP
13. Thêm caching cho performance

---

## Phần 5: Kế Hoạch Hành Động

### 1: Sửa Lỗi Dữ Liệu + Tích Hợp Cơ Bản
- [ ] Thêm các trường thiếu vào database schema
- [ ] Sửa merge và tính toán trong preprocessing
- [ ] Thêm SHAP/DiCE API endpoints
- [ ] Cập nhật RAG chat method để nhận SHAP/DiCE

### 2: Nâng Cao Tích Hợp
- [ ] Nâng cao RAG response generation với SHAP/DiCE
- [ ] Cập nhật intervention generation
- [ ] Sửa các vấn đề assessment features

### 3: Tối Ưu
- [ ] Nâng cao knowledge base
- [ ] Thêm caching
- [ ] Thêm tests

---

