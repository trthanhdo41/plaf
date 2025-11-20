# Chương 3: Công trình liên quan & Công nghệ (Related Work & Technology)

## 3.1. Các công trình nghiên cứu liên quan

### 3.1.1. Learning Analytics và Student At-Risk Prediction

**Kuzilek et al. (2017) - OULAD Dataset**
- **Đóng góp**: Công bố OULAD dataset với 32,593 sinh viên
- **Phương pháp**: Baseline models (Logistic Regression, Decision Trees)
- **Kết quả**: AUC 0.70-0.75
- **Hạn chế**: Không có explainability, không có intervention mechanism
- **Kế thừa**: Sử dụng OULAD dataset, cải thiện accuracy và thêm XAI + RAG

**Hlosta et al. (2017) - Early Prediction**
- **Đóng góp**: Dự đoán sớm trong tuần đầu tiên
- **Phương pháp**: Logistic Regression với temporal features
- **Kết quả**: AUC 0.70-0.80 trong first weeks
- **Hạn chế**: Accuracy thấp, không có actionable recommendations
- **Kế thừa**: Sử dụng ý tưởng early prediction, cải thiện bằng ensemble methods

**Waheed et al. (2020) - Deep Learning Approach**
- **Đóng góp**: Áp dụng LSTM cho sequential student data
- **Phương pháp**: Recurrent Neural Networks
- **Kết quả**: AUC 0.87
- **Hạn chế**: Black box, không explainable, không có intervention
- **Khác biệt**: Luận văn này ưu tiên interpretable models (CatBoost) với XAI

**Márquez-Vera et al. (2016) - SVM for Course Failure**
- **Đóng góp**: Sử dụng SVM cho dự đoán trượt môn
- **Phương pháp**: Support Vector Machines với RBF kernel
- **Kết quả**: Accuracy 85%
- **Hạn chế**: Khó giải thích, không scale tốt
- **So sánh**: Luận văn này đạt 95% accuracy với interpretable models

### 3.1.2. Explainable AI trong Giáo dục

**Lundberg & Lee (2017) - SHAP Framework**
- **Đóng góp**: Unified framework cho model interpretability
- **Lý thuyết**: Shapley values từ game theory
- **Ưu điểm**: Model-agnostic, theoretically grounded
- **Ứng dụng trong luận văn**: SHAP cho global + local explanations

**Mothilal et al. (2020) - DiCE Counterfactuals**
- **Đóng góp**: Diverse Counterfactual Explanations
- **Phương pháp**: Optimization-based counterfactual generation
- **Ưu điểm**: Actionable, diverse, feasible
- **Ứng dụng trong luận văn**: DiCE cho prescriptive recommendations

**Ribeiro et al. (2018) - Anchor Explanations**
- **Đóng góp**: High-precision local rules
- **Phương pháp**: IF-THEN rules với precision threshold
- **Ưu điểm**: Human-readable, interpretable
- **Ứng dụng trong luận văn**: Anchor cho local explanations

**Khosravi et al. (2022) - XAI in Education Review**
- **Đóng góp**: Systematic review của XAI applications trong giáo dục
- **Findings**: Majority of systems lack actionable explanations
- **Gap identified**: Need for integration of XAI with intervention systems
- **Luận văn này**: Fills gap bằng XAI-RAG integration

### 3.1.3. Conversational AI và Chatbots trong Giáo dục

**Graesser et al. (2004) - AutoTutor**
- **Đóng góp**: Rule-based intelligent tutoring system
- **Phương pháp**: Decision trees, keyword matching
- **Hạn chế**: Limited conversational ability, rigid responses
- **Khác biệt**: Luận văn này sử dụng generative AI (Gemini)

**Goel & Polepeddi (2016) - Jill Watson**
- **Đóng góp**: AI teaching assistant tại Georgia Tech
- **Phương pháp**: Retrieval-based chatbot
- **Kết quả**: Answered 97% of forum questions correctly
- **Hạn chế**: Template responses, không có personalization
- **Cải tiến**: Luận văn này sử dụng RAG với personalization

**Lewis et al. (2020) - RAG Architecture**
- **Đóng góp**: Retrieval-Augmented Generation framework
- **Phương pháp**: Retrieval + LLM generation
- **Ưu điểm**: Grounded responses, updatable knowledge
- **Ứng dụng trong luận văn**: RAG với FAISS + Gemini 2.5 Flash

**Kuhail et al. (2023) - Educational Chatbots Review**
- **Đóng góp**: Systematic review của chatbots trong giáo dục
- **Findings**: Most chatbots lack personalization và data-driven insights
- **Gap**: Integration với learning analytics systems
- **Luận văn này**: Integrates RAG chatbot với ML predictions + XAI

### 3.1.4. Prescriptive Learning Analytics

**Susnjak (2023) - PLAF Framework**
- **Đóng góp**: Conceptual framework cho Prescriptive Learning Analytics
- **8 Stages**: Data → Features → Models → XAI → Counterfactuals → Recommendations → Intervention → Monitoring
- **Hạn chế**: Chỉ là conceptual framework, không có implementation
- **Luận văn này**: **First complete implementation** của PLAF framework

**Viberg et al. (2018) - LA Adoption Review**
- **Đóng góp**: Review về adoption của Learning Analytics
- **Findings**: Gap giữa research và practice
- **Barriers**: Lack of actionable insights, scalability issues
- **Luận văn này**: Addresses barriers bằng automated intervention

**Ifenthaler & Yau (2020) - Utilising LA for Intervention**
- **Đóng góp**: Framework cho intervention strategies
- **Phương pháp**: Manual advisor-driven interventions
- **Hạn chế**: Không scale, không automated
- **Luận văn này**: Automates interventions qua RAG chatbot

### 3.1.5. Cold-Start Problem Solutions

**Kizilcec et al. (2013) - Demographic Prediction in MOOCs**
- **Đóng góp**: Sử dụng demographics cho early prediction
- **Phương pháp**: Logistic Regression với demographic features
- **Kết quả**: Moderate accuracy (70%)
- **Ứng dụng trong luận văn**: K-NN demographic approach

**Fernández-García et al. (2019) - Transfer Learning**
- **Đóng góp**: Transfer learning across courses
- **Phương pháp**: Train on one course, apply to another
- **Hạn chế**: Domain shift issues
- **Khác biệt**: Luận văn này sử dụng K-NN (simpler, more interpretable)

**Tinto (1975) - Student Integration Theory**
- **Đóng góp**: Theoretical foundation cho student retention
- **Key insight**: First weeks are critical for intervention
- **Implication**: Cold-start solution is essential
- **Luận văn này**: Enables day-1 intervention

---

## 3.2. Tổng quan công nghệ nền tảng

### 3.2.1. Machine Learning Frameworks

**Scikit-learn**
- **Mục đích**: ML utilities, preprocessing, evaluation
- **Ưu điểm**: 
  - Comprehensive, well-documented
  - Standardized API
  - CPU-efficient
- **Nhược điểm**: Không tối ưu cho large-scale data
- **Sử dụng trong luận văn**: Train-test split, metrics, preprocessing

**CatBoost**
- **Mục đích**: Gradient boosting cho categorical data
- **Ưu điểm**:
  - Automatic categorical encoding
  - Ordered boosting (giảm overfitting)
  - High accuracy
- **Nhược điểm**: Memory-intensive
- **Sử dụng trong luận văn**: **Primary ML model** (AUC 0.9848)

**XGBoost**
- **Mục đích**: Extreme Gradient Boosting
- **Ưu điểm**:
  - Fast training
  - Regularization built-in
  - Feature importance
- **Nhược điểm**: Cần extensive hyperparameter tuning
- **Sử dụng trong luận văn**: Baseline comparison

**LightGBM** (Considered but not used)
- **Lý do không chọn**: CatBoost performs better on OULAD

### 3.2.2. Explainability Libraries

**SHAP (SHapley Additive exPlanations)**
- **Version**: 0.41.0
- **Ưu điểm**:
  - TreeExplainer cho CatBoost (fast)
  - Comprehensive visualizations
  - Theoretically grounded
- **Sử dụng**: Global + local explanations

**DiCE-ML (Diverse Counterfactual Explanations)**
- **Version**: 0.9
- **Ưu điểm**:
  - Optimization-based
  - Feasibility constraints
  - Diverse scenarios
- **Sử dụng**: Prescriptive recommendations

**Alternatives Considered:**
- **LIME**: Less actionable, perturbation-based
- **Anchors**: Used for supplementary local rules
- **Chosen**: SHAP + DiCE for comprehensive XAI

### 3.2.3. Vector Search & Embeddings

**FAISS (Facebook AI Similarity Search)**
- **Version**: 1.7.4
- **Ưu điểm**:
  - Extremely fast similarity search
  - CPU and GPU support
  - Scalable to billions of vectors
- **Index type used**: IndexFlatL2 (exact search)
- **Sử dụng**: RAG retrieval

**Alternatives Considered:**
| Library | Pros | Cons | Decision |
|---------|------|------|----------|
| **FAISS** | Fast, scalable, CPU-efficient | Requires manual index management | ✅ **Chosen** |
| **Pinecone** | Managed service, easy to use | Cloud dependency, cost | ❌ Rejected |
| **Weaviate** | GraphQL API, hybrid search | Overhead for simple use case | ❌ Rejected |
| **ChromaDB** | Simple API, embedded | Less mature, slower | ❌ Rejected |

**Embedding Models:**
- **text-embedding-004** (Google): 768-dim vectors
- **Alternatives**: OpenAI embeddings (more expensive)

### 3.2.4. Large Language Models

**Google Gemini 2.5 Flash**
- **Ưu điểm**:
  - Fast (< 2s latency)
  - Cost-effective ($0.075/1M tokens)
  - Large context window (1M tokens)
  - Multimodal (future work)
- **Nhược điểm**: External API dependency
- **Sử dụng**: RAG response generation

**Alternatives Considered:**
| Model | Latency | Cost | Quality | Decision |
|-------|---------|------|---------|----------|
| **Gemini 2.5 Flash** | < 2s | $0.075/1M | High | ✅ **Chosen** |
| **GPT-4** | 5-10s | $30/1M | Highest | ❌ Too slow & expensive |
| **GPT-3.5-turbo** | 2-3s | $0.50/1M | Good | ❌ Slower than Gemini |
| **Claude 3** | 3-5s | $15/1M | High | ❌ More expensive |
| **Llama 3** | Variable | Free (self-host) | Good | ❌ Infrastructure overhead |

### 3.2.5. Backend Framework

**FastAPI**
- **Version**: 0.104.1
- **Ưu điểm**:
  - High performance (async support)
  - Auto-generated API docs (Swagger)
  - Type hints validation (Pydantic)
  - WebSocket support (for chatbot)
- **Nhược điểm**: None significant
- **Sử dụng**: REST API cho predictions, explanations, chatbot

**Alternatives:**
- **Flask**: Simpler but slower, no async
- **Django**: Too heavy for this use case
- **Chosen**: FastAPI for performance + developer experience

### 3.2.6. Frontend Framework

**React**
- **Version**: 18.2.0
- **Ưu điểm**:
  - Component-based architecture
  - Large ecosystem
  - Virtual DOM (performance)
- **Libraries used**:
  - **Recharts**: Data visualization
  - **Axios**: HTTP client
  - **React Router**: Navigation
- **Sử dụng**: Student portal + Advisor dashboard

**Streamlit** (Prototype)
- **Ưu điểm**: Rapid prototyping, Python-native
- **Nhược điểm**: Limited customization
- **Sử dụng**: Initial prototype, demo

### 3.2.7. Database

**PostgreSQL** (Production)
- **Version**: 15.0
- **Ưu điểm**:
  - ACID compliance
  - JSON support
  - Scalable
- **Schema**: Students, Assessments, Activities, VLE, Predictions

**SQLite** (Development/Demo)
- **Ưu điểm**: Zero-config, embedded
- **Nhược điểm**: Not for production scale
- **Sử dụng**: Local development, thesis demo

### 3.2.8. Data Processing

**Pandas**
- **Version**: 2.1.0
- **Sử dụng**: Data loading, feature engineering, aggregation

**NumPy**
- **Version**: 1.24.0
- **Sử dụng**: Numerical computations, z-score standardization

**Joblib**
- **Sử dụng**: Model serialization (save/load)

---

## 3.3. Lựa chọn giải pháp công nghệ

### 3.3.1. Tiêu chí lựa chọn

**1. Performance:**
- Latency < 2s cho chatbot responses
- Training time < 30 minutes cho ML models
- Dashboard load time < 3s

**2. Scalability:**
- Support 10,000+ students
- Concurrent users: 100+
- Vector search: millions of documents

**3. Cost:**
- Minimize cloud costs
- Prefer open-source
- LLM API cost < $10/month for demo

**4. Interpretability:**
- Explainable ML models
- Transparent decision-making
- Audit trail

**5. Developer Experience:**
- Good documentation
- Active community
- Type safety (Python type hints)

### 3.3.2. Biện luận lựa chọn ML Model

**Tại sao chọn CatBoost?**

**So sánh các thuật toán:**
| Model | AUC | Training Time | Interpretability | Categorical Handling |
|-------|-----|---------------|------------------|---------------------|
| **CatBoost** | **0.9848** | 15 min | High (SHAP) | **Automatic** |
| XGBoost | 0.9821 | 12 min | High (SHAP) | Manual encoding |
| Random Forest | 0.9756 | 20 min | Medium | Manual encoding |
| SVM | 0.9512 | 45 min | Low | Manual encoding |
| Logistic Regression | 0.8923 | 2 min | High | Manual encoding |

**Lý do chọn CatBoost:**
1. **Highest accuracy**: AUC 0.9848 (best among all)
2. **Automatic categorical encoding**: No need for manual encoding
3. **Ordered boosting**: Reduces overfitting
4. **SHAP support**: TreeExplainer works well
5. **Reasonable training time**: 15 minutes acceptable

**Trade-offs:**
- Memory usage cao hơn XGBoost (acceptable với modern hardware)
- Slightly slower training than XGBoost (nhưng accuracy cao hơn)

### 3.3.3. Biện luận lựa chọn RAG Stack

**Tại sao chọn FAISS + Gemini?**

**Retrieval: FAISS vs. Alternatives**
- **FAISS**: Fast, CPU-efficient, no cloud dependency
- **Pinecone**: Cloud-based, easier but costs $70/month
- **Decision**: FAISS cho control + cost savings

**LLM: Gemini vs. GPT-4**
- **Gemini 2.5 Flash**: < 2s latency, $0.075/1M tokens
- **GPT-4**: 5-10s latency, $30/1M tokens (400x more expensive)
- **Decision**: Gemini cho speed + cost

**Embedding: Google vs. OpenAI**
- **Google text-embedding-004**: Free with Gemini API
- **OpenAI text-embedding-3**: $0.13/1M tokens
- **Decision**: Google cho cost + integration

### 3.3.4. Biện luận lựa chọn Backend/Frontend

**Backend: FastAPI vs. Flask**
- **FastAPI**: Async, auto docs, type validation
- **Flask**: Simpler, synchronous
- **Decision**: FastAPI cho performance + developer experience

**Frontend: React vs. Streamlit**
- **React**: Full control, production-ready
- **Streamlit**: Rapid prototyping, limited customization
- **Decision**: React cho production, Streamlit cho prototype

**Database: PostgreSQL vs. MongoDB**
- **PostgreSQL**: Relational, ACID, SQL
- **MongoDB**: NoSQL, flexible schema
- **Decision**: PostgreSQL cho structured educational data

### 3.3.5. Architecture Decision Records

**ADR-001: Use CatBoost for ML Model**
- **Context**: Need high accuracy + interpretability
- **Decision**: CatBoost
- **Consequences**: Best accuracy, automatic categorical handling, SHAP support

**ADR-002: Use RAG instead of Fine-tuning**
- **Context**: Need grounded responses, easy updates
- **Decision**: RAG with FAISS + Gemini
- **Consequences**: No hallucination, updatable knowledge, lower cost

**ADR-003: Use SHAP + DiCE for XAI**
- **Context**: Need global + local + counterfactual explanations
- **Decision**: SHAP for importance, DiCE for counterfactuals
- **Consequences**: Comprehensive explainability, actionable insights

**ADR-004: Use K-NN for Cold-Start**
- **Context**: Need day-1 predictions for new students
- **Decision**: K-NN on demographics
- **Consequences**: Simple, interpretable, works from day 1

---

## 3.4. So sánh với các hệ thống hiện có

### 3.4.1. Commercial Learning Analytics Platforms

**Blackboard Analytics**
- **Features**: Dashboards, reports, basic predictions
- **Hạn chế**: No explainability, no automated intervention
- **Khác biệt**: Luận văn này có XAI + RAG chatbot

**Canvas Analytics**
- **Features**: Student activity tracking, at-risk flags
- **Hạn chế**: Generic advice, no personalization
- **Khác biệt**: Luận văn này có personalized RAG responses

**Civitas Learning**
- **Features**: Predictive models, intervention workflows
- **Hạn chế**: Manual advisor-driven, not automated
- **Khác biệt**: Luận văn này automates qua chatbot

### 3.4.2. Research Prototypes

**Student Explorer (University of Michigan)**
- **Features**: At-risk prediction, advisor dashboard
- **Hạn chế**: No explainability, no chatbot
- **Khác biệt**: Luận văn này có SHAP + DiCE + RAG

**Course Signals (Purdue University)**
- **Features**: Traffic light system (red/yellow/green)
- **Hạn chế**: Simple indicators, no detailed explanations
- **Khác biệt**: Luận văn này có detailed SHAP explanations

### 3.4.3. Positioning của Luận văn này

**Unique Contributions:**
1. **First complete PLAF implementation** (Susnjak, 2023)
2. **XAI-RAG integration**: SHAP/DiCE-enhanced chatbot
3. **Cold-start handler**: K-NN demographic approach
4. **Dual-interface**: Student + Advisor perspectives
5. **Open-source**: Reproducible on OULAD

**Comparison Table:**
| System | Prediction | XAI | Chatbot | Cold-Start | Open-Source |
|--------|------------|-----|---------|------------|-------------|
| **This Thesis** | ✅ 0.98 AUC | ✅ SHAP+DiCE | ✅ RAG | ✅ K-NN | ✅ Yes |
| Blackboard | ✅ Basic | ❌ No | ❌ No | ❌ No | ❌ No |
| Canvas | ✅ Basic | ❌ No | ❌ No | ❌ No | ❌ No |
| Civitas | ✅ Good | ⚠️ Limited | ❌ No | ❌ No | ❌ No |
| Student Explorer | ✅ Good | ❌ No | ❌ No | ❌ No | ⚠️ Limited |

---

**Tóm tắt Chương 3:**

Chương này đã trình bày:
1. **Công trình liên quan**: OULAD research, XAI in education, RAG chatbots, PLAF framework
2. **Công nghệ nền tảng**: ML frameworks, XAI libraries, vector search, LLMs, backend/frontend
3. **Lựa chọn công nghệ**: CatBoost (accuracy), FAISS+Gemini (RAG), FastAPI+React (web)
4. **Biện luận**: Performance, cost, interpretability, scalability
5. **So sánh**: Positioning với commercial platforms và research prototypes

**Điểm khác biệt chính:**
- First complete PLAF implementation
- XAI-RAG integration (novel)
- Cold-start solution
- Open-source, reproducible

Chương tiếp theo sẽ trình bày giải pháp đề xuất chi tiết.
