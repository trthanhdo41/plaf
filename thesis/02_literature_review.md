# Chapter 2: Literature Review & Theoretical Framework

## 2.1 Learning Analytics Framework

### 2.1.1 Evolution of Learning Analytics

**Descriptive Analytics (What happened?)**
- Historical data analysis: grades, attendance, completion rates
- Dashboard reporting for administrators
- Limitation: Reactive, no predictive power
- Examples: Tableau dashboards, basic LMS reports

**Diagnostic Analytics (Why did it happen?)**
- Correlation analysis, pattern identification
- Root cause analysis of student performance
- Limitation: Explains past, doesn't predict future
- Examples: Regression analysis, factor analysis

**Predictive Analytics (What will happen?)**
- Machine learning for forecasting outcomes
- At-risk student identification
- Limitation: Prediction without prescription
- Examples: Dropout prediction models, early warning systems

**Prescriptive Analytics (What should we do?)**
- Actionable recommendations based on predictions
- Intervention strategies, personalized guidance
- **Key Innovation**: Closes the loop from insight to action
- Reference: **Susnjak, T. (2023). Prescriptive Learning Analytics Framework (PLAF)**

### 2.1.2 Susnjak's PLAF Framework

**Framework Stages**:
1. **Data Collection**: Multi-source integration (LMS, SIS, external)
2. **Feature Engineering**: Domain-relevant predictors
3. **Predictive Modeling**: Risk assessment algorithms
4. **Explainability**: Interpretable AI for trust
5. **Counterfactual Analysis**: "What if" scenarios
6. **Recommendation Generation**: Actionable advice
7. **Intervention Delivery**: Communication to stakeholders
8. **Outcome Monitoring**: Close the feedback loop

**Gap in Original Framework**:
- Susnjak proposed conceptual framework, no full implementation
- No automated intervention mechanism (manual advisor required)
- No cold-start solution for new students
- **This thesis**: First complete implementation with RAG-based automation

## 2.2 Student At-Risk Prediction

### 2.2.1 Machine Learning Approaches

**Decision Trees & Ensembles**
- Random Forest (Breiman, 2001): Ensemble of decision trees, robust to overfitting
- XGBoost (Chen & Guestrin, 2016): Gradient boosting, handles imbalanced data
- CatBoost (Prokhorenkova et al., 2018): Categorical feature handling, ordered boosting
- Advantage: Interpretable feature importance, high accuracy
- Application in education: Student dropout prediction (Hellas et al., 2018)

**Support Vector Machines**
- SVM (Cortes & Vapnik, 1995): Maximum margin classifier, kernel methods
- Application: Course failure prediction (Márquez-Vera et al., 2016)
- Limitation: Difficult to interpret, computationally expensive for large datasets

**Logistic Regression**
- Traditional baseline for binary classification
- Advantage: Interpretable coefficients, probabilistic output
- Application: MOOCs dropout prediction (Xing et al., 2016)

**Deep Learning**
- Neural networks, LSTMs for sequential student data
- High accuracy but "black box" nature
- Limited adoption in education due to interpretability requirements
- Reference: Recurrent Neural Networks for student modeling (Piech et al., 2015)

### 2.2.2 Feature Engineering in Educational Contexts

**Demographic Features**
- Age, gender, socioeconomic status (IMD band), prior education
- Predictive but immutable (cannot be changed by intervention)

**Behavioral Features**
- VLE engagement: clicks, time spent, activity diversity
- Assessment performance: scores, submission timing, attempts
- Highly predictive and actionable (can be influenced)

**Temporal Features**
- Early vs. late submission patterns
- Trajectory of engagement over time
- Critical: Early prediction requires features available in first weeks

**OULAD-Specific Features** (used in this thesis):
- 25 engineered features with z-score standardization
- Examples: `avg_assessment_score_z`, `total_vle_clicks_z`, `vle_activity_diversity_z`
- Immutable: gender, region, age_band (6 features)
- Actionable: VLE engagement, assessment performance (19 features)

### 2.2.3 State-of-the-Art Results on OULAD

- Kuzilek et al. (2017): Original OULAD paper, baseline models
- Hlosta et al. (2017): Early prediction, AUC 0.70-0.80 in first weeks
- Waheed et al. (2020): Deep learning approach, AUC 0.87
- **Our target**: AUC > 0.90 with interpretable models (CatBoost, RF)

## 2.3 Explainable AI in Education

### 2.3.1 The Need for XAI in High-Stakes Decisions

**Educational Context Demands Transparency**:
- Students have right to understand risk predictions (GDPR, FERPA)
- Educators need to trust and act on AI recommendations
- Institutional accountability requires explainable decisions
- Ethical imperative: Avoid "black box" discrimination

### 2.3.2 SHAP (SHapley Additive exPlanations)

**Theoretical Foundation**:
- Lundberg & Lee (2017): Unified framework for interpretability
- Game-theoretic approach: Feature contributions to prediction
- Shapley values from cooperative game theory (fair attribution)

**Application in This Work**:
- TreeExplainer for ensemble models (CatBoost, RF, XGBoost)
- Global importance: Top 10 features driving overall predictions
- Local explanations: Individual student's risk factors
- Implementation: `src/explainability/shap_explainer.py`

**Advantages**:
- Model-agnostic, theoretically grounded
- Consistent feature attributions
- Visual plots: summary, waterfall, force plots

**Limitations**:
- Computational cost: O(TLD²) for tree models (T=trees, L=leaves, D=depth)
- Requires background data sample for comparison
- Approximations for large feature spaces

### 2.3.3 Anchor Explanations

**Rule-Based Interpretability**:
- Ribeiro et al. (2018): High-precision local rules
- "IF condition1 AND condition2 THEN prediction (with 90% precision)"
- Example: "IF total_vle_clicks_z < -0.5 AND avg_score < 60 THEN at-risk (precision 0.92)"

**Application**:
- Local explanations for individual students
- Human-readable decision boundaries
- Implementation: `src/explainability/anchor_explainer.py`

**Trade-offs**:
- High precision but may have limited coverage
- Threshold selection (0.90 in our config)
- Simpler than SHAP but less comprehensive

### 2.3.4 DiCE Counterfactual Explanations

**Counterfactual Reasoning for Actionability**:
- Mothilal et al. (2020): Diverse Counterfactual Explanations
- "What changes would flip your prediction from at-risk to safe?"
- Example: "Increase VLE clicks by 50% AND improve assessment score by 15 points"

**Why DiCE for Education**:
- Actionable: Shows what students can change
- Diverse: Multiple pathways to success (not one-size-fits-all)
- Feasible: Constraints on realistic changes (can't change demographics)

**Implementation Details**:
- Feasibility constraints in `config/config.yaml`:
  - `avg_assessment_score`: Can only increase (1.0-1.5x multiplier)
  - `total_vle_clicks`: Can increase up to 2x
  - `papers_failed`: Can reduce to 0
- Immutable features: gender, region, age_band, num_prev_attempts
- Actionable features: VLE engagement, assessment performance

**Alternatives Considered**:
- LIME (Ribeiro et al., 2016): Less actionable, perturbation-based
- Prototype selection: Shows similar successful students
- Chosen DiCE for direct actionability

## 2.4 Conversational AI for Education

### 2.4.1 Educational Chatbots: Evolution

**Rule-Based Chatbots (2010s)**:
- Decision trees, keyword matching
- Limited conversational ability
- Example: AutoTutor (Graesser et al., 2004)

**Retrieval-Based Chatbots**:
- FAQ matching, template responses
- Better coverage but rigid
- Example: Jill Watson (Georgia Tech, 2016)

**Generative AI Chatbots (2020s)**:
- GPT-3, GPT-4, Gemini: Natural language generation
- Flexible, human-like responses
- Risk: Hallucination, lack of grounding in facts

### 2.4.2 Retrieval-Augmented Generation (RAG)

**Why RAG for Educational Contexts**:
- **Grounding**: Responses based on verified knowledge base (course content, strategies)
- **Controllability**: Retrieval ensures relevant context, reduces hallucination
- **Updatability**: Easy to add new course materials without retraining LLM
- **Transparency**: Can show sources for responses

**RAG Architecture** (Lewis et al., 2020):
1. **Indexing**: Embed knowledge base into vector store (FAISS)
2. **Retrieval**: Find top-k relevant documents for query (cosine similarity)
3. **Generation**: LLM generates response conditioned on retrieved context

**Our Implementation**:
- Knowledge base: OULAD course activities + learning strategies + study tips
- Vector store: FAISS with TF-IDF embeddings (lightweight, CPU-compatible)
- LLM: Google Gemini 2.5 Flash (fast, cost-effective)
- Personalization: Inject student context (name, risk level, performance) into prompt
- Implementation: `src/chatbot/rag_system.py`

**Advantages Over Fine-Tuning**:
- No need for large training dataset
- Easily updated with new content
- Lower computational cost
- Maintains general LLM capabilities

### 2.4.3 Personalization in AI Tutoring Systems

**Importance of Context-Aware Responses**:
- Generic advice ineffective (Pane et al., 2014)
- Students need guidance tailored to their situation
- Personalization dimensions:
  - Risk level (high/medium/low)
  - Performance metrics (grades, VLE engagement)
  - Course context (module, presentation)
  - Emotional state (detected from query sentiment)

**Our Personalization Strategy**:
- Student profile injected into LLM prompt:
  ```
  Student: [First Name], Module: [Code], Risk: [Probability]
  Current Performance: Avg Score [X], VLE Clicks [Y]
  Query: [Student's question]
  Context: [Retrieved course strategies]
  Generate empathetic, specific, actionable advice.
  ```

### 2.4.4 Empathy in AI Responses

**Why Empathy Matters**:
- At-risk students often face emotional challenges (anxiety, overwhelm)
- Empathetic tone improves engagement (Brave & Nass, 2009)
- AI should support, not judge

**Empathy Techniques in Our Chatbot**:
- Acknowledgment: "I understand this is challenging..."
- Encouragement: "You can improve with these steps..."
- Specificity: Concrete actions rather than vague advice
- Positive framing: Focus on growth potential, not deficits

## 2.5 Cold-Start Problem in Educational AI

### 2.5.1 Defining the Cold-Start Problem

**Three Types of Cold-Start**:
1. **New User**: Student with no historical learning data (our focus)
2. **New Item**: New course with no student data
3. **New System**: Entire system launch with minimal data

**Why Critical in Education**:
- First weeks are crucial for intervention (Tinto, 1975)
- Waiting for historical data means missing critical window
- Traditional ML models cannot predict without features

### 2.5.2 Existing Solutions

**Content-Based Filtering**:
- Use student demographics/pre-enrollment data
- Assumption: Similar students have similar outcomes
- Reference: Demographic prediction in MOOCs (Kizilcec et al., 2013)

**Collaborative Filtering**:
- Use similarity to other students
- Limitation: Requires some overlap in features/courses

**Transfer Learning**:
- Train on one cohort, apply to new cohort
- Limitation: Domain shift between cohorts/institutions

**Default/Average Prediction**:
- Assign population average risk
- Baseline but uninformative (no personalization)

### 2.5.3 Our K-NN Demographic Approach

**Innovation**: K-Nearest Neighbors on Demographics Only

**Method**:
1. Encode 6 demographic features: gender, region, education, IMD, age, disability
2. Find k=10 most similar historical students (Euclidean distance)
3. Weighted risk prediction based on neighbor outcomes
4. Confidence score: Inverse of average distance (closer neighbors = higher confidence)

**Implementation**: `src/models/cold_start_handler.py`

**Advantages**:
- Works on day one (demographics available at enrollment)
- Interpretable (similar students as evidence)
- Confidence scoring indicates reliability
- No training required (instance-based learning)

**Evaluation**:
- Compare MAE, RMSE against historical students
- Measure accuracy gap: cold-start vs. full-feature models
- Expected performance: Slightly lower than full model but better than random/default

## 2.6 Research Gap Summary

### What Exists
✓ Predictive models for at-risk students (high accuracy)  
✓ XAI techniques for model interpretability  
✓ Educational chatbots (rule-based and generative)  
✓ Cold-start solutions (collaborative filtering, transfer learning)  
✓ Conceptual frameworks for prescriptive LA (Susnjak, 2023)  

### What's Missing (Our Contributions)
✗ **End-to-end implementation of prescriptive LA framework**  
✗ **Automated intervention via RAG-based chatbot**  
✗ **Integration of XAI with actionable prescriptions**  
✗ **Cold-start handler specifically for educational contexts**  
✗ **Dual-interface system (student + advisor perspectives)**  
✗ **Comprehensive evaluation of all components together**  

### Research Positioning

This dissertation fills the gap by:
1. Implementing Susnjak's PLAF framework end-to-end (first in literature)
2. Innovating with RAG chatbot for scalable, automated intervention
3. Solving cold-start problem with K-NN demographic approach
4. Evaluating complete system on real dataset (OULAD, 32,593 students)
5. Open-sourcing reproducible pipeline for research community

---

**Key References**:
- Susnjak (2023): Prescriptive Learning Analytics Framework
- Lundberg & Lee (2017): SHAP explanations
- Mothilal et al. (2020): DiCE counterfactuals
- Lewis et al. (2020): RAG architecture
- Kuzilek et al. (2017): OULAD dataset

**Research Questions Mapping**:
- RQ1 (Prediction) → Section 2.2 (ML approaches)
- RQ2 (XAI) → Section 2.3 (SHAP, Anchors, DiCE)
- RQ3 (RAG chatbot) → Section 2.4 (Conversational AI)
- RQ4 (Cold-start) → Section 2.5 (Cold-start solutions)

