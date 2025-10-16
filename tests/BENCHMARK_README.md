# PLAF Benchmark Suite

Comprehensive benchmarking suite for evaluating all components of the PLAF system.

## What Gets Benchmarked

### 1. **Predictive Models Benchmark** (`benchmark_predictive.py`)
Evaluates all ML models for student at-risk prediction:
- **Models tested**: CatBoost, Random Forest, XGBoost, SVM, Logistic Regression
- **Metrics**:
  - Cross-validation AUC (5-fold)
  - Test set: Accuracy, Precision, Recall, F1-Score, AUC
  - Training time, prediction time
  - Confusion matrix, classification report
- **Output**: Comparison table ranking models by performance

### 2. **RAG System Benchmark** (`benchmark_rag.py`)
Evaluates the chatbot's RAG (Retrieval-Augmented Generation) system:
- **Retrieval Quality**:
  - Relevance of retrieved documents
  - Retrieval time per query
- **Response Quality**:
  - Context accuracy
  - Personalization
  - Response completeness
- **End-to-End Latency**:
  - Full query → response time
- **Test Cases**: 8 different question types (academic advice, concept explanation, time management, etc.)

### 3. **LLM Advice Benchmark** (`benchmark_llm.py`)
Evaluates quality of AI-generated advice for at-risk students:
- **Quality Metrics**:
  - Specificity (contains actual numbers/goals)
  - Actionability (has concrete steps)
  - Relevance (mentions engagement, grades)
  - Personalization
  - Encouragement tone
  - Readability
- **Consistency**: Tests if advice is consistent across multiple runs
- **Relevance**: Checks if advice matches student's risk level
- **Response Time**: Measures generation latency

## How to Run

### Prerequisites

1. **Install dependencies**:
```bash
pip install pandas numpy scikit-learn catboost xgboost google-generativeai
```

2. **Set up data**:
```bash
# Generate modeling data first
python run_pipeline.py
```

3. **Set API key** (for LLM benchmark):
```bash
export GEMINI_API_KEY=your_api_key_here
```

### Run Individual Benchmarks

#### Predictive Models
```bash
python tests/benchmark_predictive.py
```

**Output**: 
- Console: Model comparison table
- File: `results/predictive_benchmark_YYYYMMDD_HHMMSS.csv`

#### RAG System
```bash
python tests/benchmark_rag.py
```

**Output**:
- Console: Retrieval relevance, response quality, latency metrics
- File: `results/rag_benchmark_YYYYMMDD_HHMMSS.json`

#### LLM Advice
```bash
python tests/benchmark_llm.py
```

**Output**:
- Console: Quality, consistency, relevance scores
- File: `results/llm_benchmark_YYYYMMDD_HHMMSS.json`

### Run All Benchmarks

Run the comprehensive benchmark suite:

```bash
python run_all_benchmarks.py
```

This will:
1. Run all 3 benchmarks sequentially
2. Generate a comprehensive report
3. Save results to `results/comprehensive_benchmark_YYYYMMDD_HHMMSS.json`

**Estimated time**: 15-30 minutes

## Understanding Results

### Predictive Models

**Good scores**:
- AUC: > 0.80 (excellent), > 0.70 (good)
- F1-Score: > 0.75 (good balance of precision/recall)
- Precision: > 0.80 (fewer false alarms)
- Recall: > 0.75 (catches most at-risk students)

**Example output**:
```
Model Performance Comparison (sorted by Test AUC):

model           test_auc  test_f1  test_precision  test_recall  test_accuracy  train_time
CatBoost        0.8654    0.7812   0.8123         0.7534       0.8432         45.23
RandomForest    0.8521    0.7654   0.7989         0.7345       0.8312         23.45
XGBoost         0.8498    0.7623   0.7856         0.7412       0.8298         67.89
```

### RAG System

**Good scores**:
- Retrieval Relevance: > 0.70 (retrieves relevant context)
- Response Quality: > 0.75 (generates useful responses)
- Latency: < 3s (fast enough for real-time chat)

**Example output**:
```
BENCHMARK SUMMARY
Retrieval Relevance:   0.825
Response Quality:      0.780
End-to-End Latency:    2.15s
```

### LLM Advice

**Good scores**:
- Advice Quality: > 0.75 (comprehensive and actionable)
- Consistency: > 0.80 (stable across runs)
- Relevance: > 0.85 (matches student's situation)
- Response Time: < 5s (acceptable for advice generation)

**Example output**:
```
BENCHMARK SUMMARY
Response Time:  3.24s
Advice Quality: 0.812
Consistency:    0.856
Relevance:      0.900
```

## Output Files

All benchmark results are saved to the `results/` directory:

- `predictive_benchmark_*.csv`: Detailed model comparison
- `rag_benchmark_*.json`: RAG system metrics
- `llm_benchmark_*.json`: LLM advice quality metrics
- `comprehensive_benchmark_*.json`: Combined report from all benchmarks

## Customization

### Adjust Predictive Model Parameters

Edit `tests/benchmark_predictive.py`:
```python
# Change number of CV folds
benchmark.run_full_benchmark(n_folds=10)  # More thorough

# Use different data
benchmark.run_full_benchmark(data_path="custom_data.csv")
```

### Add More RAG Test Cases

Edit `tests/benchmark_rag.py`:
```python
self.test_cases = [
    {
        "question": "Your custom question",
        "expected_topics": ["topic1", "topic2"],
        "category": "custom_category"
    },
    # ... more test cases
]
```

### Adjust LLM Quality Criteria

Edit `tests/benchmark_llm.py`:
```python
# Customize quality score weights
quality_score = (
    (1.0 if scores["has_specific_numbers"] else 0.0) * 0.30 +  # Increase weight
    (1.0 if scores["has_actionable_steps"] else 0.0) * 0.30 +
    # ... adjust other weights
)
```

## Interpreting Results

### When Predictive Models Perform Poorly
- Check data quality and balance
- Verify feature engineering
- Try hyperparameter tuning
- Consider ensemble methods

### When RAG Retrieval Is Poor
- Review vector store quality
- Check if knowledge base has relevant content
- Adjust chunk size and overlap
- Tune similarity threshold

### When LLM Advice Is Low Quality
- Review prompt engineering
- Add more context to prompts
- Use better student profile data
- Consider fine-tuning

## Troubleshooting

**"File not found: modeling_data.csv"**
```bash
# Run the full pipeline first to generate data
python run_pipeline.py
```

**"RAG benchmark failed: Cannot load vector store"**
```bash
# Initialize the RAG system first
python -c "from src.chatbot.rag_system import RAGChatbot; RAGChatbot()"
```

**"LLM benchmark failed: API key not found"**
```bash
# Set your Gemini API key
export GEMINI_API_KEY=your_key_here
```

**"Out of memory during benchmark"**
- Reduce CV folds: `n_folds=3`
- Use smaller test samples
- Run benchmarks individually instead of all at once

## Notes

- **First run is slower**: Vector stores and models need to be loaded
- **API rate limits**: LLM benchmark may be throttled if running too frequently
- **Randomness**: Some variation in results is normal due to random seeds
- **Test data**: Make sure you have sufficient test data for meaningful results

## Next Steps

After benchmarking:

1. **Analyze results**: Identify which components need improvement
2. **Optimize**: Focus on low-performing areas
3. **Re-benchmark**: Measure improvement after changes
4. **Deploy**: Use best-performing configuration in production

## References

- OULAD Dataset: https://www.kaggle.com/datasets/anlgrbz/student-demographics-online-education-dataoulad
- SHAP Explainability: https://github.com/slundberg/shap
- Gemini API: https://ai.google.dev/

