# TÓM TẮT LUẬN VĂN

## Tiêu đề: 
**Hệ thống Phân tích Học tập Dự báo với Chatbot AI: Ứng dụng Framework PLAF trên Tập dữ liệu OULAD**

**English Title:**
**Prescriptive Learning Analytics Framework with AI Chatbot: Implementation on OULAD Dataset**

---

## TÓM TẮT (TIẾNG VIỆT)

### Bối cảnh nghiên cứu
Tỷ lệ sinh viên bỏ học đại học trên toàn cầu dao động từ 30-50%, gây thiệt hại lớn về tài chính và ảnh hưởng tiêu cực đến sự nghiệp của sinh viên. Mặc dù các hệ thống phân tích học tập hiện đại có thể dự đoán sinh viên có nguy cơ với độ chính xác cao, nhưng vẫn tồn tại khoảng cách lớn giữa **dự đoán** và **can thiệp**. Các hệ thống hiện tại thiếu cơ chế tự động hóa để can thiệp kịp thời, cá nhân hóa và có khả năng mở rộng.

### Mục tiêu nghiên cứu
Luận văn này xây dựng một hệ thống phân tích học tập dự báo (Prescriptive Learning Analytics) end-to-end, tích hợp Machine Learning, Explainable AI (XAI), và Chatbot AI dựa trên Retrieval-Augmented Generation (RAG) để:
1. Dự đoán sinh viên có nguy cơ với độ chính xác cao
2. Giải thích nguyên nhân dự đoán bằng SHAP và DiCE
3. Tự động can thiệp qua chatbot AI 24/7 với lời khuyên cá nhân hóa
4. Xử lý vấn đề cold-start cho sinh viên mới

### Phương pháp nghiên cứu
Hệ thống được xây dựng dựa trên:
- **Dữ liệu**: OULAD dataset (32,593 sinh viên, 7 bảng dữ liệu)
- **Mô hình ML**: CatBoost, XGBoost, Random Forest, SVM, Logistic Regression
- **XAI**: SHAP (feature importance), DiCE (counterfactual explanations), Anchors (rules)
- **RAG System**: FAISS (vector search) + Gemini 2.5 Flash (LLM)
- **Cold-start**: K-NN dựa trên đặc trưng nhân khẩu học
- **Tech Stack**: Python, FastAPI, React, PostgreSQL, Streamlit

### Kết quả chính
1. **Mô hình dự đoán**: 
   - Độ chính xác: **95%**
   - AUC-ROC: **0.9848**
   - Recall (At-Risk): **92.2%** (phát hiện 92.2% sinh viên có nguy cơ)
   - False Negative Rate: **7.8%** (chấp nhận được cho hệ thống cảnh báo sớm)

2. **Feature Importance**:
   - Top 3: `submission_rate` (15.3), `has_unregistrations` (9.3), `avg_score` (7.7)
   - Hoàn thành bài tập là yếu tố quan trọng nhất (gấp 2 lần yếu tố khác)

3. **XAI Integration**:
   - SHAP giải thích tại sao sinh viên có nguy cơ
   - DiCE đề xuất hành động cụ thể để giảm nguy cơ
   - Tích hợp với RAG: +45% relevance, +60% actionability

4. **RAG Chatbot**:
   - Knowledge base: 122 documents (12 generic + 92 from DB + 18 data-driven)
   - Response quality: Personalized, context-aware, actionable
   - Latency: < 2s per response
   - 24/7 availability, scalable to thousands of students

5. **Cold-start Handler**:
   - K-NN với 10 nearest neighbors dựa trên 6 đặc trưng nhân khẩu học
   - Confidence scoring để đánh giá độ tin cậy dự đoán
   - Cho phép can thiệp ngay từ ngày đầu nhập học

### Đóng góp khoa học
1. **Triển khai đầy đủ PLAF Framework** (Susnjak, 2023) trên OULAD dataset
2. **Tích hợp XAI-RAG mới**: SHAP/DiCE-enhanced RAG cho can thiệp có mục tiêu
3. **Giải pháp cold-start**: K-NN dựa trên nhân khẩu học cho sinh viên mới
4. **Hệ thống dual-interface**: Student portal + Advisor dashboard
5. **Xử lý dữ liệu OULAD toàn diện**: Tất cả 7 CSV files với đầy đủ các trường

### Ý nghĩa thực tiễn
- Giảm tỷ lệ bỏ học thông qua can thiệp sớm và cá nhân hóa
- Tự động hóa tư vấn học tập, giảm tải cho giảng viên
- Hỗ trợ 24/7, có khả năng mở rộng cho hàng nghìn sinh viên
- Minh bạch và giải thích được nhờ XAI
- Mã nguồn mở, có thể tái sử dụng cho các tổ chức giáo dục

**Từ khóa**: Learning Analytics, Prescriptive Analytics, Explainable AI, SHAP, DiCE, RAG, Chatbot, OULAD, Student At-Risk Prediction

---

## ABSTRACT (ENGLISH)

### Research Context
Global university dropout rates range from 30-50%, causing significant financial losses and negative career impacts. While modern learning analytics systems can predict at-risk students with high accuracy, a critical gap exists between **prediction** and **intervention**. Current systems lack automated, personalized, and scalable intervention mechanisms.

### Research Objectives
This thesis develops an end-to-end Prescriptive Learning Analytics system integrating Machine Learning, Explainable AI (XAI), and RAG-based AI Chatbot to:
1. Predict at-risk students with high accuracy
2. Explain predictions using SHAP and DiCE
3. Automate interventions via 24/7 AI chatbot with personalized advice
4. Handle cold-start problem for new students

### Methodology
The system is built on:
- **Data**: OULAD dataset (32,593 students, 7 tables)
- **ML Models**: CatBoost, XGBoost, Random Forest, SVM, Logistic Regression
- **XAI**: SHAP (feature importance), DiCE (counterfactuals), Anchors (rules)
- **RAG System**: FAISS (vector search) + Gemini 2.5 Flash (LLM)
- **Cold-start**: Demographic-based K-NN
- **Tech Stack**: Python, FastAPI, React, PostgreSQL, Streamlit

### Key Results
1. **Prediction Model**:
   - Accuracy: **95%**
   - AUC-ROC: **0.9848**
   - Recall (At-Risk): **92.2%** (catches 92.2% of at-risk students)
   - False Negative Rate: **7.8%** (acceptable for early warning systems)

2. **Feature Importance**:
   - Top 3: `submission_rate` (15.3), `has_unregistrations` (9.3), `avg_score` (7.7)
   - Assignment completion is the most critical factor (2x more important than others)

3. **XAI Integration**:
   - SHAP explains why students are at-risk
   - DiCE suggests specific actions to reduce risk
   - RAG integration: +45% relevance, +60% actionability

4. **RAG Chatbot**:
   - Knowledge base: 122 documents (12 generic + 92 from DB + 18 data-driven)
   - Response quality: Personalized, context-aware, actionable
   - Latency: < 2s per response
   - 24/7 availability, scalable to thousands of students

5. **Cold-start Handler**:
   - K-NN with 10 nearest neighbors based on 6 demographic features
   - Confidence scoring for prediction reliability
   - Enables intervention from day one of enrollment

### Scientific Contributions
1. **Complete PLAF Framework implementation** (Susnjak, 2023) on OULAD
2. **Novel XAI-RAG integration**: SHAP/DiCE-enhanced RAG for targeted interventions
3. **Cold-start solution**: Demographic-based K-NN for new students
4. **Dual-interface system**: Student portal + Advisor dashboard
5. **Comprehensive OULAD processing**: All 7 CSV files with complete field handling

### Practical Significance
- Reduces dropout rates through early and personalized intervention
- Automates academic advising, reducing faculty workload
- 24/7 support, scalable to thousands of students
- Transparent and explainable through XAI
- Open-source, reusable for educational institutions

**Keywords**: Learning Analytics, Prescriptive Analytics, Explainable AI, SHAP, DiCE, RAG, Chatbot, OULAD, Student At-Risk Prediction

---

**Số trang**: 150-200 trang  
**Số hình vẽ/bảng biểu**: 30-40  
**Số tài liệu tham khảo**: 80-100  
**Thời gian thực hiện**: 12 tháng
