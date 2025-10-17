# Chapter 4: Implementation

## 4.1 Implementation Overview

This chapter summarizes the implementation of the Prescriptive Learning Management System (PLMS), focusing on the 8-stage pipeline execution and key technical components. The complete implementation is available in the open-source repository with detailed code in `run_pipeline.py` and supporting modules.

## 4.2 Pipeline Execution Summary

### 4.2.1 Stage 1-2: Data Ingestion & Preprocessing
- **Input**: OULAD dataset (7 CSV files, 32,593 students)
- **Processing**: Data validation, merging, cleaning
- **Output**: Merged dataset (`data/processed/merged_data.csv`)
- **Key Files**: `src/data/loader.py`, `src/data/preprocessing.py`

### 4.2.2 Stage 3: Feature Engineering
- **Features**: 25 engineered features with z-score standardization
- **Categories**: Demographics (6), VLE behavior (10), Assessment performance (9)
- **Output**: Feature-engineered dataset (`data/features/modeling_data.csv`)
- **Key Files**: `src/data/feature_engineering.py`

### 4.2.3 Stage 4: ML Model Training
- **Models**: 5 algorithms (CatBoost, RF, XGBoost, SVM, LR)
- **Validation**: 5-fold stratified cross-validation
- **Selection**: Best model saved (`models/best_model.pkl`)
- **Key Files**: `src/models/train.py`

### 4.2.4 Stage 5: Explainability Generation
- **SHAP**: Global and local explanations (`plots/shap/`)
- **Anchors**: Rule-based explanations
- **DiCE**: Counterfactual examples (`results/counterfactuals.json`)
- **Key Files**: `src/explainability/`, `src/prescriptive/dice_explainer.py`

### 4.2.5 Stage 6: LLM Advice Generation
- **Model**: Google Gemini 2.5 Flash
- **Input**: SHAP + DiCE explanations
- **Output**: Personalized advice (`results/llm_advice.json`)
- **Key Files**: `src/prescriptive/llm_advisor.py`

### 4.2.6 Stage 7-8: Interface Deployment
- **Student Portal**: Streamlit app (`src/lms_portal/student_app.py`)
- **Advisor Dashboard**: Streamlit app (`src/dashboard/app.py`)
- **Database**: SQLite with real-time updates
- **Integration**: LMS-ready API endpoints

## 4.3 Key Implementation Components

### 4.3.1 Cold-Start Handler
- **Algorithm**: K-NN on 6 demographic features
- **Implementation**: `src/models/cold_start_handler.py`
- **Features**: Gender, region, education, IMD, age, disability
- **Output**: Risk probability + confidence score

### 4.3.2 RAG Chatbot System
- **Vector Store**: FAISS with TF-IDF embeddings
- **LLM**: Gemini 2.5 Flash for generation
- **Knowledge Base**: OULAD course content + learning strategies
- **Implementation**: `src/chatbot/rag_system.py`

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
