# Chương 2: Cơ sở lý thuyết (Theoretical Background)

## 2.1. Tổng quan về Learning Analytics

### 2.1.1. Định nghĩa Learning Analytics

**Learning Analytics** là quá trình đo lường, thu thập, phân tích và báo cáo dữ liệu về người học và bối cảnh học tập của họ, nhằm mục đích hiểu và tối ưu hóa quá trình học tập và môi trường mà nó diễn ra (Siemens & Long, 2011).

**Các đặc điểm chính:**
- **Data-driven**: Dựa trên dữ liệu thực tế từ hệ thống học tập
- **Actionable**: Cung cấp insights có thể hành động
- **Personalized**: Hỗ trợ cá nhân hóa trải nghiệm học tập
- **Predictive**: Dự đoán kết quả học tập trong tương lai

### 2.1.2. Các cấp độ phân tích

**1. Descriptive Analytics (Phân tích mô tả)**
- **Mục đích**: Hiểu "điều gì đã xảy ra"
- **Phương pháp**: Thống kê mô tả, dashboard, báo cáo
- **Ví dụ**: Điểm trung bình lớp, tỷ lệ hoàn thành khóa học
- **Hạn chế**: Chỉ nhìn lại quá khứ, không dự đoán

**2. Diagnostic Analytics (Phân tích chẩn đoán)**
- **Mục đích**: Hiểu "tại sao nó xảy ra"
- **Phương pháp**: Phân tích tương quan, nhận dạng mẫu
- **Ví dụ**: Tìm nguyên nhân sinh viên trượt môn
- **Hạn chế**: Giải thích quá khứ, không dự đoán tương lai

**3. Predictive Analytics (Phân tích dự đoán)**
- **Mục đích**: Dự đoán "điều gì sẽ xảy ra"
- **Phương pháp**: Machine Learning, Statistical modeling
- **Ví dụ**: Dự đoán sinh viên có nguy cơ bỏ học
- **Hạn chế**: Dự đoán mà không đề xuất hành động

**4. Prescriptive Analytics (Phân tích dự báo)**
- **Mục đích**: Đề xuất "nên làm gì"
- **Phương pháp**: Optimization, Simulation, XAI + Recommendations
- **Ví dụ**: Đề xuất chiến lược can thiệp cụ thể cho sinh viên
- **Đổi mới**: Khép kín vòng lặp từ insight đến hành động

### 2.1.3. PLAF Framework (Susnjak, 2023)

**Prescriptive Learning Analytics Framework** là khung phân tích học tập dự báo được đề xuất bởi Susnjak (2023), bao gồm 8 giai đoạn:

**Giai đoạn 1: Thu thập dữ liệu (Data Collection)**
- Tích hợp đa nguồn: LMS, SIS, external data
- Dữ liệu thô: demographics, VLE interactions, assessments

**Giai đoạn 2: Kỹ thuật đặc trưng (Feature Engineering)**
- Tạo các đặc trưng dự đoán từ dữ liệu thô
- Chuẩn hóa, xử lý missing values

**Giai đoạn 3: Mô hình dự đoán (Predictive Modeling)**
- Huấn luyện mô hình ML để dự đoán nguy cơ
- Đánh giá hiệu suất: AUC, F1-Score, Recall

**Giai đoạn 4: Giải thích mô hình (Explainability)**
- Sử dụng XAI để giải thích dự đoán
- SHAP, LIME, Anchors

**Giai đoạn 5: Phân tích phản thực (Counterfactual Analysis)**
- Tạo kịch bản "nếu...thì" để thay đổi kết quả
- DiCE counterfactual explanations

**Giai đoạn 6: Tạo khuyến nghị (Recommendation Generation)**
- Chuyển đổi insights thành lời khuyên hành động
- Cá nhân hóa theo từng sinh viên

**Giai đoạn 7: Phân phối can thiệp (Intervention Delivery)**
- Truyền đạt khuyến nghị đến stakeholders
- Email, dashboard, chatbot

**Giai đoạn 8: Giám sát kết quả (Outcome Monitoring)**
- Theo dõi hiệu quả can thiệp
- Cập nhật mô hình dựa trên feedback

**Khoảng trống trong framework gốc:**
- Susnjak chỉ đề xuất khung lý thuyết, chưa có triển khai đầy đủ
- Không có cơ chế can thiệp tự động (cần advisor thủ công)
- Không giải quyết vấn đề cold-start cho sinh viên mới
- **Luận văn này**: Triển khai đầy đủ với RAG chatbot tự động hóa

---

## 2.2. Machine Learning cho dự đoán sinh viên

### 2.2.1. Các thuật toán Machine Learning

**1. Decision Trees & Ensemble Methods**

**Random Forest (Breiman, 2001)**
- **Nguyên lý**: Tập hợp nhiều decision trees, voting để ra quyết định
- **Ưu điểm**: 
  - Robust to overfitting
  - Feature importance tự nhiên
  - Xử lý tốt dữ liệu phi tuyến
- **Nhược điểm**: Khó giải thích từng cây riêng lẻ
- **Ứng dụng**: Dự đoán dropout (Hellas et al., 2018)

**XGBoost (Chen & Guestrin, 2016)**
- **Nguyên lý**: Gradient boosting với regularization
- **Ưu điểm**:
  - Xử lý tốt dữ liệu mất cân bằng
  - Tốc độ nhanh, hiệu suất cao
  - Built-in feature importance
- **Nhược điểm**: Nhiều hyperparameters cần tuning
- **Ứng dụng**: Student performance prediction

**CatBoost (Prokhorenkova et al., 2018)**
- **Nguyên lý**: Categorical boosting với ordered boosting
- **Ưu điểm**:
  - Xử lý tự động categorical features
  - Giảm overfitting qua ordered boosting
  - Không cần extensive preprocessing
- **Nhược điểm**: Tốn bộ nhớ hơn XGBoost
- **Ứng dụng**: **Được chọn làm mô hình chính trong luận văn này**

**2. Support Vector Machines (SVM)**
- **Nguyên lý**: Tìm siêu phẳng phân tách tối ưu (maximum margin)
- **Kernel methods**: RBF, polynomial để xử lý phi tuyến
- **Ưu điểm**: Hiệu quả với dữ liệu chiều cao
- **Nhược điểm**: 
  - Khó giải thích
  - Tốn tính toán với dataset lớn
- **Ứng dụng**: Course failure prediction (Márquez-Vera et al., 2016)

**3. Logistic Regression**
- **Nguyên lý**: Mô hình tuyến tính với sigmoid activation
- **Ưu điểm**:
  - Giải thích dễ (coefficients)
  - Output xác suất trực tiếp
  - Baseline tốt
- **Nhược điểm**: Giả định tuyến tính, kém với dữ liệu phức tạp
- **Ứng dụng**: MOOCs dropout prediction (Xing et al., 2016)

**4. Deep Learning (Tham khảo)**
- **Neural Networks, LSTMs**: Cho dữ liệu sequential
- **Ưu điểm**: Độ chính xác cao với dữ liệu lớn
- **Nhược điểm**: "Black box", khó giải thích
- **Hạn chế**: Ít được áp dụng trong giáo dục do yêu cầu interpretability

### 2.2.2. Feature Engineering trong giáo dục

**1. Demographic Features (Đặc trưng nhân khẩu học)**
- **Các đặc trưng**: Age, gender, socioeconomic status (IMD band), prior education
- **Tính chất**: Predictive nhưng **immutable** (không thể thay đổi bằng can thiệp)
- **Vai trò**: Dùng cho cold-start prediction, không dùng cho counterfactuals

**2. Behavioral Features (Đặc trưng hành vi)**
- **VLE Engagement**: 
  - `total_clicks`: Tổng số lần tương tác với VLE
  - `num_days_active`: Số ngày có hoạt động
  - `avg_clicks_per_day`: Trung bình clicks mỗi ngày
  - `resource_diversity`: Đa dạng tài liệu truy cập
- **Assessment Performance**:
  - `avg_score`: Điểm trung bình
  - `score_std`: Độ biến động điểm số
  - `submission_rate`: Tỷ lệ nộp bài
  - `num_late_submissions`: Số bài nộp trễ
- **Tính chất**: Highly predictive và **actionable** (có thể can thiệp)

**3. Temporal Features (Đặc trưng thời gian)**
- **Early vs. Late patterns**: Nộp bài sớm/trễ
- **Trajectory**: Xu hướng engagement theo thời gian
- **Critical**: Dự đoán sớm cần features có sẵn trong tuần đầu

**4. Derived Features (Đặc trưng dẫn xuất)**
- **Study Intensity**: Kết hợp score và clicks
- **Engagement Consistency**: Độ đều đặn của hoạt động
- **Resource Diversity**: Breadth of learning materials

### 2.2.3. Z-score Standardization

**Tại sao cần chuẩn hóa?**
- Các features có scale khác nhau (clicks: 0-10000, scores: 0-100)
- ML models nhạy cảm với scale (SVM, Logistic Regression)
- So sánh công bằng giữa các cohorts

**Z-score Formula:**
```
z = (x - μ) / σ
```
Trong đó:
- `x`: Giá trị gốc
- `μ`: Mean của cohort (module + presentation)
- `σ`: Standard deviation của cohort

**Standardization by Cohort:**
- **Tại sao by cohort?**: Các modules khác nhau có độ khó khác nhau
- **Cohort definition**: `code_module` + `code_presentation`
- **Ví dụ**: Sinh viên Module AAA 2013J được so sánh với peers trong cùng cohort

**Implementation:**
```python
# Ví dụ: Chuẩn hóa avg_score
cohort_mean = df.groupby(['code_module', 'code_presentation'])['avg_score'].mean()
cohort_std = df.groupby(['code_module', 'code_presentation'])['avg_score'].std()
df['avg_score_z'] = (df['avg_score'] - cohort_mean) / cohort_std
```

---

## 2.3. Explainable AI (XAI)

### 2.3.1. Tại sao cần XAI trong giáo dục?

**Bối cảnh quyết định quan trọng (High-Stakes Decisions):**
- Sinh viên có quyền hiểu tại sao bị dự đoán có nguy cơ (GDPR, FERPA)
- Giảng viên cần tin tưởng và hành động dựa trên AI recommendations
- Trách nhiệm giải trình của tổ chức giáo dục
- Đạo đức: Tránh "black box" discrimination

**Yêu cầu pháp lý:**
- **GDPR (EU)**: Right to explanation
- **FERPA (US)**: Student data privacy
- **Transparency**: Giải thích rõ ràng quyết định AI

### 2.3.2. SHAP (SHapley Additive exPlanations)

**Nền tảng lý thuyết:**
- Lundberg & Lee (2017): Unified framework for interpretability
- **Game theory**: Shapley values từ cooperative game theory
- **Fair attribution**: Phân bổ công bằng đóng góp của features

**Shapley Value Formula:**
```
φᵢ = Σ [|S|!(|F|-|S|-1)! / |F|!] × [f(S∪{i}) - f(S)]
```
Trong đó:
- `φᵢ`: SHAP value của feature i
- `S`: Subset của features
- `F`: Tập tất cả features
- `f(S)`: Prediction với feature subset S

**TreeExplainer cho Ensemble Models:**
- Tối ưu cho CatBoost, XGBoost, Random Forest
- Complexity: O(TLD²) với T=trees, L=leaves, D=depth
- Nhanh hơn KernelExplainer

**Ứng dụng trong luận văn:**
- **Global Importance**: Top 10 features quan trọng nhất
- **Local Explanations**: Giải thích từng sinh viên
- **Visualization**: Summary plot, waterfall plot, force plot

**Ưu điểm:**
- Model-agnostic (áp dụng cho mọi model)
- Theoretically grounded (game theory)
- Consistent feature attributions

**Nhược điểm:**
- Computational cost cao
- Cần background data sample
- Approximations cho feature space lớn

### 2.3.3. DiCE (Diverse Counterfactual Explanations)

**Counterfactual Reasoning:**
- Mothilal et al. (2020): Giải thích phản thực đa dạng
- **Câu hỏi**: "Thay đổi gì để flip prediction từ at-risk → safe?"
- **Ví dụ**: "Tăng VLE clicks 50% VÀ cải thiện điểm 15 points"

**Tại sao DiCE cho giáo dục?**
- **Actionable**: Chỉ ra điều sinh viên có thể thay đổi
- **Diverse**: Nhiều con đường đến thành công (không one-size-fits-all)
- **Feasible**: Ràng buộc thay đổi thực tế (không thể thay đổi demographics)

**Optimization Problem:**
```
minimize: distance(x, x') + λ × diversity(CF_set)
subject to: 
  - f(x') = desired_class
  - x'ᵢ ∈ feasible_range(xᵢ) for actionable features
  - x'ⱼ = xⱼ for immutable features
```

**Feasibility Constraints:**
- **Immutable features**: gender, region, age_band, num_prev_attempts
- **Actionable features**: VLE engagement, assessment scores
- **Realistic ranges**: 
  - `avg_score`: Chỉ tăng (1.0-1.5x)
  - `total_clicks`: Tăng tối đa 2x
  - `papers_failed`: Giảm về 0

**Implementation:**
```python
# Ví dụ: Tạo counterfactuals
dice_exp = explainer.generate_counterfactuals(
    query_instance=student_features,
    total_CFs=3,  # 3 diverse scenarios
    desired_class=0,  # Safe
    features_to_vary=['total_clicks_z', 'avg_score_z'],  # Actionable only
    permitted_range={'avg_score_z': [current, current*1.5]}
)
```

**So sánh với LIME:**
- **LIME**: Perturbation-based, less actionable
- **DiCE**: Optimization-based, directly actionable
- **Chọn DiCE**: Vì tính actionability cao hơn

---

## 2.4. Retrieval-Augmented Generation (RAG)

### 2.4.1. Vấn đề với LLMs thuần túy

**Hallucination Problem:**
- LLMs có thể tạo thông tin sai lệch
- Không grounded in facts
- Nguy hiểm trong giáo dục (lời khuyên sai)

**Knowledge Cutoff:**
- LLMs chỉ biết đến thời điểm training
- Không biết course materials mới
- Không biết student-specific data

**Lack of Control:**
- Khó kiểm soát response quality
- Không thể update knowledge dễ dàng

### 2.4.2. RAG Architecture

**Định nghĩa (Lewis et al., 2020):**
RAG = Retrieval + Generation
- **Retrieval**: Tìm kiếm thông tin relevant từ knowledge base
- **Generation**: LLM tạo response dựa trên retrieved context

**Kiến trúc 3 giai đoạn:**

**1. Indexing (Offline)**
```
Documents → Chunking → Embedding → Vector Store (FAISS)
```
- **Chunking**: Chia documents thành chunks nhỏ
- **Embedding**: Chuyển text → vectors (768-dim)
- **FAISS**: Facebook AI Similarity Search (vector database)

**2. Retrieval (Runtime)**
```
Query → Embedding → Similarity Search → Top-k Documents
```
- **Query embedding**: Chuyển câu hỏi → vector
- **Cosine similarity**: Tìm documents gần nhất
- **Top-k**: Lấy k documents relevant nhất (k=3-5)

**3. Generation (Runtime)**
```
Query + Retrieved Context + Student Profile → LLM → Response
```
- **Prompt engineering**: Kết hợp query, context, student info
- **LLM**: Gemini 2.5 Flash (fast, cost-effective)
- **Response**: Personalized, grounded answer

**Ưu điểm RAG:**
- **Grounding**: Responses dựa trên verified knowledge
- **Controllability**: Retrieval đảm bảo relevance
- **Updatability**: Thêm documents mới không cần retrain LLM
- **Transparency**: Có thể show sources

**So sánh với Fine-tuning:**
| Aspect | RAG | Fine-tuning |
|--------|-----|-------------|
| Training data | Không cần | Cần dataset lớn |
| Update knowledge | Dễ (add docs) | Khó (retrain) |
| Computational cost | Thấp | Cao |
| Transparency | Cao (show sources) | Thấp |

### 2.4.3. FAISS Vector Search

**Facebook AI Similarity Search:**
- Open-source library cho similarity search
- Tối ưu cho billions of vectors
- CPU và GPU support

**Index Types:**
- **IndexFlatL2**: Exact search, tốt cho < 1M vectors
- **IndexIVFFlat**: Approximate search, nhanh hơn
- **IndexHNSW**: Hierarchical Navigable Small World, tốt nhất

**Similarity Metrics:**
- **L2 distance**: Euclidean distance
- **Cosine similarity**: Góc giữa vectors
- **Inner product**: Dot product

**Implementation:**
```python
import faiss
import numpy as np

# Create index
dimension = 768  # Embedding dimension
index = faiss.IndexFlatL2(dimension)

# Add vectors
embeddings = np.array(document_embeddings).astype('float32')
index.add(embeddings)

# Search
query_vector = np.array([query_embedding]).astype('float32')
distances, indices = index.search(query_vector, k=5)
```

### 2.4.4. Gemini 2.5 Flash

**Tại sao chọn Gemini 2.5 Flash?**
- **Speed**: < 2s latency (nhanh hơn GPT-4)
- **Cost**: $0.075/1M tokens (rẻ hơn GPT-4)
- **Quality**: Comparable với GPT-3.5-turbo
- **Context window**: 1M tokens (lớn)
- **Multimodal**: Text, image, video (future work)

**Embedding Model:**
- **text-embedding-004**: 768-dim vectors
- **Task types**: retrieval_document, retrieval_query
- **Performance**: Tốt cho semantic search

---

## 2.5. Các độ đo đánh giá

### 2.5.1. Metrics cho Classification

**Confusion Matrix:**
```
                Predicted
                Safe    At-Risk
Actual Safe     TN      FP
       At-Risk  FN      TP
```

**Accuracy:**
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```
- **Ý nghĩa**: Tỷ lệ dự đoán đúng tổng thể
- **Hạn chế**: Không tốt với imbalanced data

**Precision:**
```
Precision = TP / (TP + FP)
```
- **Ý nghĩa**: Trong số dự đoán at-risk, bao nhiêu % đúng?
- **Quan trọng**: Giảm false alarms

**Recall (Sensitivity):**
```
Recall = TP / (TP + FN)
```
- **Ý nghĩa**: Trong số thực tế at-risk, phát hiện được bao nhiêu %?
- **Quan trọng nhất trong giáo dục**: Không bỏ sót sinh viên có nguy cơ

**F1-Score:**
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```
- **Ý nghĩa**: Trung bình điều hòa của Precision và Recall
- **Khi nào dùng**: Cân bằng giữa precision và recall

**AUC-ROC:**
- **ROC Curve**: True Positive Rate vs. False Positive Rate
- **AUC**: Area Under the Curve (0-1)
- **Ý nghĩa**: Khả năng phân biệt giữa 2 classes
- **Threshold-independent**: Đánh giá model tổng thể

### 2.5.2. Cost-Benefit Analysis trong giáo dục

**False Negative (FN) - Bỏ sót sinh viên có nguy cơ:**
- **Cost**: Rất cao (sinh viên dropout, mất học phí, ảnh hưởng career)
- **Priority**: Minimize FN rate

**False Positive (FP) - Cảnh báo nhầm:**
- **Cost**: Thấp (sinh viên nhận hỗ trợ không cần thiết)
- **Acceptable**: FP rate cao hơn FN rate

**Optimal Threshold:**
- Không phải 0.5 mặc định
- Điều chỉnh để minimize FN (e.g., threshold = 0.3)
- Trade-off: Tăng recall, giảm precision

### 2.5.3. Metrics cho RAG System

**Retrieval Quality:**
- **Relevance@k**: Tỷ lệ documents relevant trong top-k
- **MRR (Mean Reciprocal Rank)**: 1/rank của document đầu tiên relevant
- **NDCG (Normalized Discounted Cumulative Gain)**: Ranking quality

**Generation Quality:**
- **Perplexity**: Độ "ngạc nhiên" của model (thấp = tốt)
- **BLEU/ROUGE**: So sánh với reference answers (nếu có)
- **Human evaluation**: Relevance, Actionability, Empathy (1-5 scale)

**System Metrics:**
- **Latency**: Thời gian response (< 2s target)
- **Throughput**: Số queries/second
- **Cost**: $/1000 queries

---

**Tóm tắt Chương 2:**

Chương này đã trình bày nền tảng lý thuyết cho hệ thống PLAF:
1. **Learning Analytics**: Từ descriptive → prescriptive, PLAF framework
2. **Machine Learning**: CatBoost, XGBoost, RF, SVM, Logistic Regression
3. **Feature Engineering**: Demographic, behavioral, temporal features, z-score standardization
4. **Explainable AI**: SHAP (feature importance), DiCE (counterfactuals)
5. **RAG**: Retrieval + Generation, FAISS, Gemini 2.5 Flash
6. **Evaluation Metrics**: Accuracy, Precision, Recall, F1, AUC, cost-benefit analysis

Chương tiếp theo sẽ trình bày các công trình liên quan và lựa chọn công nghệ.
