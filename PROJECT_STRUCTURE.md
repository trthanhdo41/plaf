# Project Structure Guide

File này explain cấu trúc folders và files trong project. Đọc để biết đâu là đâu khi bắt đầu code.

```
PLAF/
│
├── OULAD dataset/                # Raw data từ Kaggle
│   ├── studentInfo.csv           # Main file - có final_result (target)
│   ├── studentAssessment.csv     # Scores data
│   ├── assessments.csv           # Assessment metadata
│   ├── studentRegistration.csv   # Registration timestamps
│   ├── studentVle.csv            # VLE logs (warning: 433MB!)
│   ├── vle.csv                   # VLE resource info
│   └── courses.csv               # Course list
│
├── data/
│   ├── raw/                      # Optional - copy of OULAD
│   ├── processed/                # Cleaned data
│   │   ├── cleaned_data.csv
│   │   └── train_test_split.pkl
│   └── features/                 # Feature-engineered datasets
│       ├── features_raw.csv      # Before z-scoring
│       ├── features_z_scored.csv # After z-scoring
│       └── feature_names.json
│
├── notebooks/                    # Jupyter notebooks for prototyping
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_xai_analysis.ipynb
│   └── 05_prescriptive_analysis.ipynb
│
├── src/                          # Production code
│   │
│   ├── data/                     # Module 1: Data pipeline
│   │   ├── __init__.py
│   │   ├── loader.py             # CSV loading logic
│   │   ├── preprocessor.py       # Cleaning, missing values
│   │   └── feature_engineer.py   # Feature creation + z-scores
│   │
│   ├── models/                   # Module 2: ML models
│   │   ├── __init__.py
│   │   ├── trainer.py            # Train & benchmark models
│   │   ├── evaluator.py          # Cross-validation, metrics
│   │   └── predictor.py          # Load saved model, predict
│   │
│   ├── explainability/           # Module 2: XAI components
│   │   ├── __init__.py
│   │   ├── shap_explainer.py     # SHAP implementation
│   │   ├── anchor_explainer.py   # Anchor rules
│   │   └── visualizer.py         # Plotting functions
│   │
│   ├── prescriptive/             # Module 3: Prescriptive layer
│   │   ├── __init__.py
│   │   ├── dice_generator.py     # DiCE counterfactuals
│   │   ├── value_converter.py    # Z-score <-> raw conversion
│   │   └── llm_advisor.py        # Gemini API integration
│   │
│   ├── dashboard/                # Module 4: Web interface
│   │   ├── __init__.py
│   │   ├── app.py                # Streamlit main app
│   │   ├── components/           # Page components
│   │   │   ├── overview.py
│   │   │   ├── student_list.py
│   │   │   ├── student_detail.py
│   │   │   └── intervention_log.py
│   │   └── utils.py
│   │
│   └── utils.py                  # Shared helper functions
│
├── models/                       # Saved trained models (gitignored)
│   ├── best_model.pkl
│   ├── scaler.pkl
│   ├── feature_names.json
│   └── model_benchmark.csv
│
├── config/                       # Config files
│   ├── config.yaml               # Main settings
│   └── prompt_templates.yaml     # LLM prompts
│
├── logs/                         # App logs (gitignored)
│   └── plaf.log
│
├── plots/                        # Generated charts (gitignored)
│   ├── shap_summary.png
│   ├── shap_dependence/
│   └── force_plots/
│
├── tests/                        # Unit tests (optional)
│   ├── test_data_loader.py
│   ├── test_feature_engineer.py
│   └── test_models.py
│
├── README.md                     # Main documentation
├── PROJECT_STRUCTURE.md          # This file
├── requirements.txt              # Python deps
├── .gitignore                    # Git ignore
└── .env.example                  # Template for API keys

```

## Workflow by modules

### Module 1: Data Pipeline (Step 1)
```
loader.py → preprocessor.py → feature_engineer.py
(Load CSVs) → (Clean + merge) → (Engineer features + z-score)
```

### Module 2: Predictive + XAI (Steps 2-5)
```
trainer.py → shap_explainer.py + anchor_explainer.py
(Train models) → (Explain predictions)
```

### Module 3: Prescriptive (Steps 6-7)
```
dice_generator.py → value_converter.py → llm_advisor.py
(Counterfactuals) → (Z→raw values) → (Generate NL advice)
```

### Module 4: Dashboard (Step 8)
```
app.py (main Streamlit app)
```

## Quick start

**1. Environment setup:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Config API key:**
```bash
cp .env.example .env
# Edit .env, add your GEMINI_API_KEY
```

**3. Start exploring:**
```bash
# Option A: Use notebooks (recommended for first time)
jupyter notebook

# Option B: Run scripts directly
python -m src.data.loader
python -m src.models.trainer
```

**4. Launch dashboard:**
```bash
streamlit run src/dashboard/app.py
```

## Data flow

Simple flow chart:
```
CSV files → loader → preprocessor → feature_engineer → trainer
→ SHAP/Anchors → DiCE → LLM → Dashboard
```

## Where to start?

**If you're new to the project:**
1. Read `README.md` first
2. Open `notebooks/01_data_exploration.ipynb`
3. Explore OULAD dataset structure
4. Gradually work through other notebooks

**If you're implementing:**
Priority order:
- `src/data/loader.py` - start here
- `src/data/feature_engineer.py` - then this
- `src/models/trainer.py` - core modeling
- `src/explainability/*` - XAI layer
- `src/prescriptive/*` - advanced stuff
- `src/dashboard/app.py` - UI last

## Development tips

- Use notebooks for prototyping, then move stable code to `src/`
- Commit frequently (at least after each major milestone)
- Add docstrings (future you will thank you)
- Don't optimize prematurely - make it work first, then make it fast
- If stuck on DiCE or SHAP, check their official docs/examples

---

Good luck! This is an ambitious project but totally doable step by step.

