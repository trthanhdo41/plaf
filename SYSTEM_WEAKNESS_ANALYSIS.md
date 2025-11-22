# System Weakness Analysis & Improvement Plan

**Date:** November 20, 2025
**Status:** Critical Review

## Executive Summary

Your system has a strong architecture (ML + Explainability + RAG), but currently relies on **simulated/mock data** for its most advanced features. This undermines the "AI" value proposition.

| Component | Status | Critical Issue |
|-----------|--------|----------------|
| **ML Predictions** | ✅ Fixed | Predictions are now correctly populating the database (3,350 at-risk students found). |
| **Explainability** | ✅ **FIXED** | `explainability_bridge.py` now uses real SHAP/DiCE values. |
| **RAG System** | ✅ **IMPROVED** | Knowledge base now includes 18 data-driven insights from OULAD analysis. |
| **Evaluation** | ✅ **COMPLETE** | Model evaluation report generated with 95% accuracy, 98.5% AUC-ROC. |

---


## 1. Explainability is "Fake" (FIXED)

**File:** `src/explainability/explainability_bridge.py`

**Problem:** The system was using hardcoded rules instead of the trained ML model to generate SHAP values and counterfactuals.

**Fix Implemented:**
- Modified `explainability_bridge.py` to load the actual trained model (`models/best_model.pkl`) and feature data.
- Integrated `SHAPExplainer` to calculate real SHAP values based on student features.
- Integrated `CounterfactualGenerator` (DiCE) to generate data-driven counterfactuals for at-risk students.
- Added fallback logic to infer feature names if the pickle file is missing.

**Verification:**
- Verified using `verify_explainability.py`.
- Low-risk students show low probability and negative SHAP values.
- High-risk students show high probability, positive SHAP values, and actionable DiCE recommendations.

---

## 2. RAG Knowledge Base is Generic (IMPROVED)

**File:** `src/chatbot/rag_system.py`

**Problem:** The chatbot's knowledge base was limited to ~12 generic study tips, lacking data-driven insights from OULAD analysis.

**Fix Implemented:**
- Created `enhance_knowledge_base.py` to analyze the modeling data and extract patterns.
- Generated 18 data-driven documents covering:
  - Engagement patterns (low/medium/high engagement risk rates)
  - Score patterns (performance categories and associated risks)
  - Course-specific insights (risk rates by module)
  - Combined risk factors (multiple warning signs)
  - Submission patterns (assignment completion impact)
  - Evidence-based success strategies
  - Early warning signs
- Modified `rag_system.py` to load `data/enhanced_knowledge_base.txt`.
- Total knowledge base now contains 122 documents (12 generic + 92 from DB + 18 data-driven).

**Verification:**
- Verified using `test_rag_enhanced.py`.
- RAG system successfully loads and indexes all documents.
- Search queries now return specific, data-driven advice (e.g., "Students with low engagement have 93.9% risk").

---

## 4. Evaluation Metrics are Missing (COMPLETE)

**File:** `generate_evaluation_report.py`

**Problem:** The evaluation script existed but hadn't been run to verify model performance.

**Fix Implemented:**
- Ran `generate_evaluation_report.py` on test set (6,519 students)
- Generated comprehensive metrics and visualizations

**Results:**
- **Overall Accuracy:** 95%
- **AUC-ROC Score:** 0.9848 (excellent discrimination)
- **Precision (At-Risk):** 97% (few false alarms)
- **Recall (At-Risk):** 92.2% (catches most at-risk students)
- **False Negative Rate:** 7.8% (268 missed at-risk students)
- **False Positive Rate:** 2.9% (88 safe students flagged)

**Top 3 Most Important Features:**
1. `submission_rate_z` (15.3) - Assignment completion is critical
2. `has_unregistrations` (9.3) - Course withdrawals are strong predictor
3. `avg_score_z` (7.7) - Assessment performance matters

**Visualizations Generated:**
- Confusion matrix: `plots/evaluation/confusion_matrix.png`
- ROC curve: `plots/evaluation/roc_curve.png`
- Risk distribution: `plots/evaluation/risk_distribution.png`

**Critical Finding:**
- 7.8% false negative rate means 268 at-risk students are missed
- This is acceptable for an early warning system (92.2% recall is good)
- Could lower threshold to catch more at-risk students if needed

---

## Recommended Action Plan

1.  **Switch to Real Explainability**: ✅ **DONE** (Integrated SHAP and DiCE into bridge)
2.  **Enrich Knowledge Base**: ✅ **DONE** (Generated 18 data-driven documents from OULAD analysis)
3.  **Run Evaluation**: ✅ **DONE** (95% accuracy, 98.5% AUC-ROC, 7.8% FN rate)
