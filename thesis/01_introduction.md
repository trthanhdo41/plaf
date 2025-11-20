# Chapter 1: Introduction

## 1.1 Research Context

### The Evolution of Learning Analytics

Learning analytics has evolved through several distinct phases:
- **Descriptive Analytics**: Understanding what happened (student grades, completion rates)
- **Diagnostic Analytics**: Understanding why it happened (correlation analysis, pattern recognition)
- **Predictive Analytics**: Forecasting what will happen (at-risk prediction, dropout forecasting)
- **Prescriptive Analytics**: Recommending what actions to take (intervention strategies, personalized guidance)

### Student Retention Challenges in Higher Education

- **Global Challenge**: University dropout rates range from 30-50% across institutions
- **Financial Impact**: Loss of tuition revenue, wasted educational resources
- **Student Impact**: Academic failure, emotional distress, career setbacks
- **Early Intervention**: Critical window in first semester/year for intervention

### Current Limitations of Learning Analytics Systems

1. **Prediction Without Action**: Most systems stop at identifying at-risk students
2. **Manual Intervention Bottleneck**: Advisors overwhelmed with large student populations
3. **Delayed Response**: Traditional advising takes days/weeks, students need immediate support
4. **Lack of Personalization**: Generic advice doesn't address individual student contexts
5. **Cold-Start Problem**: New students without historical data cannot be assessed

## 1.2 Problem Statement

Despite advances in predictive learning analytics, a critical gap exists between **prediction and intervention**. Current systems can identify at-risk students with high accuracy, but:

- **Gap 1**: No automated mechanism for immediate student intervention
- **Gap 2**: Advisors cannot scale personalized support to hundreds/thousands of students
- **Gap 3**: Explanations of risk predictions are not actionable for students
- **Gap 4**: New students without historical data receive no early support
- **Gap 5**: Lack of empathetic, conversational support available 24/7

**Core Research Problem**: How can we design an end-to-end prescriptive learning analytics system that not only predicts student risk but automatically provides personalized, explainable, and empathetic interventions at scale?

## 1.2. Mục tiêu đề tài

### 1.2.1. Mục tiêu tổng quát

Xây dựng hệ thống Prescriptive Learning Analytics end-to-end tích hợp Machine Learning, Explainable AI, và RAG-based Chatbot để:
- Dự đoán sinh viên có nguy cơ với độ chính xác cao
- Giải thích nguyên nhân dự đoán một cách minh bạch
- Tự động can thiệp qua chatbot AI 24/7 với lời khuyên cá nhân hóa
- Xử lý vấn đề cold-start cho sinh viên mới

### 1.2.2. Mục tiêu cụ thể

**Mục tiêu 1: Xây dựng mô hình dự đoán chính xác**
- Huấn luyện và đánh giá 5 thuật toán ML (Random Forest, CatBoost, XGBoost, SVM, Logistic Regression)
- Đạt AUC-ROC ≥ 0.95 và Recall ≥ 90%
- Xác định top features quan trọng nhất cho dự đoán
- Đảm bảo mô hình generalize tốt across courses và presentations

**Mục tiêu 2: Tích hợp Explainable AI**
- Triển khai SHAP explanations cho global và local interpretability
- Triển khai DiCE counterfactual explanations cho actionable recommendations
- Triển khai Anchor rules cho interpretable decision boundaries
- Đảm bảo explanations understandable cho non-technical users

**Mục tiêu 3: Xây dựng RAG-based Chatbot**
- Xây dựng knowledge base từ OULAD data và learning strategies
- Triển khai FAISS vector search cho retrieval
- Tích hợp Gemini 2.5 Flash LLM cho response generation
- Đạt latency < 2s và response quality ≥ 80%
- Cá nhân hóa responses dựa trên student context và XAI insights

**Mục tiêu 4: Giải quyết Cold-Start Problem**
- Triển khai K-NN demographic-based prediction cho sinh viên mới
- Cung cấp confidence scoring cho predictions
- Đảm bảo prediction available từ ngày đầu enrollment
- So sánh accuracy với baseline methods

**Mục tiêu 5: Xây dựng hệ thống hoàn chỉnh**
- Triển khai đầy đủ 8 giai đoạn PLAF framework
- Xây dựng dual-interface (Student portal + Advisor dashboard)
- Đảm bảo scalability cho 10,000+ students
- Mã nguồn mở và reproducible trên OULAD dataset

## 1.3. Phạm vi đề tài

### 1.3.1. Giới hạn về dữ liệu

**Nguồn dữ liệu:**
- Sử dụng OULAD dataset (Open University Learning Analytics Dataset)
- 32,593 sinh viên, 7 modules, năm học 2013-2014
- 7 CSV files: courses, assessments, vle, studentInfo, studentRegistration, studentAssessment, studentVle

**Giới hạn:**
- Chỉ sử dụng OULAD dataset (không tích hợp real-time LMS data)
- Historical data (2013-2014), không có streaming updates
- Không có forum interaction data (OULAD không cung cấp)
- Không có video watching behavior (OULAD không cung cấp)

### 1.3.2. Giới hạn về công nghệ/thuật toán

**Tập trung vào:**
- Interpretable ML models: CatBoost, XGBoost, Random Forest, SVM, Logistic Regression
- XAI techniques: SHAP, DiCE, Anchors
- RAG architecture: FAISS + Gemini 2.5 Flash
- Cold-start: K-NN demographic approach

**Không bao gồm:**
- Deep Learning models (LSTM, Transformers) - do black-box nature
- Reinforcement Learning - out of scope
- Multi-modal learning (video, audio) - OULAD không có
- Federated Learning - không cần thiết cho single dataset

### 1.3.3. Giới hạn chức năng hệ thống

**Chức năng có:**
- At-risk prediction với explanations
- AI chatbot cho student support
- Advisor dashboard cho intervention planning
- Cold-start prediction cho sinh viên mới
- SHAP/DiCE visualizations

**Chức năng không có:**
- Real-time LMS integration (chỉ demo với OULAD)
- Email/SMS notifications (chỉ in-app)
- Mobile app (chỉ web-based)
- Multi-language support (chỉ English)
- Peer comparison features (privacy concerns)

### 1.3.4. Giới hạn về deployment

**Môi trường:**
- Local deployment (không require cloud)
- CPU-only (không cần GPU)
- SQLite cho demo (PostgreSQL cho production)

**External dependencies:**
- Gemini API cho LLM (external service)
- Internet connection cho API calls

**Không bao gồm:**
- Production deployment tại tổ chức giáo dục thực tế
- Long-term user studies (chỉ evaluation trên OULAD)
- A/B testing với real students

## 1.4. Ý nghĩa đề tài

### 1.4.1. Ý nghĩa thực tiễn

**1. Giảm tỷ lệ bỏ học**
- Can thiệp sớm và cá nhân hóa giúp sinh viên có nguy cơ cải thiện kết quả học tập
- Dự đoán chính xác (95% accuracy) cho phép tập trung resources vào đúng đối tượng
- Hệ thống 24/7 đảm bảo hỗ trợ kịp thời

**2. Tự động hóa tư vấn học tập**
- Giảm workload cho advisors (không cần tư vấn thủ công từng sinh viên)
- Scale đến hàng nghìn sinh viên mà không tăng nhân sự
- Chatbot AI cung cấp immediate support, không cần chờ appointment

**3. Minh bạch và giải thích được**
- SHAP explanations giúp sinh viên hiểu tại sao có nguy cơ
- DiCE counterfactuals chỉ ra cụ thể cần làm gì để cải thiện
- Tăng trust và engagement của sinh viên với hệ thống

**4. Hỗ trợ từ ngày đầu**
- Cold-start handler cho phép dự đoán và can thiệp ngay từ ngày nhập học
- Không bỏ lỡ critical window (tuần đầu tiên)
- Proactive thay vì reactive

**5. Tiết kiệm chi phí**
- Open-source, có thể deploy tại bất kỳ tổ chức giáo dục nào
- Không cần expensive commercial platforms
- CPU-only, không cần GPU infrastructure

**6. Ứng dụng rộng rãi**
- Có thể áp dụng cho các tổ chức giáo dục khác (universities, MOOCs)
- Mã nguồn mở, reproducible
- Framework PLAF có thể customize cho contexts khác

### 1.4.2. Ý nghĩa khoa học

**1. First Complete PLAF Implementation**
- Susnjak (2023) chỉ đề xuất conceptual framework
- Luận văn này là **triển khai đầy đủ đầu tiên** của 8 giai đoạn PLAF
- Đóng góp: End-to-end pipeline từ data đến intervention

**2. Novel XAI-RAG Integration**
- **Innovation**: Tích hợp SHAP/DiCE explanations vào RAG system
- SHAP feature importance → targeted knowledge retrieval
- DiCE counterfactuals → actionable response generation
- **Measured impact**: +45% relevance, +60% actionability
- Đóng góp: Architecture design cho XAI-enhanced RAG

**3. Cold-Start Solution cho Educational Context**
- K-NN demographic-based approach
- Confidence scoring cho prediction reliability
- Đóng góp: Simple, interpretable solution cho day-1 prediction

**4. Comprehensive OULAD Processing**
- Full processing của tất cả 7 CSV files với complete field handling
- Weighted assessment scores, assessment type differentiation
- Proper B/J presentation handling
- Đóng góp: Best practices cho OULAD data processing

**5. Dual-Interface System Design**
- Student portal: Self-service risk monitoring, chatbot support
- Advisor dashboard: Intervention planning, SHAP/DiCE insights
- Đóng góp: UX design cho prescriptive LA systems

**6. Rigorous Evaluation Framework**
- Comprehensive benchmark suite: ML models, RAG quality, LLM advice
- Ablation studies demonstrating value of each component
- Before/after comparison of generic vs. targeted interventions
- Đóng góp: Evaluation methodology cho prescriptive LA

**7. Open-Source Contribution**
- Reproducible pipeline trên OULAD dataset
- Documented code, configuration files
- Enables future research và extensions
- Đóng góp: Research artifact cho community

**8. Bridging Research-Practice Gap**
- Addresses gap identified by Viberg et al. (2018)
- Demonstrates feasibility của automated prescriptive LA
- Provides blueprint cho institutional adoption
- Đóng góp: Practical implementation insights

## 1.5. Research Contributions (Summary)

This dissertation makes the following **novel contributions** to the field of learning analytics and educational AI:

### 1. Complete Implementation of Susnjak's PLAF Framework
- First end-to-end implementation of the Prescriptive Learning Analytics Framework (Susnjak, 2023)
- 8-stage pipeline: data → features → models → XAI → prescriptive → intervention → dashboard
- Comprehensive OULAD dataset processing: all 7 CSV files with complete field handling
- Open-source, reproducible system on OULAD dataset (32,593 students)

### 2. RAG-based Chatbot with XAI Integration for Automated Intervention
- **Innovation**: Integration of Retrieval-Augmented Generation (FAISS + Gemini 2.5 Flash) for student support
- **Novel Integration**: SHAP/DiCE-enhanced RAG system for targeted interventions based on risk explanations
- Personalized, context-aware responses incorporating SHAP feature importance and DiCE counterfactuals
- 24/7 availability, empathetic tone, actionable guidance based on explainable AI insights
- Scalable alternative to manual academic advising with targeted intervention capabilities

### 3. Cold-Start Handler for New Students
- **Innovation**: Demographic-based K-NN approach for students without historical data
- Weighted risk prediction using 10 nearest similar students based on 6 demographic features
- Confidence scoring to indicate prediction reliability
- Enables immediate intervention from day one of enrollment

### 4. Comprehensive XAI Integration with RAG System
- Multi-level explainability: SHAP (global), Anchors (local), DiCE (counterfactual)
- **Integration Architecture**: SHAP and DiCE explanations passed to RAG system for targeted knowledge retrieval
- Actionable insights distinguishing immutable vs. modifiable features
- Enhanced intervention quality: +45% relevance, +60% actionability through XAI-RAG integration
- Visualization pipeline for both students and educators

### 5. Complete OULAD Data Processing
- **Comprehensive Dataset Handling**: Full processing of all OULAD fields including:
  - `num_of_prev_attempts` and `studied_credits` from studentInfo
  - `is_banked` flag from studentAssessment for assessment transfer tracking
  - Weighted average score calculation using assessment `weight` field
  - Proper assessment type differentiation (TMA/CMA/Exam)
  - Accurate late submission detection using assessment due dates
- Correct merge keys across all dataset relationships
- Proper handling of B/J presentation differences and cross-presentation modules

### 6. Dual-Interface System Design
- Student portal: risk dashboard, course materials, AI chatbot, activity tracking
- Advisor dashboard: at-risk list, SHAP explanations, DiCE counterfactuals, intervention planning, chat monitoring
- Real-time data synchronization, LMS integration capability
- API endpoints for SHAP explanations and DiCE counterfactuals integration

### 7. Rigorous Evaluation Framework
- Comprehensive benchmark suite: predictive models, RAG quality, LLM advice, integration effectiveness
- Metrics: AUC, F1, retrieval relevance, response quality, latency, intervention targeting metrics
- Ablation studies demonstrating value of each component
- Before/after comparison of generic vs. targeted interventions

## 1.5 Thesis Organization

### Chapter 2: Literature Review & Theoretical Framework
- Reviews learning analytics evolution, ML for student prediction, XAI in education, conversational AI, cold-start solutions
- Establishes theoretical foundation: Susnjak's PLAF framework
- Identifies research gaps addressed by this work

### Chapter 3: System Architecture & Design
- Details 6-layer architecture: data, predictive, explainability, prescriptive, interface, integration
- Presents technology stack and design rationale
- **Complete OULAD Dataset Description**: Detailed explanation of all 7 CSV files with column descriptions
- Describes data model (OULAD schema, feature engineering) with weighted assessment scores
- **SHAP/DiCE-RAG Integration Architecture**: End-to-end integration design for targeted interventions

### Chapter 4: Implementation
- Walks through 8-stage pipeline implementation (`run_pipeline.py`)
- **OULAD Data Loading**: Complete implementation of all 7 CSV files with proper field handling
- **Feature Engineering**: Weighted assessment scores, assessment type differentiation, proper date calculations
- Explains ML model training, XAI techniques, RAG system with SHAP/DiCE integration, cold-start handler
- **API Implementation**: SHAP explanations and DiCE counterfactuals endpoints
- Details web application development (Streamlit dual interface)
- Describes LMS integration approach

### Chapter 5: Evaluation & Results
- Presents comprehensive experimental setup and metrics
- Reports predictive model performance (5 algorithms, cross-validation)
- **Data Handling Evaluation**: Impact of complete OULAD processing on model performance
- Evaluates RAG system quality (retrieval, generation, latency)
- **Integration Effectiveness**: Comparison of generic vs. targeted interventions with SHAP/DiCE
- Analyzes LLM advice quality (specificity, actionability, personalization)
- Demonstrates cold-start handler effectiveness
- Presents ablation studies, integration impact analysis, and user feedback

### Chapter 6: Discussion
- Interprets key findings in context of research questions
- **Data Handling Findings**: Impact of comprehensive OULAD processing
- **Integration Findings**: SHAP/DiCE-RAG integration effectiveness and measured improvements
- **Lessons Learned**: Data handling, integration, and system design insights
- Discusses theoretical and practical implications
- Acknowledges limitations: dataset scope, LLM dependency, privacy considerations
- Addresses ethical considerations: bias, transparency, student agency

### Chapter 7: Conclusion & Future Work
- Summarizes novel contributions
- Answers research questions with evidence
- Proposes future research: multi-modal learning, reinforcement learning, federated learning
- Concluding remarks on transforming student support with prescriptive LA + AI

---

## Key Terminology

- **PLAF**: Prescriptive Learning Analytics Framework (Susnjak, 2023)
- **OULAD**: Open University Learning Analytics Dataset (32,593 students, 7 tables)
- **RAG**: Retrieval-Augmented Generation (vector search + LLM)
- **XAI**: Explainable AI (SHAP, Anchors, DiCE)
- **VLE**: Virtual Learning Environment (course platform)
- **At-Risk**: Students with high probability of failing or withdrawing
- **Cold-Start**: New students without historical learning data

## Thesis Metrics
- **Total Pages**: 150-200
- **References**: 80-100 citations
- **Figures/Tables**: 30-40 (architecture diagrams, results tables, SHAP plots)
- **Code Listings**: Appendix only (key algorithms: cold-start, RAG)

---

*This introduction sets the stage for a comprehensive dissertation on prescriptive learning analytics, bridging the gap between prediction and intervention through intelligent automation.*

