# Prescriptive Learning Analytics Framework (PLAF)

## Tổng quan dự án

Dự án này implement framework phân tích học tập dựa trên paper của Teo Susnjak (arXiv:2208.14582). Mục tiêu chính:

- Dự đoán sinh viên có nguy cơ drop out hoặc fail
- Giải thích WHY model predict như vậy (dùng XAI techniques)
- Tự động generate lời khuyên cụ thể để sinh viên cải thiện

### So với các hệ thống prediction thông thường

Hầu hết các project chỉ làm prediction rồi dừng lại. Project này đi xa hơn:
- Dùng SHAP và Anchors để explain predictions (transparency)
- Dùng DiCE để tạo counterfactual scenarios (what-if analysis)
- Dùng Gemini API để convert technical findings thành natural language advice

## Dataset

Dùng OULAD (Open University Learning Analytics Dataset) từ Kaggle. Dataset này khá lớn, có 7 tables:

**Core tables:**
- `studentInfo.csv` (3.3MB) - demographics + target variable `final_result` (Pass/Fail/Withdrawn/Distinction)
- `studentAssessment.csv` (5.4MB) - điểm các bài assignment
- `studentVle.csv` (433MB!) - log tương tác của SV với learning platform (clicks, views, etc)

**Supporting tables:**
- `assessments.csv` - metadata về assignments (type, weight, due date)
- `studentRegistration.csv` - registration/unregistration dates
- `vle.csv` - VLE resources info
- `courses.csv` - course metadata

Target là predict `final_result`. Specifically, mình sẽ tạo binary variable:
- `is_at_risk = 1` nếu Fail hoặc Withdrawn
- `is_at_risk = 0` nếu Pass hoặc Distinction

## Pipeline Overview

Framework chia thành 4 modules chính, follow paper architecture:

### Module 1: Data Pipeline (Step 1)

**Input:** 7 CSV files từ OULAD dataset
**Output:** Clean, merged dataframe với engineered features

To-do list:
- Load all tables và join chúng lại (dùng student_id + course_id làm keys)
- Handle missing data (zero-fill cho numeric, mode/median cho categorical - tùy case)
- Encode categorical variables (gender, region, education level, etc.)
- Create target variable `is_at_risk` từ `final_result`

Feature engineering cơ bản:
- Academic performance metrics: avg score, số assignments submitted, số papers failed
- VLE engagement: total clicks, activity diversity (bao nhiêu loại resources đã access)
- Temporal features: days between registration và course start, early vs late submission patterns
- Demographics từ studentInfo

### Module 2: Predictive Modeling (Steps 2-5)

#### Step 2: Z-score standardization

Một trick quan trọng trong paper là normalize features bằng z-scores **theo cohort**:
```python
z_score = (student_value - cohort_mean) / cohort_std
```

Tại sao? Vì mỗi course/semester có difficulty và grading khác nhau. Z-score giúp so sánh "relative performance" thay vì absolute values. Ví dụ: 70% ở course dễ khác xa 70% ở course khó.

Apply cho: avg_score, vle_clicks, submission_rate, etc.

#### Step 3: Train và benchmark models

Cần train nhiều models để compare (follow best practices):
- Random Forest
- CatBoost (thường perform best với tabular data)
- XGBoost
- Logistic Regression (baseline)
- SVM

Setup:
- 5-fold cross-validation với stratified split (vì data imbalanced)
- Track metrics: F1 (primary), Accuracy, Precision, Recall, AUC
- Save best model

Lưu ý: Dataset này thường imbalanced (nhiều Pass hơn Fail), nên F1-score quan trọng hơn accuracy.

#### Step 4 & 5: Explainability (XAI)

Đây là phần hay của paper - không chỉ predict mà còn explain.

**Global explainability (Step 4):**
Dùng SHAP để hiểu model behavior ở level tổng thể:
- SHAP summary plot: features nào quan trọng nhất?
- SHAP dependence plots: relationship giữa feature values và predictions
- Giúp build trust với stakeholders (advisors, admins)

**Local explainability (Step 5):**
For each at-risk student, generate 2 types of explanations:

1. **SHAP force plots** - visual breakdown
   - Show which features push prediction toward "at-risk" (red) vs "safe" (blue)
   - Quantitative, chi tiết

2. **Anchor rules** - human-readable conditions
   - Example: "Student at-risk BECAUSE papers_failed > 1 AND avg_score < 60"
   - Easier cho non-technical advisors hiểu

Library: `shap`, `anchor-exp`

### Module 3: Prescriptive Analytics (Steps 6-7)

Đây là core innovation của paper - từ "why at-risk" sang "what to do".

#### Step 6: Counterfactual generation với DiCE

Idea: tìm minimum changes trong student behavior để flip prediction từ at-risk → safe.

DiCE generates "what-if" scenarios:
- "What if student increases VLE clicks by 50%?"
- "What if they improve avg score from 52% to 65%?"

Important: phân biệt actionable vs immutable features
- Can change: scores, vle_clicks, submission behavior
- Cannot change: age, gender, prior education

Set feasibility constraints (không realistic nếu suggest tăng score từ 40% lên 95% instantly):
```python
# Example constraints
avg_score: current → min(current * 1.3, 90)  # max 30% increase
vle_clicks: current → current * 2  # max double
papers_failed: 0 → current  # can only reduce
```

Output sẽ là counterfactual examples in z-score format.

#### Step 7: Convert to natural language advice

2-part process:

**Part 1: Convert z-scores back to raw values**
DiCE outputs are in z-score format (e.g., avg_score_z = 0.3). Need to convert back:
```python
raw_value = z_score * cohort_std + cohort_mean
```
Now we have interpretable numbers like "increase avg score from 52% to 68%".

**Part 2: Generate natural language với LLM**
Dùng Gemini API (hoặc ChatGPT) để convert numerical recommendations thành readable advice.

Prompt engineering approach:
- System role: academic advisor
- Input: current state + recommended changes (JSON format)
- Output format: summary + bullet points + expected outcome
- Tone: supportive but concrete

Example flow:
```
Current: avg_score=52%, vle_clicks=45/week, papers_failed=2
Target: avg_score=68%, vle_clicks=95/week, papers_failed=0

→ LLM generates:
"Based on your performance, here's what would help:
- Improve your average from 52% to 68% by attending office hours...
- Increase platform engagement to ~95 interactions per week...
- Focus on completing all assignments to avoid failures..."
```

### Module 4: Dashboard (Step 8)

Build interactive interface cho advisors/administrators. Plan to use Streamlit (simple, quick to build).

**Key pages:**

1. **Overview page**
   - Summary stats: how many students at-risk, distribution by risk level
   - Model performance metrics

2. **Student list**
   - Table với search/filter capabilities
   - Sort by risk level, course, demographics
   - Click vào student để see details

3. **Individual student view** (main page)
   - Risk score với gauge visualization
   - SHAP force plot (why at-risk?)
   - Anchor rules (simple if-then explanation)
   - Generated advice options (3-5 suggestions từ LLM)
   
4. **Intervention tracking**
   - Log when advisor contacts student
   - Record which advice was given
   - Follow-up reminders

Tech stack: Streamlit (frontend) + Plotly (charts) + saved models (backend)

## Tech stack

Main libraries cần install (xem file requirements.txt):
- pandas, numpy, scikit-learn (standard ML stack)
- catboost, xgboost (tree-based models)
- shap (explainability)
- anchor-exp (rule-based explanations)
- dice-ml (counterfactual generation)
- google-generativeai (Gemini API access)
- streamlit (dashboard)
- plotly, matplotlib (visualization)

Setup:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Cần tạo file `.env` với Gemini API key (get from Google AI Studio)

## Project structure

```
PLAF/
├── OULAD dataset/          # Raw data từ Kaggle (7 CSV files)
├── data/
│   ├── processed/          # Cleaned data after preprocessing
│   └── features/           # Feature-engineered data
├── notebooks/              # Jupyter notebooks cho experimentation
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   └── ...
├── src/                    # Source code modules
│   ├── data/              # Data pipeline
│   ├── models/            # Model training & evaluation
│   ├── explainability/    # XAI components (SHAP, Anchors)
│   ├── prescriptive/      # DiCE, LLM integration
│   └── dashboard/         # Streamlit app
├── models/                # Saved trained models
├── config/                # Configuration files
├── requirements.txt
└── README.md
```

Xem `PROJECT_STRUCTURE.md` để biết chi tiết từng file.

## TODO Progress (7 of 39 completed)

### Completed Tasks
- [x] Setup project structure: tạo folders (data/, src/, notebooks/, models/, config/)
- [x] Tạo requirements.txt với tất cả dependencies cần thiết
- [x] Create comprehensive documentation (usage guide, API docs)
- [x] Tạo __init__.py files cho tất cả src/ modules
- [x] Tạo setup test notebook để verify environment
- [x] Tạo starter template cho data loader
- [x] Tạo data exploration notebook template

### In Progress
- [ ] Module 1 - Step 1: Load OULAD dataset (7 CSV files) và explore cấu trúc dữ liệu

### Pending Tasks
- [ ] Module 1 - Step 1: Data cleaning (handle missing values, detect outliers)
- [ ] Module 1 - Step 1: Merge tables (studentInfo + assessments + VLE + registration)
- [ ] Module 1 - Step 1: Create target variable is_at_risk (binary: Fail/Withdrawn=1, Pass/Distinction=0)
- [ ] Module 2 - Step 2: Feature Engineering - tạo academic features (avg_score, papers_failed, submission_rate)
- [ ] Module 2 - Step 2: Feature Engineering - tạo VLE engagement features (total_clicks, activity_diversity)
- [ ] Module 2 - Step 2: Z-score standardization cho tất cả numeric features theo cohort
- [ ] Module 2 - Step 2: Encode categorical features (Binary/One-Hot Encoding)
- [ ] Module 2 - Step 3: Train/test split với stratified sampling
- [ ] Module 2 - Step 3: Train Random Forest với k-fold cross-validation
- [ ] Module 2 - Step 3: Train CatBoost với k-fold cross-validation
- [ ] Module 2 - Step 3: Train XGBoost với k-fold cross-validation
- [ ] Module 2 - Step 3: Train Logistic Regression với k-fold cross-validation
- [ ] Module 2 - Step 3: Train SVM với k-fold cross-validation
- [ ] Module 2 - Step 3: Benchmark comparison - tạo bảng so sánh F1, Accuracy, Precision, Recall, AUC cho tất cả models
- [ ] Module 2 - Step 3: Select best model và save (pickle/joblib)
- [ ] Module 2 - Step 4: Setup SHAP explainer cho best model
- [ ] Module 2 - Step 4: Generate SHAP Summary Plot (global feature importance)
- [ ] Module 2 - Step 4: Generate SHAP Dependence Plots cho top features
- [ ] Module 2 - Step 5: Generate SHAP Force Plots cho individual at-risk students
- [ ] Module 2 - Step 5: Setup Anchors explainer và generate rule-based explanations
- [ ] Module 3 - Step 6: Setup DiCE counterfactual explainer
- [ ] Module 3 - Step 6: Define actionable vs immutable features
- [ ] Module 3 - Step 6: Set constraints cho feasible ranges của actionable features
- [ ] Module 3 - Step 6: Generate counterfactuals cho at-risk students
- [ ] Module 3 - Step 7: Convert z-scores về raw values (interpretable format)
- [ ] Module 3 - Step 7: Setup Gemini 2.5 Flash API connection
- [ ] Module 3 - Step 7: Design prompt template cho NLG (system, task, student data, output format)
- [ ] Module 3 - Step 7: Test LLM generation với sample students và refine prompts
- [ ] Module 3 - Step 7: Generate remedial advice cho tất cả at-risk students
- [ ] Module 4 - Step 8: Setup Streamlit/Gradio dashboard structure
- [ ] Module 4 - Step 8: Create Overview page (statistics, risk distribution)
- [ ] Module 4 - Step 8: Create Student List page (searchable table với filters)
- [ ] Module 4 - Step 8: Create Individual Student Detail page (risk score, SHAP plots, Anchor rules, LLM advice)
- [ ] Module 4 - Step 8: Create Intervention Logging page (advisor notes, follow-up)
- [ ] Prepare presentation slides/report summarizing methodology và results

## Important notes

**Ethical concerns:**
- Model bias: check if predictions are biased by demographics (gender, age, region)
- Privacy: anonymize student IDs trong reports
- Transparency: students có quyền biết tại sao bị flagged as at-risk

**Technical limitations:**
- Data imbalance: OULAD has way more Pass than Fail/Withdrawn → need proper metrics (F1 > accuracy)
- Temporal aspect: model predicts at one snapshot, cần retrain periodically as semester progresses
- Feasibility: không phải mọi suggested change đều realistic (e.g., can't magically improve score 50% overnight)

**LLM considerations:**
- API costs: Gemini có free tier nhưng limited requests/day
- Consistency: prompt engineering matter - test thoroughly để output không bị random
- Validation: advisors should review LLM-generated advice before sending to students (hallucination risk)

## References

Main paper:
- Susnjak, T. (2023). "A Prescriptive Learning Analytics Framework: Beyond Predictive Modelling and onto Explainable AI with Prescriptive Analytics and ChatGPT". arXiv:2208.14582
- Link: https://arxiv.org/abs/2208.14582v2

Dataset:
- OULAD: https://www.kaggle.com/datasets/anlgrbz/student-demographics-online-education-dataoulad

Key libraries documentation:
- SHAP: https://shap.readthedocs.io/
- DiCE: https://interpret.ml/DiCE/
- Gemini API: https://ai.google.dev/

---

Last updated: October 2025

