# System Overview: PLMS Architecture

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLMS ARCHITECTURE (8-Stage Pipeline)         │
└─────────────────────────────────────────────────────────────────┘

[Stage 1-2: Data Layer]
    OULAD Dataset (32,593 students, 7 tables)
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
    ├── CatBoost (Best Model: AUC=0.983)
    ├── Random Forest (AUC=0.975)
    ├── XGBoost (AUC=0.972)
    ├── SVM (AUC=0.965)
    └── Logistic Regression (AUC=0.923)
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

## Technology Stack

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

## Data Flow Architecture

### 1. Data Ingestion Pipeline
```
OULAD CSV Files → Data Validation → Merging → SQLite Storage
     ↓
Feature Engineering → Z-Score Standardization → Modeling Dataset
     ↓
Train/Test Split (80/20) → Cross-Validation → Model Selection
```

### 2. Real-Time Prediction Pipeline
```
New Student Data → Feature Computation → Model Inference → Risk Score
     ↓
XAI Generation → SHAP + DiCE + Anchors → Explanations
     ↓
RAG Chatbot → FAISS Retrieval → Gemini Generation → Response
     ↓
Dashboard Update → Student/Advisor Interfaces
```

### 3. Cold-Start Pipeline
```
New Student Demographics → K-NN Search → Similar Students
     ↓
Weighted Prediction → Confidence Score → Risk Assessment
     ↓
Immediate Intervention → Chatbot Support → Advisor Notification
```

## Component Details

### Predictive Models
```python
# Model Configuration
models = {
    'CatBoost': CatBoostClassifier(
        iterations=500,
        learning_rate=0.1,
        depth=6,
        auto_class_weights='Balanced',
        random_state=42
    ),
    'RandomForest': RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight='balanced',
        random_state=42
    ),
    # ... other models
}

# Evaluation Metrics
metrics = ['accuracy', 'precision', 'recall', 'f1', 'auc']
cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
```

### XAI Implementation
```python
# SHAP Global Explanations
explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_sample)
shap.summary_plot(shap_values, X_sample)

# DiCE Counterfactuals
dice_explainer = Dice(data, model, method='random')
counterfactuals = dice_explainer.generate_counterfactuals(
    query_instance, total_CFs=5, desired_class=0
)

# Anchor Rules
anchor_explainer = AnchorTabularExplainer(...)
explanation = anchor_explainer.explain_instance(
    instance, model.predict, threshold=0.90
)
```

### RAG System
```python
# Knowledge Base Construction
knowledge_base = [
    "Effective time management: Use the Pomodoro technique...",
    "Active reading strategies: SQ3R method...",
    "VLE engagement tips: Complete all interactive activities...",
    # ... course-specific content from OULAD
]

# FAISS Indexing
vectorizer = TfidfVectorizer(max_features=512)
embeddings = vectorizer.fit_transform(knowledge_base)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings.astype('float32'))

# Response Generation
def chat(query, student_data):
    # Retrieve relevant context
    context_docs = search(query, top_k=3)
    
    # Generate personalized response
    prompt = build_prompt(query, context_docs, student_data)
    response = gemini_model.generate_content(prompt)
    
    return response.text
```

### Cold-Start Handler
```python
class ColdStartHandler:
    def __init__(self, historical_data):
        self.demographic_features = [
            'gender', 'region', 'highest_education',
            'imd_band', 'age_band', 'disability'
        ]
        self.knn_model = NearestNeighbors(n_neighbors=10)
        self._prepare_model()
    
    def predict_new_student(self, demographics):
        # Encode demographics
        encoded = encode_demographics(demographics)
        
        # Find similar students
        distances, indices = self.knn_model.kneighbors([encoded])
        
        # Weighted prediction
        neighbors = self.historical_data.iloc[indices[0]]
        weights = 1 / (distances[0] + 1e-6)
        risk_prob = np.average(neighbors['risk_probability'], weights=weights)
        
        return {'risk_probability': risk_prob, 'confidence': confidence}
```

## Interface Architecture

### Student Portal
```python
# Streamlit App Structure
def student_portal():
    # Authentication
    if not st.session_state.logged_in:
        login_page()
        return
    
    # Dashboard
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Risk Level", risk_level, delta=None)
    with col2:
        st.metric("Average Score", avg_score, delta=score_change)
    with col3:
        st.metric("VLE Engagement", vle_clicks, delta=vle_change)
    
    # SHAP Explanation
    st.subheader("Why am I at-risk?")
    display_shap_explanation(student_shap_values)
    
    # AI Chatbot
    st.subheader("Chat with AI Tutor")
    chat_interface(rag_system, student_data)
    
    # Course Materials
    st.subheader("Course Materials")
    display_course_materials(student_id)
```

### Advisor Dashboard
```python
# Advisor Interface
def advisor_dashboard():
    # At-risk student list
    st.subheader("At-Risk Students")
    at_risk_students = get_at_risk_students()
    selected_student = st.selectbox("Select Student", at_risk_students)
    
    if selected_student:
        # Student details
        display_student_profile(selected_student)
        
        # SHAP waterfall plot
        display_shap_plot(selected_student)
        
        # DiCE counterfactuals
        display_counterfactuals(selected_student)
        
        # Chat history
        display_chat_history(selected_student)
        
        # Intervention planning
        create_intervention(selected_student)
```

## Database Schema

### Core Tables
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
    is_at_risk BOOLEAN,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Activities Table (VLE tracking)
CREATE TABLE activities (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    material_id INTEGER,
    activity_type TEXT,
    timestamp DATETIME,
    duration INTEGER,
    clicks INTEGER,
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
    attempts INTEGER,
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
    response_quality REAL,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- Interventions Table
CREATE TABLE interventions (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    advisor_id INTEGER,
    intervention_type TEXT,
    description TEXT,
    status TEXT,  -- Pending/Completed/Declined
    created_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (student_id) REFERENCES students(id)
);
```

## Performance Characteristics

### Computational Performance
```
System Performance Metrics
┌─────────────────┬──────────┬──────────┬──────────┬──────────┐
│ Component       │ Startup  │ Runtime  │ Memory   │ CPU      │
│                 │ Time     │ Latency  │ Usage    │ Usage    │
├─────────────────┼──────────┼──────────┼──────────┼──────────┤
│ ML Models       │ 2.3s     │ 0.08ms   │ 156MB    │ 12%      │
│ FAISS Index     │ 0.8s     │ 0.03ms   │ 23MB     │ 3%       │
│ Database        │ 0.5s     │ 0.02ms   │ 45MB     │ 2%       │
│ Streamlit Apps  │ 3.2s     │ 0.15ms   │ 89MB     │ 8%       │
│ Gemini API      │ N/A      │ 1.21s    │ 0MB      │ 0%       │
├─────────────────┼──────────┼──────────┼──────────┼──────────┤
│ Total System    │ 6.8s     │ 1.34s    │ 313MB    │ 25%      │
└─────────────────┴──────────┴──────────┴──────────┴──────────┘
```

### Scalability Limits
- **Concurrent Users**: 100 (single instance)
- **Database Size**: 1M students (SQLite limit)
- **FAISS Index**: 100K documents (memory limit)
- **API Rate**: 60 requests/minute (Gemini limit)

### Optimization Strategies
- **Batch Processing**: Offline ML training, real-time inference
- **Caching**: FAISS index persistence, model serialization
- **Async Processing**: Chatbot queue system for high load
- **Database Indexing**: Optimized queries for common operations

## Security and Privacy

### Authentication & Authorization
```python
# Role-based access control
def check_permissions(user_id, resource, action):
    user_role = get_user_role(user_id)
    
    if user_role == 'student':
        return resource == 'own_data' and action in ['read', 'update']
    elif user_role == 'advisor':
        return resource in ['student_data', 'interventions'] and action in ['read', 'create']
    elif user_role == 'admin':
        return True
    
    return False
```

### Data Protection
- **Encryption**: Student data encrypted at rest and in transit
- **Anonymization**: Personal identifiers removed from training data
- **Consent**: Students can opt out of AI monitoring
- **Audit Logs**: All access and modifications logged
- **GDPR/FERPA**: Compliance with privacy regulations

### Privacy Controls
- **Data Minimization**: Only necessary data collected
- **Right to Explanation**: Students can request prediction explanations
- **Data Portability**: Students can export their data
- **Right to Deletion**: Students can request data removal

## Deployment Architecture

### Development Environment
```
Local Development Setup
├── Python Virtual Environment
├── SQLite Database
├── Streamlit Development Server
├── Local FAISS Index
└── Gemini API (external)
```

### Production Deployment
```
Production Architecture
├── Load Balancer (nginx)
├── Application Servers (multiple Streamlit instances)
├── Database Cluster (PostgreSQL)
├── Redis Cache
├── FAISS Index Sharding
├── API Gateway (Gemini integration)
└── Monitoring & Logging
```

### LMS Integration
```
LMS Integration Points
├── SSO Authentication (SAML/OAuth)
├── Data Synchronization (nightly batch + webhooks)
├── API Endpoints (REST/GraphQL)
├── Notification System (email/SMS)
└── Analytics Dashboard (embedded)
```

## Configuration Management

### Central Configuration
```yaml
# config/config.yaml
model:
  cv_folds: 5
  primary_metric: "f1"
  models: [catboost, random_forest, xgboost, svm, logistic_regression]

xai:
  shap:
    background_samples: 100
    top_features: 10
  dice:
    total_CFs: 5
    desired_class: 0

rag:
  top_k: 3
  similarity_threshold: 0.7

llm:
  model_name: "gemini-2.5-flash"
  temperature: 0.7
  max_tokens: 500
```

### Environment Management
```bash
# .env file
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///data/lms_test.db
LOG_LEVEL=INFO
DEBUG=False
```

## Monitoring and Maintenance

### Health Checks
```python
def system_health_check():
    checks = {
        'database': check_database_connection(),
        'ml_models': check_model_loading(),
        'faiss_index': check_index_integrity(),
        'gemini_api': check_api_connectivity(),
        'streamlit_apps': check_app_availability()
    }
    
    return all(checks.values()), checks
```

### Performance Monitoring
- **Response Times**: Track API and inference latency
- **Error Rates**: Monitor system failures and exceptions
- **Resource Usage**: CPU, memory, disk, network utilization
- **User Engagement**: Chat frequency, feature usage, satisfaction scores

### Maintenance Tasks
- **Model Retraining**: Periodic updates with new data
- **Index Updates**: Refresh FAISS index with new content
- **Database Cleanup**: Archive old data, optimize queries
- **Security Updates**: Regular dependency updates and patches

---

*This system overview provides a comprehensive understanding of the PLMS architecture, enabling effective communication of technical details during the defense presentation.*
