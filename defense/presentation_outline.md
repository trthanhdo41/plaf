# PhD Defense Presentation Outline

## Presentation Overview
- **Duration**: 20-30 minutes + Q&A
- **Slides**: 26 slides
- **Audience**: AI/Computer Science focused committee
- **Format**: Live demo + pre-recorded video backup

---

## Slide Structure

### Opening (3 slides, 2 minutes)

**Slide 1: Title Slide**
```
Prescriptive Learning Management System (PLMS)
Design, Implementation, and Evaluation of an AI-Powered 
Student Support System

PhD Defense
[Your Name]
[Date]
[University]
```

**Slide 2: Agenda**
```
Today's Presentation
• Research Problem & Motivation
• System Architecture & Design  
• Key Technical Contributions
• Experimental Results
• Live System Demonstration
• Research Contributions
• Questions & Discussion
```

**Slide 3: Research Motivation**
```
The Challenge: Student Dropout Crisis
• 30-50% university dropout rates globally
• $16.5B annual cost to US economy
• Critical intervention window: first semester

Current Gap: Prediction Without Action
• Most LA systems stop at identifying at-risk students
• Manual intervention bottleneck (advisors overwhelmed)
• No 24/7 support for "crisis moments"
• Generic advice doesn't address individual contexts
```

### Background (3 slides, 3 minutes)

**Slide 4: Learning Analytics Evolution**
```
Learning Analytics Framework
Descriptive → Diagnostic → Predictive → Prescriptive

Current State: Most systems stop here
• High prediction accuracy (AUC > 0.90)
• But no automated intervention

Our Goal: Complete the loop
• Predict → Explain → Prescribe → Intervene
```

**Slide 5: Research Gap**
```
What's Missing?
✗ End-to-end prescriptive LA implementation
✗ Automated empathetic intervention
✗ Cold-start solution for new students  
✗ Integration of XAI with actionable prescriptions

Our Solution: PLMS
✓ Complete PLAF framework implementation
✓ RAG-based chatbot for 24/7 support
✓ Demographic K-NN for immediate intervention
✓ Multi-level explainability (SHAP + DiCE + Anchors)
```

**Slide 6: Research Questions**
```
RQ1: How accurately can ML models predict at-risk students?
RQ2: How can XAI make predictions actionable?
RQ3: How effective is RAG chatbot for intervention?
RQ4: How to handle cold-start problem for new students?
```

### System Overview (2 slides, 2 minutes)

**Slide 7: PLMS Architecture**
```
8-Stage Pipeline
┌─────────────────────────────────────────────────┐
│ Data → Features → Models → XAI → Prescriptive → │
│     → Chatbot → Dashboard → LMS Integration     │
└─────────────────────────────────────────────────┘

Technology Stack:
• ML: CatBoost, Random Forest, XGBoost, SVM, LR
• XAI: SHAP, DiCE, Anchors  
• AI: FAISS + Gemini 2.5 Flash
• UI: Streamlit (Student + Advisor portals)
• Data: OULAD (32,593 students)
```

**Slide 8: Key Innovations**
```
1. RAG Chatbot Integration
   • FAISS vector search + Gemini generation
   • Personalized, empathetic responses
   • 24/7 availability

2. Cold-Start Handler  
   • K-NN on demographics (6 features)
   • Immediate predictions for new students
   • Confidence scoring

3. Multi-Level XAI
   • Global: SHAP feature importance
   • Local: Anchor rules  
   • Counterfactual: DiCE "what-if" scenarios
```

### Methodology (6 slides, 6 minutes)

**Slide 9: OULAD Dataset**
```
Open University Learning Analytics Dataset
• 32,593 students across 7 modules
• 7 data tables: demographics, VLE, assessments
• Target: Binary at-risk classification
• Train/Test: 80/20 stratified split

Feature Engineering: 25 features
• Demographics (6 immutable)
• VLE behavior (10 actionable)  
• Assessment performance (9 actionable)
• Z-score standardization
```

**Slide 10: Predictive Models**
```
5 ML Algorithms with 5-Fold CV
• CatBoost (Primary)
• Random Forest
• XGBoost  
• SVM
• Logistic Regression

Evaluation Metrics:
• AUC, F1, Precision, Recall, Accuracy
• Training time, inference latency
• Statistical significance testing
```

**Slide 11: Cold-Start Solution**
```
Problem: New students have no VLE/assessment history
Solution: K-Nearest Neighbors on Demographics

Algorithm:
1. Encode 6 demographic features
2. Find k=10 most similar historical students  
3. Weighted risk prediction
4. Confidence score (inverse distance)

Features: gender, region, education, IMD, age, disability
```

**Slide 12: XAI Implementation**
```
Multi-Level Explainability

SHAP (Global & Local):
• TreeExplainer for ensemble models
• Feature importance ranking
• Individual student explanations

DiCE (Counterfactual):
• "What changes would make you safe?"
• Feasibility constraints (immutable vs actionable)
• Multiple pathways to success

Anchors (Rules):
• "IF condition1 AND condition2 THEN at-risk"
• Human-readable decision boundaries
```

**Slide 13: RAG Chatbot System**
```
Architecture:
Query → Embedding → FAISS Retrieval → Gemini Generation → Response

Knowledge Base:
• OULAD course content
• Learning strategies & study tips
• Best practices for online learning

Personalization:
• Student profile injection
• Risk level awareness
• Course context integration
```

**Slide 14: Dual Interface Design**
```
Student Portal:
• Risk dashboard with SHAP explanations
• Course materials with activity tracking
• AI chatbot for personalized support

Advisor Dashboard:  
• At-risk student list with risk scores
• SHAP plots and DiCE counterfactuals
• Chat history monitoring
• Intervention planning tools
```

### Results (5 slides, 5 minutes)

**Slide 15: Predictive Performance**
```
Model Comparison (Test Set)
┌─────────────┬────────┬──────┬──────────┬────────┐
│ Model       │ AUC    │ F1   │ Precision│ Recall │
├─────────────┼────────┼──────┼──────────┼────────┤
│ CatBoost    │ 0.9830 │0.7812│  0.8123  │0.7534  │
│ RandomForest│ 0.9754 │0.7654│  0.7989  │0.7345  │
│ XGBoost     │ 0.9721 │0.7623│  0.7856  │0.7412  │
│ SVM         │ 0.9654 │0.7456│  0.7734  │0.7198  │
│ LogReg      │ 0.9234 │0.6987│  0.7123  │0.6856  │
└─────────────┴────────┴──────┴──────────┴────────┘

CatBoost: Best performance, selected for production
```

**Slide 16: Cold-Start Evaluation**
```
New Student Prediction Performance
┌─────────────┬────────┬────────┬──────────┐
│ Method      │ MAE    │ RMSE   │ Accuracy │
├─────────────┼────────┼────────┼──────────┤
│ Cold-Start  │ 0.234  │ 0.312  │  71.2%   │
│ Default     │ 0.342  │ 0.423  │  50.0%   │
│ Random      │ 0.498  │ 0.707  │  50.0%   │
│ Full Model  │ 0.156  │ 0.198  │  85.6%   │
└─────────────┴────────┴────────┴──────────┘

Significant improvement over baselines
Enables immediate intervention from day 1
```

**Slide 17: XAI Insights**
```
Top 5 Most Important Features (SHAP)
1. avg_assessment_score_z: -0.42 (low scores increase risk)
2. total_vle_clicks_z: -0.35 (low engagement increases risk)  
3. early_submission_rate_z: -0.28 (late submissions increase risk)
4. papers_failed_z: +0.25 (failures increase risk)
5. vle_activity_diversity_z: -0.22 (narrow activity increases risk)

Key Insight: Behavioral features > Demographics
DiCE Success Rate: 94.2% (found feasible alternatives)
```

**Slide 18: RAG System Quality**
```
RAG Evaluation Results
┌─────────────────┬──────────┬─────────────┐
│ Metric          │ Score    │ Target      │
├─────────────────┼──────────┼─────────────┤
│ Retrieval Relev │ 0.825    │ >0.70 ✓    │
│ Response Quality│ 0.816    │ >0.75 ✓    │
│ End-to-End Time │ 1.279s   │ <3.0s ✓    │
│ Personalization │ 0.834    │ >0.75 ✓    │
└─────────────────┴──────────┴─────────────┘

User Satisfaction: 78% find advice helpful
84% would use system again
```

**Slide 19: LLM Advice Quality**
```
Advice Quality Dimensions
┌─────────────────┬──────────┬─────────────┐
│ Dimension       │ Score    │ Interpretation│
├─────────────────┼──────────┼─────────────┤
│ Specificity     │ 0.823    │ Contains numbers│
│ Actionability   │ 0.856    │ Concrete steps│
│ Relevance       │ 0.901    │ Matches context│
│ Personalization │ 0.834    │ Uses student info│
│ Encouragement   │ 0.798    │ Positive tone │
│ Consistency     │ 0.867    │ Stable across runs│
└─────────────────┴──────────┴─────────────┘

Overall Quality: 0.842 (target >0.75 ✓)
```

### Live Demo/Video (1 slide, 3-5 minutes)

**Slide 20: System Demonstration**
```
Live Demo: PLMS in Action

1. Student Portal (2 min)
   • Login as high-risk student (risk=0.78)
   • Dashboard: grades, VLE activity, SHAP explanation
   • Course materials with activity tracking

2. RAG Chatbot (2 min)  
   • Student: "I'm struggling with grades, help!"
   • Show RAG retrieval (3 relevant strategies)
   • Gemini generates personalized, empathetic response
   • Specific advice: "Increase VLE to 250 clicks/week"

3. Advisor Dashboard (1 min)
   • At-risk student list with risk scores
   • Select student → SHAP plot + DiCE counterfactuals
   • View chat history, create intervention plan

[Pre-recorded video backup ready]
```

### Discussion (3 slides, 3 minutes)

**Slide 21: Key Findings**
```
Research Questions Answered
✓ RQ1: CatBoost achieves AUC=0.983 (excellent prediction)
✓ RQ2: Multi-level XAI enables actionable insights
✓ RQ3: RAG chatbot provides effective 24/7 intervention  
✓ RQ4: Cold-start handler enables immediate support

Key Insight: Complete prescriptive LA pipeline works!
High accuracy + Explainability + Automated intervention = Effective PLMS
```

**Slide 22: Limitations & Future Work**
```
Current Limitations
• Single institution dataset (OULAD from Open University UK)
• 2013-2014 data may not reflect current practices
• LLM dependency (API costs, privacy concerns)
• 14.4% accuracy gap for cold-start vs full model

Future Directions
• Multi-modal learning (text, video, social data)
• Reinforcement learning for adaptive interventions
• Multi-institution validation
• Long-term outcome studies
```

**Slide 23: Ethical Considerations**
```
Responsible AI in Education
• Algorithmic bias: Regular auditing across demographics
• Privacy: GDPR/FERPA compliance, student consent
• Transparency: Explainable decisions, student access to data
• Human oversight: AI augments, doesn't replace advisors

Student Agency: Opt-out options, human advisor alternatives
Institutional responsibility: Regular bias audits, outcome monitoring
```

### Contributions & Future Work (2 slides, 2 minutes)

**Slide 24: Novel Contributions**
```
1. Complete PLAF Implementation
   • First end-to-end implementation of Susnjak's framework
   • 8-stage pipeline on 32,593 students

2. RAG Innovation for Education  
   • FAISS + Gemini integration for personalized support
   • 24/7 empathetic intervention at scale

3. Cold-Start Solution
   • Demographic K-NN for immediate new student support
   • 71.2% accuracy vs 50% baseline

4. Multi-Level XAI
   • SHAP + DiCE + Anchors for comprehensive interpretability
   • Actionable insights for students and educators
```

**Slide 25: Future Research Directions**
```
Technical Enhancements
• Multi-modal learning (assignment text, forum posts)
• Federated learning for multi-institution deployment
• Real-time model adaptation

Educational Applications  
• Longitudinal intervention effectiveness studies
• Peer support integration
• Curriculum optimization using system insights

Societal Impact
• Equity and access research
• Global deployment across cultures
• Policy frameworks for AI in education
```

### Closing (1 slide)

**Slide 26: Thank You**
```
Thank You!

Questions & Discussion

Contact: [your.email@university.edu]
Repository: https://github.com/trthanhdo41/plaf
Demo: Available for hands-on exploration

The future of learning analytics:
From prediction to prescription through intelligent automation
```

---

## Presentation Guidelines

### Design Principles
- **University template**: Use your institution's slide template
- **Color scheme**: Blue primary, green for safe/red for at-risk
- **Font size**: Minimum 18pt for readability
- **Diagrams**: Clear architecture flow, minimal text
- **Code**: Only show key algorithms (cold-start, RAG)
- **Results**: Color-coded tables, highlight best values

### Timing Strategy
- **Opening (2 min)**: Set context quickly
- **Background (3 min)**: Establish research gap
- **System (2 min)**: High-level architecture
- **Methodology (6 min)**: Technical details for CS audience
- **Results (5 min)**: Evidence-based conclusions
- **Demo (3-5 min)**: Show working system
- **Discussion (3 min)**: Limitations and implications
- **Contributions (2 min)**: Novel contributions
- **Closing (1 min)**: Thank you and Q&A

### Demo Preparation
- **Test equipment**: Verify laptop/projector compatibility
- **Backup video**: 5-minute pre-recorded walkthrough ready
- **Test data**: Compelling student profiles with varying risk levels
- **Internet**: Check API connectivity for Gemini
- **Fallback**: Screenshots if both demo and video fail

### Q&A Strategy
- **Listen fully**: Wait for complete question before answering
- **Use whiteboard**: For technical explanations if available
- **Refer to slides**: "As shown in slide 15..."
- **Acknowledge limitations**: "That's a valid concern..."
- **Evidence-based**: Support answers with evaluation results

---

## Backup Materials

### Additional Slides (if needed)
- **Detailed algorithm pseudocode**
- **More evaluation metrics**
- **User study details**
- **Comparison with commercial systems**
- **Cost-benefit analysis**

### Technical Deep Dive
- **Code walkthrough**: Key functions in `src/`
- **Configuration**: `config/config.yaml` parameters
- **Benchmark results**: Detailed performance tables
- **Architecture decisions**: Why CatBoost, FAISS, Gemini?

### Evaluation Details
- **Statistical tests**: Significance testing results
- **Ablation studies**: Component impact analysis
- **User feedback**: Qualitative comments from students/advisors
- **Error analysis**: Where the system fails and why
