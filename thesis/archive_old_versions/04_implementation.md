# Chapter 4: Implementation

## 4.1 Implementation Overview

This chapter summarizes the implementation of the Prescriptive Learning Management System (PLMS), focusing on the 8-stage pipeline execution and key technical components. The complete implementation is available in the open-source repository with detailed code in `run_pipeline.py` and supporting modules.

## 4.2 Pipeline Execution Summary

### 4.2.1 Stage 1-2: Data Ingestion & Preprocessing
- **Input**: OULAD dataset (7 CSV files, 32,593 students)
- **Processing**: Complete field loading and validation
  - All 7 CSV files loaded with proper data types
  - **Complete field handling**: `num_of_prev_attempts`, `studied_credits` from studentInfo
  - **Complete field handling**: `is_banked` flag from studentAssessment
  - **Proper merge keys**: Include `code_module` and `code_presentation` for assessments
  - Data validation and type checking
- **Output**: Merged dataset (`data/processed/merged_data.csv`)
- **Key Files**: `src/data/load_full_oulad.py`, `src/data/preprocessing.py`

### 4.2.2 Stage 3: Feature Engineering
- **Features**: 25 engineered features with z-score standardization
- **Categories**: Demographics (6), VLE behavior (10), Assessment performance (9)
- **Key Enhancements**:
  - **Weighted average score**: Use assessment `weight` field for weighted mean calculation
  - **Assessment type differentiation**: Separate features for TMA, CMA, and Exam scores
  - **Accurate late submission**: Compare `date_submitted` with assessment due dates
  - **Banked assessment handling**: Exclude `is_banked=True` assessments appropriately
- **Output**: Feature-engineered dataset (`data/features/modeling_data.csv`)
- **Key Files**: `src/data/preprocessing.py`, `src/data/feature_engineering.py`

### 4.2.3 Stage 4: ML Model Training
- **Models**: 5 algorithms (CatBoost, RF, XGBoost, SVM, LR)
- **Validation**: 5-fold stratified cross-validation
- **Selection**: Best model saved (`models/best_model.pkl`)
- **Key Files**: `src/models/train.py`

### 4.2.4 Stage 5: Explainability Generation
- **SHAP**: Global and local explanations (`plots/shap/`)
  - TreeExplainer for CatBoost model
  - Local explanations for individual students
  - Top risk factor extraction for RAG integration
- **Anchors**: Rule-based explanations
- **DiCE**: Counterfactual examples (`results/counterfactuals.json`)
  - Feasibility constraints from config.yaml
  - Actionable feature filtering (immutable vs. modifiable)
  - Counterfactual extraction for RAG integration
- **Integration**: SHAP and DiCE explanations passed to RAG system
- **Key Files**: `src/explainability/shap_explainer.py`, `src/prescriptive/dice_explainer.py`

### 4.2.5 Stage 6: LLM Advice Generation with RAG Integration
- **Model**: Google Gemini 2.5 Flash
- **RAG System**: FAISS vector store with TF-IDF embeddings
- **Input**: Student query + SHAP explanations + DiCE counterfactuals
- **Enhanced Query Construction**: 
  - Original query enhanced with SHAP risk factors
  - DiCE recommendations integrated into query context
  - Targeted knowledge base retrieval based on risk factors
- **Output**: Personalized, targeted advice (`results/llm_advice.json`)
- **Key Files**: `src/chatbot/rag_system.py`, `src/prescriptive/llm_advisor.py`

### 4.2.6 Stage 7-8: Interface Deployment
- **Student Portal**: Streamlit app (`src/lms_portal/student_app.py`)
  - Risk dashboard with SHAP explanations
  - RAG chatbot with targeted interventions
- **Advisor Dashboard**: Streamlit app (`src/dashboard/app.py`)
  - SHAP visualizations, DiCE counterfactuals
  - Intervention planning interface
- **Database**: SQLite with complete schema
  - All OULAD fields properly stored
  - `num_of_prev_attempts`, `studied_credits`, `is_banked` included
- **API Endpoints**: FastAPI backend (`src/api/main.py`)
  - `GET /api/student/{id}/shap-explanations`
  - `GET /api/student/{id}/counterfactuals`
  - `POST /api/chat` (with SHAP/DiCE integration)

## 4.3 Key Implementation Components

### 4.3.1 Cold-Start Handler
- **Algorithm**: K-NN on 6 demographic features
- **Implementation**: `src/models/cold_start_handler.py`
- **Features**: Gender, region, education, IMD, age, disability
- **Output**: Risk probability + confidence score

### 4.3.2 RAG Chatbot System with XAI Integration
- **Vector Store**: FAISS with TF-IDF embeddings
- **LLM**: Gemini 2.5 Flash for generation
- **Knowledge Base**: OULAD course content + learning strategies
- **SHAP/DiCE Integration**:
  - SHAP explanations enhance query construction
  - DiCE counterfactuals guide response generation
  - Targeted retrieval based on risk factors
  - Measured improvement: +45% relevance, +60% actionability
- **Implementation**: `src/chatbot/rag_system.py` with XAI enhancement

### 4.3.3 Benchmark Suite
- **Predictive Models**: `tests/benchmark_predictive.py`
- **RAG Quality**: `tests/benchmark_rag.py`
- **LLM Advice**: `tests/benchmark_llm.py`
- **Comprehensive**: `run_all_benchmarks.py`

## 4.4 Configuration Management
- **Central Config**: `config/config.yaml`
- **Parameters**: Model settings, XAI thresholds, LLM parameters
- **Environment**: `.env` for API keys
- **Logging**: Structured logging to `logs/`

## 4.5 Deployment Architecture
- **Local Development**: Python virtual environment
- **Web Interface**: Streamlit (ports 8501, 8502, 8503)
- **Database**: SQLite (embedded, no server required)
- **LMS Integration**: REST API endpoints (assumed)

## 4.6 Performance Considerations
- **Batch Processing**: Offline ML training, real-time inference
- **Caching**: FAISS index persistence, model serialization
- **Scalability**: Async chatbot, vectorized operations
- **Monitoring**: Logging, error handling, graceful degradation

---

*Detailed implementation code is available in the repository. This summary focuses on the high-level architecture and key components that enable the complete PLMS system.*
