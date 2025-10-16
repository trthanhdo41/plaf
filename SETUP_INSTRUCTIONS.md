# PLAF Setup Instructions

## Prerequisites
- Python 3.8+ (tested with Python 3.12.12)
- Git

## Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/trthanhdo41/plaf.git
cd plaf
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install pandas numpy scikit-learn python-dotenv google-generativeai streamlit plotly sqlalchemy scipy joblib threadpoolctl
```

### 4. Download OULAD Dataset
Download from: https://www.kaggle.com/datasets/anlgrbz/student-demographics-online-education-dataoulad
Extract to `OULAD dataset/` folder in project root

### 5. Set API Key
Create `.env` file:
```bash
echo "GEMINI_API_KEY=AIzaSyBxqH7HXGHGFcdBz13GBPN8BrnEj5hf3R0" > .env
```

## Running the System

### Test Pipeline
```bash
python test_pipeline_simple.py
```

### Full Pipeline
```bash
python run_pipeline.py
```

### Web Applications
```bash
# Student Portal
streamlit run src/lms_portal/student_app.py --server.port 8501

# Advisor Dashboard
streamlit run src/dashboard/app.py --server.port 8502

# Benchmark Dashboard
streamlit run src/dashboard/benchmark_dashboard.py --server.port 8503
```

## Troubleshooting

### Python 3.14 Compatibility
- XGBoost disabled for Python 3.14 compatibility
- SHAP disabled if not available
- DiCE disabled if not available

### Common Issues
1. **Streamlit not found**: `pip install streamlit`
2. **Plotly not found**: `pip install plotly`
3. **Database locked**: Wait and retry
4. **Memory issues**: Reduce dataset size for testing

## Performance
- **32,593 students** processed
- **25 features** engineered
- **94% accuracy** achieved
- **AUC: 0.9830**

## Support
GitHub: https://github.com/trthanhdo41/plaf
