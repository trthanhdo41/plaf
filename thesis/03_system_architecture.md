# Chapter 3: System Architecture & Design

## 3.1 Overall System Architecture

### 3.1.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLMS ARCHITECTURE (8-Stage Pipeline)         │
└─────────────────────────────────────────────────────────────────┘

[Stage 1-2: Data Layer]
    OULAD Dataset (32,593 students)
           ↓
    Data Ingestion & Preprocessing
    (studentInfo, studentAssessment, studentVle, vle, courses)
           ↓
    SQLite Database + Merged Dataset

[Stage 3: Feature Engineering]
    25 Features with Z-Score Standardization
    - Demographics (6 immutable)
    - VLE Behavior (10 actionable)
    - Assessment Performance (9 actionable)

[Stage 4: Predictive Layer]
    5 ML Models (5-Fold CV)
    ├── CatBoost (Best Model)
    ├── Random Forest
    ├── XGBoost
    ├── SVM
    └── Logistic Regression
           ↓
    Risk Predictions + Probabilities

[Stage 5: Explainability Layer (XAI)]
    ├── SHAP (Global & Local Importance)
    ├── Anchor (Rule-Based Explanations)
    └── DiCE (Counterfactual "What-Ifs")

[Stage 6: Prescriptive Layer]
    ├── LLM Advisor (Gemini 2.5 Flash)
    └── RAG Chatbot (FAISS + Gemini)
           ↓
    Personalized Interventions

[Stage 7-8: Interface & Intervention]
    ├── Student Portal (Streamlit)
    │   - Dashboard, Risk Level, Chatbot
    ├── Advisor Dashboard (Streamlit)
    │   - At-Risk List, SHAP Plots, Interventions
    └── LMS Integration (SSO, Data Sync)

[Auxiliary: Cold-Start Handler]
    K-NN on Demographics → Immediate predictions for new students
```

### 3.1.2 Technology Stack

**Configuration Reference**: `config/config.yaml`

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Data Storage** | SQLite | Lightweight, embedded, no server setup |
| **Data Processing** | Pandas, NumPy | Standard Python data science stack |
| **ML Models** | CatBoost, RF, XGBoost, SVM, LR | Diverse algorithms, ensemble strength |
| **XAI** | SHAP, Anchors, DiCE | Multi-level explanations (global/local/counterfactual) |
| **Vector Store** | FAISS (CPU) | Fast similarity search, no external dependencies |
| **LLM** | Google Gemini 2.5 Flash | Cost-effective, fast inference, good quality |
| **Web Framework** | Streamlit | Rapid prototyping, Python-native, reactive UI |
| **Orchestration** | Python Scripts | Simple pipeline execution, no complex DAGs needed |

### 3.1.3 Design Principles

1. **Modularity**: Each stage is independent, can be swapped/upgraded
2. **Reproducibility**: Fixed random seeds (42), version-pinned dependencies
3. **Scalability**: Batch processing, async chatbot, vectorized operations
4. **Interpretability**: XAI at every decision point, transparent to users
5. **Robustness**: Graceful degradation (e.g., fallback if Gemini API fails)
6. **Privacy**: Role-based access, encryption, audit logs (GDPR/FERPA ready)

## 3.2 Data Layer

### 3.2.1 OULAD Dataset Structure

**Open University Learning Analytics Dataset** (Kuzilek et al., 2017)
- **Students**: 32,593 unique learners
- **Courses**: 7 modules (AAA-GGG) × multiple presentations
- **Time Period**: 2013-2014
- **Outcome**: Pass/Fail/Withdrawn/Distinction

**Seven Data Tables**:

1. **studentInfo.csv** (32,593 rows)
   - Demographics: gender, region, age_band, highest_education, IMD_band, disability
   - Course enrollment: code_module, code_presentation
   - Outcome: final_result (Pass/Fail/Withdrawn/Distinction)

2. **studentAssessment.csv** (173,912 rows)
   - Student assessment submissions
   - Scores, submission dates

3. **assessments.csv** (206 rows)
   - Assessment metadata: type (TMA/CMA/Exam), weight, due date

4. **studentVle.csv** (10,655,280 rows)
   - Virtual Learning Environment interactions
   - Activity type, date, number of clicks

5. **vle.csv** (6,364 rows)
   - VLE content metadata: activity types, modules

6. **studentRegistration.csv** (32,593 rows)
   - Registration dates, unregistration dates

7. **courses.csv** (22 rows)
   - Course metadata: module codes, presentation dates

### 3.2.2 Database Schema

**Implementation**: `src/database/models.py`

**Entity-Relationship Design**:

```sql
-- Students Table
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    code_module TEXT,
    code_presentation TEXT,
    gender TEXT,
    region TEXT,
    highest_education TEXT,
    imd_band TEXT,
    age_band TEXT,
    disability TEXT,
    num_of_prev_attempts INTEGER,
    final_result TEXT,
    risk_probability REAL,
    is_at_risk BOOLEAN
);

-- Activities Table (VLE tracking)
CREATE TABLE activities (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    material_id INTEGER,
    activity_type TEXT,
    timestamp DATETIME,
    duration INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- Assessments Table
CREATE TABLE assessments (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    assessment_type TEXT,
    score REAL,
    submission_date DATE,
    is_late BOOLEAN,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- Chat History Table
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    message TEXT,
    response TEXT,
    timestamp DATETIME,
    context_used TEXT,  -- JSON of RAG context
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- Interventions Table
CREATE TABLE interventions (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    advisor_id INTEGER,
    intervention_type TEXT,
    description TEXT,
    created_at DATETIME,
    status TEXT,  -- Pending/Completed/Declined
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- Course Materials Table
CREATE TABLE course_materials (
    id INTEGER PRIMARY KEY,
    code_module TEXT,
    title TEXT,
    content TEXT,
    material_type TEXT,  -- Video/Reading/Quiz/Forum
    week_number INTEGER
);
```

### 3.2.3 Feature Engineering Pipeline

**Implementation**: `src/data/feature_engineering.py`

**25 Engineered Features**:

**Demographic Features (6, Immutable)**:
1. `gender` (encoded: M/F)
2. `region` (encoded: 13 UK regions)
3. `highest_education` (encoded: No Formal/Lower Than A/A Level/HE/Post Graduate)
4. `imd_band` (socioeconomic, encoded: 0-10% to 90-100%)
5. `age_band` (encoded: 0-35, 35-55, 55+)
6. `disability` (encoded: Y/N)

**VLE Behavioral Features (10, Actionable)**:
7. `total_vle_clicks_z` (z-scored total interactions)
8. `vle_activity_diversity_z` (z-scored unique activity types)
9. `avg_daily_vle_clicks_z` (z-scored daily average)
10. `days_active_vle_z` (z-scored unique days with activity)
11. `vle_early_engagement_z` (z-scored clicks in first 2 weeks)
12. `vle_mid_engagement_z` (z-scored clicks in weeks 3-6)
13. `vle_late_engagement_z` (z-scored clicks after week 6)
14. `vle_trend_z` (z-scored engagement slope over time)
15. `weekend_vle_ratio_z` (z-scored weekend vs weekday clicks)
16. `evening_vle_ratio_z` (z-scored evening vs daytime clicks)

**Assessment Features (9, Actionable)**:
17. `avg_assessment_score_z` (z-scored mean score)
18. `num_assessments_submitted_z` (z-scored count)
19. `assessment_completion_rate_z` (z-scored % submitted)
20. `early_submission_rate_z` (z-scored % submitted before deadline)
21. `late_submission_rate_z` (z-scored % submitted after deadline)
22. `papers_failed_z` (z-scored count of failures)
23. `score_improvement_trend_z` (z-scored score trajectory)
24. `TMA_score_z` (z-scored tutor-marked assessments)
25. `CMA_score_z` (z-scored computer-marked assessments)

**Z-Score Standardization**:
```python
z_score = (value - mean) / std_dev
```
- Mean = 0, Std = 1 across training set
- Handles outliers, makes features comparable
- Applied to 19 continuous features

**Target Variable**:
```python
is_at_risk = 1 if final_result in ['Fail', 'Withdrawn'] else 0
```

## 3.3 Predictive Layer

### 3.3.1 Model Selection Rationale

**Why 5 Models?**
- **Ensemble Diversity**: Different algorithms capture different patterns
- **Benchmark Comparison**: Identify best performer empirically
- **Robustness**: Avoid overfitting to single algorithm's biases

**Model Specifications** (`src/models/train.py`):

1. **CatBoost** (Primary Model)
   ```python
   CatBoostClassifier(
       iterations=500,
       learning_rate=0.1,
       depth=6,
       auto_class_weights='Balanced',  # Handle imbalance
       random_state=42,
       verbose=False
   )
   ```
   - **Why**: Excellent categorical feature handling, built-in class weights, robust
   - **Expected**: Best AUC (~0.98) based on OULAD benchmarks

2. **Random Forest**
   ```python
   RandomForestClassifier(
       n_estimators=100,
       max_depth=10,
       class_weight='balanced',
       random_state=42,
       n_jobs=-1
   )
   ```
   - **Why**: Robust ensemble, interpretable feature importance, low overfitting

3. **XGBoost**
   ```python
   XGBClassifier(
       n_estimators=100,
       max_depth=6,
       learning_rate=0.1,
       scale_pos_weight=ratio,  # Imbalance handling
       eval_metric='logloss',
       random_state=42
   )
   ```
   - **Why**: State-of-the-art gradient boosting, fast inference

4. **SVM (RBF Kernel)**
   ```python
   SVC(
       kernel='rbf',
       C=1.0,
       class_weight='balanced',
       probability=True,  # For AUC computation
       random_state=42
   )
   ```
   - **Why**: Effective for non-linear boundaries, theoretical guarantees

5. **Logistic Regression**
   ```python
   LogisticRegression(
       max_iter=1000,
       class_weight='balanced',
       random_state=42
   )
   ```
   - **Why**: Baseline, highly interpretable, fast

### 3.3.2 Training Strategy

**Stratified K-Fold Cross-Validation** (k=5):
```python
StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
```
- Ensures balanced class distribution in each fold
- Reduces variance in performance estimates
- 80% train, 20% test within each fold

**Class Imbalance Handling**:
- At-risk students: ~30% (minority class)
- Safe students: ~70% (majority class)
- Solutions:
  - `class_weight='balanced'` in all models
  - SMOTE (Synthetic Minority Over-sampling) if needed
  - Evaluation focus on F1-score (balances precision/recall)

**Hyperparameter Tuning**:
- Method: RandomizedSearchCV (50 iterations, `config.yaml`)
- Search space example (CatBoost):
  - `iterations`: [100, 300, 500, 1000]
  - `learning_rate`: [0.01, 0.05, 0.1, 0.2]
  - `depth`: [4, 6, 8, 10]
- Metric for selection: F1-score (`config.yaml: primary_metric`)

**Model Persistence**:
```python
joblib.dump({'model': best_model, 'model_name': 'CatBoost', ...}, 
            'models/best_model.pkl')
```

### 3.3.3 Cold-Start Handler

**Implementation**: `src/models/cold_start_handler.py`

**Problem**: New students have no VLE/assessment history → 19 features missing

**Solution**: K-Nearest Neighbors on 6 Demographic Features

**Algorithm**:
```python
class ColdStartHandler:
    def __init__(self, historical_data):
        # Encode demographics: gender, region, education, IMD, age, disability
        self.label_encoders = {feature: LabelEncoder() for feature in demographics}
        self.feature_matrix = encode_demographics(historical_data)
        self.knn_model = NearestNeighbors(n_neighbors=10, metric='euclidean')
        self.knn_model.fit(self.feature_matrix)
    
    def predict_new_student(self, student_demographics, k=10):
        # 1. Encode input demographics
        encoded_input = encode(student_demographics)
        
        # 2. Find k nearest historical students
        distances, indices = self.knn_model.kneighbors([encoded_input], n_neighbors=k)
        
        # 3. Weighted prediction (inverse distance weighting)
        neighbors = historical_data.iloc[indices[0]]
        weights = 1 / (distances[0] + 1e-6)  # Avoid division by zero
        risk_prob = np.average(neighbors['risk_probability'], weights=weights)
        
        # 4. Confidence score (inverse of avg distance)
        confidence = 1 / (np.mean(distances[0]) + 1)
        
        return {
            'risk_probability': risk_prob,
            'confidence': confidence,
            'method': 'cold_start_knn',
            'n_neighbors': k
        }
```

**Evaluation Metrics**:
- MAE (Mean Absolute Error): Average prediction error
- RMSE (Root Mean Squared Error): Penalizes large errors
- Accuracy: Binary classification (>0.5 threshold)
- Confidence analysis: Correlation with prediction error

### 3.3.4 Few-Shot Learning (Advanced)

**Implementation**: `src/models/few_shot_learner.py`

**Use Case**: Adapting to new courses/cohorts with minimal data

**Prototypical Networks** (Snell et al., 2017):
```python
class ProtoNet:
    def compute_prototypes(self, support_set, labels):
        # Average embedding per class
        prototypes = {}
        for class_label in np.unique(labels):
            class_samples = support_set[labels == class_label]
            prototypes[class_label] = np.mean(class_samples, axis=0)
        return prototypes
    
    def predict(self, query_set, prototypes):
        # Classify based on nearest prototype
        distances = {cls: euclidean(query, proto) 
                    for cls, proto in prototypes.items()}
        return min(distances, key=distances.get)
```

**Training**: 5-10 examples per class (at-risk vs safe) from new cohort

**Not used in main pipeline** (OULAD has sufficient data), but ready for deployment to new institutions

## 3.4 Explainability Layer

### 3.4.1 SHAP (Global & Local Explanations)

**Implementation**: `src/explainability/shap_explainer.py`

**TreeExplainer for Ensemble Models**:
```python
import shap

explainer = shap.TreeExplainer(catboost_model)
shap_values = explainer.shap_values(X_sample)

# Global importance
shap.summary_plot(shap_values, X_sample, plot_type="bar")

# Local explanation (single student)
shap.force_plot(explainer.expected_value, shap_values[i], X_sample.iloc[i])
```

**Interpretation**:
- **Positive SHAP value**: Feature increases risk prediction
- **Negative SHAP value**: Feature decreases risk prediction
- **Magnitude**: Strength of influence

**Example Output** (Top 10 Features):
1. `avg_assessment_score_z`: -0.42 (low scores increase risk)
2. `total_vle_clicks_z`: -0.35 (low engagement increases risk)
3. `early_submission_rate_z`: -0.28 (late submissions increase risk)
4. `papers_failed_z`: +0.25 (failures increase risk)
5. `vle_activity_diversity_z`: -0.22 (narrow activity range increases risk)
...

**Plots Generated** (`plots/shap/`):
- `summary_plot.png`: Global feature importance
- `waterfall_student_*.png`: Individual explanations
- `dependence_plot_*.png`: Feature interaction effects

### 3.4.2 Anchor Explanations (Local Rules)

**Implementation**: `src/explainability/anchor_explainer.py`

**Rule Generation**:
```python
from anchor import anchor_tabular

explainer = anchor_tabular.AnchorTabularExplainer(
    class_names=['Safe', 'At-Risk'],
    feature_names=feature_names,
    train_data=X_train.values
)

explanation = explainer.explain_instance(
    X_test.iloc[i].values,
    model.predict,
    threshold=0.90  # 90% precision
)

# Output: "IF avg_score_z < -0.5 AND vle_clicks_z < -0.3 THEN At-Risk (precision=0.92)"
```

**Advantage**: Human-readable decision rules for educators/students

### 3.4.3 DiCE Counterfactual Explanations

**Implementation**: `src/prescriptive/dice_explainer.py`

**Setup**:
```python
import dice_ml

# Define data interface
dice_data = dice_ml.Data(
    dataframe=training_df,
    continuous_features=actionable_features,  # Exclude immutable
    outcome_name='is_at_risk'
)

# Define model interface
dice_model = dice_ml.Model(model=catboost_model, backend='sklearn')

# Create explainer
explainer = dice_ml.Dice(dice_data, dice_model, method='random')
```

**Generate Counterfactuals**:
```python
counterfactuals = explainer.generate_counterfactuals(
    query_instance=student_features,
    total_CFs=5,  # Generate 5 diverse alternatives
    desired_class=0,  # Want "Safe" outcome (not at-risk)
    features_to_vary=actionable_features  # Only modifiable features
)
```

**Example Output**:
```
Original: At-Risk (probability=0.78)
  avg_assessment_score_z = -0.8
  total_vle_clicks_z = -1.2
  early_submission_rate_z = -0.5

Counterfactual 1: Safe (probability=0.35)
  avg_assessment_score_z = 0.2 (+1.0)  → Improve score to above average
  total_vle_clicks_z = -0.3 (+0.9)     → Increase VLE engagement significantly
  early_submission_rate_z = 0.1 (+0.6)  → Submit earlier more often

Counterfactual 2: Safe (probability=0.38)
  avg_assessment_score_z = -0.2 (+0.6)
  total_vle_clicks_z = 0.5 (+1.7)       → Focus on VLE (more effort here)
  papers_failed_z = 0.0 (-0.3)          → Avoid failures
```

**Feasibility Constraints** (`config/config.yaml`):
```yaml
constraints:
  avg_assessment_score:
    min_multiplier: 1.0  # Can only increase (realistic)
    max_multiplier: 1.5  # Up to 50% improvement
  total_vle_clicks:
    min_multiplier: 1.0
    max_multiplier: 2.0  # Up to 2x engagement
  papers_failed:
    min_multiplier: 0.0  # Can reduce to 0 (retake/improve)
    max_multiplier: 1.0  # Can't increase failures
```

## 3.5 Prescriptive Layer

### 3.5.1 LLM-Based Advice Generation

**Implementation**: `src/prescriptive/llm_advisor.py`

**Gemini 2.5 Flash Configuration**:
```python
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Generation parameters (config.yaml)
generation_config = {
    'temperature': 0.7,      # Balanced creativity/consistency
    'max_output_tokens': 4096,  # Allow longer responses
    'top_p': 0.9             # Nucleus sampling
}
```

**Prompt Engineering**:
```python
prompt = f"""
You are an empathetic academic advisor helping a student improve their performance.

Student Profile:
- Name: {student_name}
- Course: {code_module}
- Current Risk Level: {"High" if risk_prob > 0.7 else "Medium"}
- Risk Probability: {risk_prob:.1%}

Performance Indicators:
- Average Assessment Score: {avg_score} (z-score: {avg_score_z:.2f})
- VLE Engagement: {vle_clicks} clicks (z-score: {vle_clicks_z:.2f})
- Assessments Submitted: {num_submitted}/{total_assessments}

SHAP Explanation (Top Risk Factors):
{shap_top_features}

DiCE Counterfactual Suggestions:
{counterfactual_changes}

Task: Generate personalized, actionable, and encouraging advice (3-5 concrete steps) to help this student reduce their risk and improve performance. Be specific with numbers/targets where possible.
"""

response = model.generate_content(prompt, generation_config=generation_config)
advice = response.text
```

**Example Generated Advice**:
```
Hi [Student Name],

I understand balancing your coursework with other commitments can be challenging, 
but I see opportunities to improve your situation significantly!

Here are 3 concrete steps to reduce your risk:

1. **Boost Your Assessment Scores by 15%**: Your current average is 58%. Focus on 
   upcoming assignments - aim for at least 70% on the next two TMAs. Use the 
   feedback from previous submissions to identify weak areas.

2. **Increase VLE Engagement to 250 clicks/week**: You're currently at 120 clicks/week, 
   which is below average. Spend 30 minutes daily on course materials, especially 
   videos and interactive quizzes. Set a reminder!

3. **Submit Assignments 3+ Days Before Deadline**: You've submitted 60% of work late. 
   Early submissions correlate with better scores and show you're staying on top of 
   material. Start each assignment the week it's announced.

You have the potential to succeed - these changes can move you from high-risk to 
on-track within 3-4 weeks. I'm here to support you!

Best,
Your Academic Support System
```

### 3.5.2 RAG Chatbot System

**Implementation**: `src/chatbot/rag_system.py`

**Architecture**:
```
Student Query → Embedding → FAISS Retrieval (top-k=3) → Gemini Generation → Response
                                      ↑
                              Knowledge Base (OULAD + Study Tips)
```

**Knowledge Base Construction**:
```python
knowledge_base = [
    # Learning strategies
    "Effective time management: Use the Pomodoro technique (25 min study, 5 min break)...",
    "Active reading strategies: SQ3R method (Survey, Question, Read, Recite, Review)...",
    "Spaced repetition: Review material at increasing intervals (1 day, 3 days, 1 week)...",
    
    # VLE-specific tips
    "Maximize VLE engagement: Complete all interactive activities, not just videos...",
    "Use discussion forums: Asking questions and helping peers deepens understanding...",
    
    # Course-specific (from OULAD)
    "Module AAA contains 45 oucontent activities. Focus on completing these sequentially...",
    "Module BBB has 6 quizzes. These are formative - use them to check understanding...",
    
    # Assessment tips
    "TMA preparation: Start 2 weeks before deadline, create outline first...",
    "CMA strategies: Practice with past quizzes, understand concepts not just memorization...",
]
```

**FAISS Indexing**:
```python
from sklearn.feature_extraction.text import TfidfVectorizer
import faiss

# Simple TF-IDF embeddings (lightweight, CPU-compatible)
vectorizer = TfidfVectorizer(max_features=512, stop_words='english')
embeddings = vectorizer.fit_transform(knowledge_base).toarray()

# FAISS index (L2 distance)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings.astype('float32'))
```

**Retrieval**:
```python
def search(query, top_k=3):
    query_embedding = vectorizer.transform([query]).toarray().astype('float32')
    distances, indices = index.search(query_embedding, top_k)
    
    results = [(knowledge_base[i], distances[0][j]) 
               for j, i in enumerate(indices[0])]
    return results
```

**Response Generation with Context**:
```python
def chat(query, student_data, top_k=3):
    # 1. Retrieve relevant context
    context_docs = search(query, top_k)
    context_str = "\n".join([doc for doc, score in context_docs])
    
    # 2. Build personalized prompt
    prompt = f"""
    You are a supportive AI tutor helping {student_data['first_name']}.
    
    Student Context:
    - Module: {student_data['code_module']}
    - Risk Level: {"High" if student_data['risk_probability'] > 0.7 else "Medium"}
    - Average Score: {student_data.get('avg_score', 'N/A')}
    
    Student Question: {query}
    
    Relevant Course Information:
    {context_str}
    
    Provide a helpful, empathetic, and specific response with actionable advice.
    """
    
    # 3. Generate response
    response = gemini_model.generate_content(prompt)
    
    return {
        'query': query,
        'response': response.text,
        'context_used': context_docs,
        'num_contexts': len(context_docs)
    }
```

**Advantages**:
- **Grounded**: Responses based on verified course content and learning science
- **Personalized**: Student profile injected into prompt
- **Transparent**: Can show which knowledge base entries were used
- **Updatable**: Add new course materials without retraining

## 3.6 Interface Layer

### 3.6.1 Student Portal

**Implementation**: `src/lms_portal/student_app.py` (Streamlit)

**Features**:
1. **Authentication**: Login/Register with password hashing
2. **Dashboard**:
   - Risk level indicator (green/yellow/red)
   - Current grades and progress charts
   - VLE engagement statistics
   - SHAP explanation ("Why am I at-risk?")
3. **Course Materials**: List of VLE resources with click tracking
4. **AI Chatbot**:
   - Chat interface with history
   - Personalized responses using RAG
   - Example queries: "How can I improve?", "Study tips?", "Time management?"
5. **Activity Tracking**: Automatic logging when viewing materials

**UI Mockup**:
```
┌─────────────────────────────────────────────────────┐
│  🎓 Student Learning Portal           [Logout]      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Welcome, John Doe! Module: AAA (2013J)             │
│                                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────────┐ │
│  │ Risk Level  │ │ Avg Score   │ │ VLE Clicks    │ │
│  │ ⚠️  HIGH    │ │   58%       │ │  120/week     │ │
│  │   (0.78)    │ │             │ │  (Below avg)  │ │
│  └─────────────┘ └─────────────┘ └───────────────┘ │
│                                                      │
│  📊 Why am I at-risk? (SHAP Explanation)            │
│  • Low assessment scores (-0.42 impact)             │
│  • Below-average VLE engagement (-0.35 impact)      │
│  • Late submissions (-0.28 impact)                  │
│                                                      │
│  💬 Chat with AI Tutor                              │
│  ┌────────────────────────────────────────────────┐ │
│  │ You: I'm struggling with my grades, help!      │ │
│  │                                                 │ │
│  │ AI: I understand this is challenging. Based on │ │
│  │ your profile, here are 3 steps to improve...   │ │
│  │ 1. Increase VLE engagement to 250 clicks/week  │ │
│  │ 2. Target 70%+ on next assignments...          │ │
│  └────────────────────────────────────────────────┘ │
│  [Type your question here...            ] [Send]    │
│                                                      │
│  📚 Course Materials                                │
│  □ Week 1: Introduction to AAA (5 activities)      │
│  □ Week 2: Core Concepts (8 activities)            │
│  ...                                                │
└─────────────────────────────────────────────────────┘
```

### 3.6.2 Advisor Dashboard

**Implementation**: `src/dashboard/app.py` (Streamlit)

**Features**:
1. **At-Risk Student List**:
   - Sortable table by risk probability
   - Filters: module, risk level, last activity
2. **Individual Student View**:
   - Full profile with all metrics
   - SHAP waterfall plot
   - DiCE counterfactual suggestions
   - Chat history with AI tutor
3. **Intervention Management**:
   - Create intervention plans
   - Track intervention outcomes
   - Email/notification triggers
4. **Analytics**:
   - Cohort-level statistics
   - Risk distribution charts
   - Feature importance across cohort

**UI Mockup**:
```
┌─────────────────────────────────────────────────────┐
│  📊 Advisor Dashboard                  [Admin]      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  At-Risk Students (High Priority)                   │
│  ┌────┬─────────┬────────┬──────┬──────────────┐  │
│  │ ID │ Name    │ Module │ Risk │ Last Active  │  │
│  ├────┼─────────┼────────┼──────┼──────────────┤  │
│  │ 42 │ J. Doe  │ AAA    │ 0.89 │ 3 days ago   │  │
│  │ 15 │ A. Smith│ BBB    │ 0.82 │ 1 week ago   │  │
│  │... │ ...     │ ...    │ ...  │ ...          │  │
│  └────┴─────────┴────────┴──────┴──────────────┘  │
│                                                      │
│  [View Details]                                     │
│                                                      │
│  Student: John Doe (ID: 42)                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  SHAP Explanation:                                  │
│  [Waterfall plot showing feature contributions]     │
│                                                      │
│  DiCE Counterfactuals:                             │
│  • Increase VLE clicks from 120 to 250/week        │
│  • Improve avg score from 58% to 70%               │
│  • Submit on time (currently 60% late)             │
│                                                      │
│  AI Chat History (3 conversations):                │
│  • "How to improve grades?" → [View]               │
│  • "Time management tips?" → [View]                │
│                                                      │
│  ✅ Create Intervention                            │
│  [Type: Email/Meeting] [Priority: High]            │
│  [Description: ________________] [Schedule]         │
└─────────────────────────────────────────────────────┘
```

### 3.6.3 LMS Integration (Assumption)

**Integration Points**:
1. **Authentication**: SSO via SAML/OAuth (university credentials)
2. **Data Sync**:
   - Nightly batch: Pull student enrollments, grades, VLE activity
   - Webhook: Real-time updates on new submissions
3. **Intervention Delivery**:
   - Push chatbot suggestions to LMS notifications
   - Advisor actions trigger LMS emails
4. **API Endpoints**:
   - `GET /api/students/{id}/risk`: Fetch risk prediction
   - `POST /api/interventions`: Create intervention
   - `GET /api/chat/{student_id}/history`: Retrieve chat logs

**Architecture** (if integrated with Moodle/Canvas):
```
LMS (Moodle/Canvas) ↔ REST API ↔ PLMS Backend ↔ ML Models
                                      ↓
                                  SQLite DB
                                      ↓
                              Streamlit Dashboards
```

## 3.7 Design Decisions & Trade-offs

### 3.7.1 Why CatBoost as Primary Model?
- **Decision**: Use CatBoost for production predictions
- **Alternatives**: XGBoost, Random Forest
- **Rationale**: 
  - Best AUC on OULAD (0.98 vs 0.95 for RF)
  - Handles categorical features natively (no manual encoding)
  - Built-in class balancing
  - Compatible with SHAP TreeExplainer
- **Trade-off**: Slightly slower training than LightGBM, but offline training acceptable

### 3.7.2 Why FAISS (not Pinecone/Weaviate)?
- **Decision**: FAISS for vector storage
- **Alternatives**: Pinecone, Weaviate, Elasticsearch
- **Rationale**:
  - Lightweight, no external server required
  - CPU-compatible (no GPU needed for deployment)
  - Fast enough for <10k documents (our knowledge base size)
  - Free, open-source
- **Trade-off**: Not suitable for >1M documents, but sufficient for educational content

### 3.7.3 Why Gemini (not GPT-4)?
- **Decision**: Google Gemini 2.5 Flash for LLM
- **Alternatives**: OpenAI GPT-4, Anthropic Claude
- **Rationale**:
  - Cost-effective ($0.075/1M tokens vs GPT-4 $30/1M)
  - Fast inference (~1s vs GPT-4 2-3s)
  - Good quality for educational advice (comparable to GPT-3.5 Turbo)
  - Research partnership (potential academic discount)
- **Trade-off**: Slightly lower quality than GPT-4, but 400x cheaper

### 3.7.4 Why RAG (not Fine-Tuning)?
- **Decision**: RAG for chatbot vs fine-tuning LLM
- **Alternatives**: Fine-tune Gemini, train custom model
- **Rationale**:
  - No large training dataset required (RAG works with <1k documents)
  - Easy to update knowledge base (add new course content)
  - Transparent (can cite sources)
  - Lower computational cost (no GPU training)
- **Trade-off**: Retrieval quality depends on indexing; fine-tuned model might be more fluent

### 3.7.5 Why Streamlit (not Django/React)?
- **Decision**: Streamlit for web interfaces
- **Alternatives**: Django+React, Flask+Vue
- **Rationale**:
  - Rapid prototyping (10x faster development)
  - Python-native (same language as ML pipeline)
  - Reactive UI (auto-updates on state change)
  - Sufficient for research prototype (not production-scale)
- **Trade-off**: Less customizable than React, performance limits for >1000 concurrent users

### 3.7.6 Why Z-Score (not Min-Max Scaling)?
- **Decision**: Z-score standardization for features
- **Alternatives**: Min-max scaling (0-1), robust scaling
- **Rationale**:
  - Preserves outlier information (important in education: exceptional students)
  - Mean=0, Std=1 makes interpretation easier
  - Works well with tree-based models (CatBoost insensitive to scale, but SVM benefits)
- **Trade-off**: Sensitive to outliers (but we want to detect them anyway)

---

**Key Design Principles**:
✓ **Explainability First**: XAI at every decision point  
✓ **Scalability**: Batch processing, async operations  
✓ **Reproducibility**: Fixed seeds, version control  
✓ **Privacy**: Role-based access, encryption  
✓ **Extensibility**: Modular components, plugin architecture  

**Implementation Fidelity**:
- All components reference actual code files in `/home/khale/LVTN/plaf/src/`
- Configuration driven by `config/config.yaml`
- Benchmarked on OULAD dataset (32,593 students)
- Open-source, reproducible pipeline

