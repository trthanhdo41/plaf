# Chương 4: Phát biểu vấn đề nghiên cứu (Problem Statement)

## 4.1. Phân tích bài toán

### 4.1.1. Bối cảnh bài toán

**Vấn đề thực tế:**
Tỷ lệ sinh viên bỏ học đại học toàn cầu dao động 30-50%, gây thiệt hại lớn về tài chính và ảnh hưởng tiêu cực đến sự nghiệp sinh viên. Các hệ thống Learning Analytics hiện tại có thể dự đoán sinh viên có nguy cơ với độ chính xác cao, nhưng tồn tại **khoảng cách lớn giữa dự đoán và can thiệp**.

**Các thách thức chính:**

1. **Prediction-Intervention Gap:**
   - Hệ thống dự đoán được sinh viên at-risk nhưng không có cơ chế can thiệp tự động
   - Advisors không thể scale personalized support cho hàng nghìn sinh viên
   - Can thiệp thủ công mất nhiều thời gian (days/weeks), sinh viên cần hỗ trợ ngay lập tức

2. **Lack of Explainability:**
   - Dự đoán "black box" không giải thích được
   - Sinh viên và giảng viên không hiểu tại sao có nguy cơ
   - Không có hướng dẫn cụ thể để cải thiện

3. **Cold-Start Problem:**
   - Sinh viên mới không có dữ liệu lịch sử học tập
   - Không thể dự đoán nguy cơ trong tuần đầu
   - Bỏ lỡ cơ hội can thiệp sớm (critical window)

4. **Scalability Issues:**
   - Tư vấn thủ công không scale với số lượng sinh viên lớn
   - Advisor workload quá tải
   - Không thể hỗ trợ 24/7

5. **Generic Advice:**
   - Lời khuyên chung chung không hiệu quả
   - Thiếu cá nhân hóa theo bối cảnh từng sinh viên
   - Không dựa trên data-driven insights

### 4.1.2. Mục tiêu giải quyết

**Xây dựng hệ thống Prescriptive Learning Analytics end-to-end** để:

1. **Dự đoán chính xác** sinh viên có nguy cơ (AUC > 0.95)
2. **Giải thích rõ ràng** tại sao sinh viên có nguy cơ (SHAP, DiCE)
3. **Can thiệp tự động** qua AI chatbot 24/7
4. **Cá nhân hóa** lời khuyên dựa trên XAI insights
5. **Xử lý cold-start** cho sinh viên mới
6. **Scale** đến hàng nghìn sinh viên

---

## 4.2. Định nghĩa Đầu vào (Input)

### 4.2.1. Nguồn dữ liệu

**OULAD Dataset (Open University Learning Analytics Dataset)**
- **Quy mô**: 32,593 sinh viên unique
- **Thời gian**: Năm học 2013-2014
- **Modules**: 7 modules (AAA, BBB, CCC, DDD, EEE, FFF, GGG)
- **Presentations**: B (February start), J (October start)
- **Outcome**: Pass, Fail, Withdrawn, Distinction

### 4.2.2. Cấu trúc dữ liệu (7 CSV files)

**1. courses.csv (22 module-presentations)**
```
Columns:
- code_module: Module identifier (AAA, BBB, ...)
- code_presentation: Presentation code (2013B, 2013J, 2014B, 2014J)
- module_presentation_length: Duration in days
```

**2. assessments.csv (206 assessments)**
```
Columns:
- code_module, code_presentation: Module-presentation identifier
- id_assessment: Assessment ID
- assessment_type: TMA (Tutor Marked), CMA (Computer Marked), Exam
- date: Due date (days from module start)
- weight: Weight in final grade (%)
```

**3. vle.csv (6,364 VLE materials)**
```
Columns:
- id_site: Material ID
- code_module, code_presentation: Module-presentation
- activity_type: Resource, homepage, quiz, forum, etc.
- week_from, week_to: Planned usage weeks
```

**4. studentInfo.csv (32,593 students)**
```
Columns:
- code_module, code_presentation, id_student: Identifiers
- gender: M/F
- region: Geographic region (13 regions)
- highest_education: HE Qualification, A Level, Lower Than A Level, etc.
- imd_band: Index of Multiple Deprivation (0-10%, 10-20%, ..., 90-100%)
- age_band: 0-35, 35-55, 55<=
- num_of_prev_attempts: Number of previous attempts (0, 1, 2, ...)
- studied_credits: Total credits studying
- disability: Y/N
- final_result: Pass, Fail, Withdrawn, Distinction
```

**5. studentRegistration.csv (32,593 registrations)**
```
Columns:
- code_module, code_presentation, id_student
- date_registration: Days before/after module start (negative = early)
- date_unregistration: Unregistration date (null if completed)
```

**6. studentAssessment.csv (173,912 submissions)**
```
Columns:
- id_assessment, id_student
- date_submitted: Submission date (days from module start)
- is_banked: Assessment result transferred from previous presentation (0/1)
- score: Score 0-100
```

**7. studentVle.csv (10,655,280 interactions)**
```
Columns:
- code_module, code_presentation, id_student
- id_site: VLE material ID
- date: Interaction date (days from module start)
- sum_click: Number of clicks on that day
```

### 4.2.3. Feature Engineering

**Từ dữ liệu thô → 25 features:**

**Demographic Features (6 features - Immutable):**
1. `gender_encoded`: 0/1
2. `region_encoded`: 0-12
3. `highest_education_encoded`: 0-4
4. `imd_band_encoded`: 0-9
5. `age_band_encoded`: 0-2
6. `disability_encoded`: 0/1

**Assessment Features (8 features - Actionable):**
7. `avg_score_z`: Z-score của điểm trung bình
8. `score_std_z`: Z-score của độ lệch chuẩn điểm
9. `min_score_z`: Z-score của điểm thấp nhất
10. `max_score_z`: Z-score của điểm cao nhất
11. `submission_rate_z`: Z-score của tỷ lệ nộp bài
12. `submission_rate_mean`: Mean submission rate
13. `submission_rate_std`: Std submission rate
14. `num_late_submissions`: Số bài nộp trễ

**VLE Engagement Features (8 features - Actionable):**
15. `total_clicks_z`: Z-score của tổng clicks
16. `avg_clicks_per_day_z`: Z-score của clicks/day
17. `num_days_active_z`: Z-score của số ngày active
18. `num_unique_resources_z`: Z-score của số tài liệu unique
19. `clicks_per_active_day_z`: Z-score của clicks/active day
20. `resource_diversity_z`: Z-score của đa dạng tài liệu
21. `first_vle_access`: Ngày truy cập VLE đầu tiên
22. `early_engagement`: 1 if first access <= 7 days, else 0

**Registration Features (3 features):**
23. `num_unregistrations`: Số lần unregister
24. `has_unregistrations`: 1 if unregistered, else 0
25. `registered_early`: 1 if registered before start, else 0

**Derived Features:**
26. `study_intensity_z`: (score_norm + clicks_norm) / 2

**Z-score Standardization:**
```python
# By cohort (code_module + code_presentation)
z = (x - μ_cohort) / σ_cohort
```

### 4.2.4. Input cho các components

**1. ML Model Input:**
```python
X = [25 features] # All features
y = is_at_risk    # 0 = Safe, 1 = At-Risk
```

**2. SHAP Explainer Input:**
```python
model = trained_CatBoost_model
X_background = sample(modeling_data, 100)  # Background for SHAP
X_student = student_features  # Single student
```

**3. DiCE Input:**
```python
query_instance = student_features
desired_class = 0  # Safe
features_to_vary = actionable_features  # 19 features
immutable_features = demographic_features  # 6 features
```

**4. RAG Chatbot Input:**
```python
query = student_question  # Text
student_context = {
    'id_student': int,
    'name': str,
    'risk_probability': float,
    'avg_score': float,
    'total_clicks': int,
    'shap_explanation': dict,  # Top risk factors
    'dice_counterfactuals': dict  # Recommendations
}
```

**5. Cold-Start Handler Input:**
```python
# For new students without historical data
demographic_features = [
    'gender_encoded',
    'region_encoded', 
    'highest_education_encoded',
    'imd_band_encoded',
    'age_band_encoded',
    'disability_encoded'
]
```

---

## 4.3. Định nghĩa Đầu ra (Output)

### 4.3.1. Predictive Model Output

**Binary Classification:**
```python
prediction = 0 or 1  # 0 = Safe, 1 = At-Risk
risk_probability = float [0, 1]  # Probability of being at-risk
```

**Threshold:**
- Default: 0.5
- Tuned: 0.3 (để minimize False Negatives)

**Example:**
```json
{
  "id_student": 100064,
  "prediction": 0,
  "risk_probability": 0.09,
  "risk_level": "Low"
}
```

### 4.3.2. SHAP Explanation Output

**Global Feature Importance:**
```json
{
  "top_features": [
    {"feature": "submission_rate_z", "importance": 15.30},
    {"feature": "has_unregistrations", "importance": 9.28},
    {"feature": "avg_score_z", "importance": 7.72}
  ]
}
```

**Local Explanation (per student):**
```json
{
  "id_student": 25572,
  "risk_probability": 1.00,
  "top_factors": [
    {
      "feature": "submission_rate_z",
      "feature_name": "Assignment Submission Rate",
      "value": -2.65,
      "shap_value": 2.81,
      "impact_direction": "increases_risk",
      "explanation": "Missed assignments are significantly increasing risk.",
      "recommendation": "Ensure all future assignments are submitted on time.",
      "impact_percentage": 35.2
    },
    {
      "feature": "has_unregistrations",
      "value": 1,
      "shap_value": 1.92,
      "impact_direction": "increases_risk",
      "impact_percentage": 24.1
    }
  ],
  "interpretation": "Student has 100.0% risk probability. HIGH RISK: Critical issues detected."
}
```

### 4.3.3. DiCE Counterfactual Output

**Counterfactual Scenarios:**
```json
{
  "id_student": 25572,
  "current_risk": 1.00,
  "target_risk": 0.30,
  "recommendations": [
    "Increase Average Assessment Score by 1.10 standard deviations",
    "Increase Min Score by 1.05 standard deviations",
    "Increase Days Active on Platform by 8.81 standard deviations",
    "Adjust Assignment Submission Rate by 2.15 units"
  ],
  "required_changes": {
    "avg_score_z": {
      "current": -1.50,
      "target": -0.40,
      "change_needed": 1.10,
      "feature_name": "Average Assessment Score"
    },
    "submission_rate_z": {
      "current": -2.65,
      "target": -0.50,
      "change_needed": 2.15
    }
  },
  "feasibility": "verified",
  "explanation_type": "real_dice"
}
```

### 4.3.4. RAG Chatbot Output

**Response Format:**
```json
{
  "query": "I'm struggling with my assignments. What should I do?",
  "response": "I understand you're facing challenges with assignments. Based on your data, I see that your submission rate is significantly below average, which is the #1 factor increasing your risk. Here are specific steps:\n\n1. **Immediate Action**: Set calendar reminders 3 days before each deadline.\n2. **Start Early**: Begin assignments within 24 hours of release to identify difficulties early.\n3. **Seek Help**: If stuck, attend office hours or join study groups.\n4. **Target**: Aim to submit all remaining assignments on time to reduce your risk by 40-50%.\n\nYou can do this! Small consistent improvements make a big difference.",
  "context_used": [
    "Low submission rate students have 99.9% risk...",
    "Evidence shows that improving submission rate reduces risk by 40-50%..."
  ],
  "has_explainability": true,
  "response_time_ms": 1850
}
```

### 4.3.5. Cold-Start Prediction Output

**For new students:**
```json
{
  "id_student": 999999,
  "prediction_type": "cold_start",
  "risk_probability": 0.65,
  "confidence_score": 0.72,
  "nearest_neighbors": [
    {"id": 12345, "distance": 0.15, "outcome": "Fail"},
    {"id": 67890, "distance": 0.18, "outcome": "Fail"},
    {"id": 23456, "distance": 0.22, "outcome": "Pass"}
  ],
  "explanation": "Based on 10 similar students (same demographics), 7 failed and 3 passed. Estimated risk: 65%.",
  "confidence_interpretation": "Moderate confidence (0.72). Prediction will improve as learning data accumulates."
}
```

### 4.3.6. Dashboard Visualizations

**Student Portal:**
- Risk gauge (0-100%)
- SHAP waterfall plot
- DiCE recommendations cards
- Progress tracking charts

**Advisor Dashboard:**
- At-risk student list (sortable by risk)
- SHAP summary plot (global importance)
- DiCE intervention planning
- Chat history monitoring

---

## 4.4. Ràng buộc và Yêu cầu

### 4.4.1. Functional Requirements

**FR1: Prediction Accuracy**
- AUC-ROC ≥ 0.95
- Recall (At-Risk) ≥ 90% (minimize False Negatives)
- Precision (At-Risk) ≥ 85%

**FR2: Explainability**
- SHAP values for all predictions
- DiCE counterfactuals for at-risk students
- Human-readable explanations

**FR3: Chatbot Response Quality**
- Latency < 2 seconds
- Personalized to student context
- Grounded in knowledge base (no hallucination)
- Empathetic tone

**FR4: Cold-Start Handling**
- Prediction available from day 1
- Confidence scoring
- Graceful degradation (lower confidence)

**FR5: Scalability**
- Support 10,000+ students
- Concurrent chatbot sessions: 100+
- Dashboard load time < 3 seconds

### 4.4.2. Non-Functional Requirements

**NFR1: Privacy**
- GDPR/FERPA compliant
- Student data encryption
- Access control (role-based)

**NFR2: Transparency**
- Explainable predictions
- Audit trail for interventions
- Source attribution for chatbot responses

**NFR3: Usability**
- Intuitive UI for students and advisors
- Mobile-responsive
- Accessibility (WCAG 2.1 Level AA)

**NFR4: Reliability**
- 99% uptime
- Graceful error handling
- Fallback mechanisms (e.g., rule-based if ML fails)

### 4.4.3. Technical Constraints

**Data Constraints:**
- OULAD dataset only (no real-time LMS integration for this thesis)
- Historical data (2013-2014)
- Static dataset (no streaming updates)

**Model Constraints:**
- Interpretable models preferred (CatBoost, RF, XGBoost)
- No deep learning (due to black-box nature)

**Infrastructure Constraints:**
- CPU-only (no GPU required)
- Local deployment (no cloud dependency for core functions)
- Gemini API for LLM (external dependency)

---

## 4.5. Success Criteria

### 4.5.1. Predictive Performance
- ✅ AUC-ROC ≥ 0.95
- ✅ Recall ≥ 90%
- ✅ False Negative Rate ≤ 10%

### 4.5.2. Explainability Quality
- ✅ SHAP values computed for 100% predictions
- ✅ DiCE counterfactuals for 100% at-risk students
- ✅ Explanations understandable by non-technical users

### 4.5.3. Intervention Effectiveness
- ✅ Chatbot response latency < 2s
- ✅ Response relevance ≥ 80% (human evaluation)
- ✅ Actionability score ≥ 4/5 (human evaluation)

### 4.5.4. System Integration
- ✅ End-to-end pipeline functional
- ✅ All 8 PLAF stages implemented
- ✅ Dual-interface (student + advisor) operational

---

**Tóm tắt Chương 4:**

Chương này đã định nghĩa rõ ràng bài toán nghiên cứu:

**Input:**
- OULAD dataset: 7 CSV files, 32,593 students
- 25 engineered features (6 demographic + 19 actionable)
- Z-score standardization by cohort

**Output:**
- Risk prediction: Binary + probability
- SHAP explanations: Global + local
- DiCE counterfactuals: Actionable recommendations
- RAG chatbot: Personalized responses
- Cold-start predictions: Demographic-based

**Success Criteria:**
- AUC ≥ 0.95, Recall ≥ 90%
- Latency < 2s
- Explainability for 100% predictions

Chương tiếp theo sẽ trình bày giải pháp đề xuất để giải quyết bài toán này.
