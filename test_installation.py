"""
Test script to verify installation and imports.
Run this after installing requirements.txt to check everything works.
"""

import sys

print("="*80)
print("PLAF Installation Test")
print("="*80)

# Test imports
tests = []

print("\n1. Testing core data science libraries...")
try:
    import pandas as pd
    import numpy as np
    import sklearn
    print(f"   ✓ pandas {pd.__version__}")
    print(f"   ✓ numpy {np.__version__}")
    print(f"   ✓ scikit-learn {sklearn.__version__}")
    tests.append(True)
except ImportError as e:
    print(f"   ✗ Failed: {e}")
    tests.append(False)

print("\n2. Testing ML model libraries...")
try:
    import catboost
    import xgboost
    print(f"   ✓ catboost {catboost.__version__}")
    print(f"   ✓ xgboost {xgboost.__version__}")
    tests.append(True)
except ImportError as e:
    print(f"   ✗ Failed: {e}")
    tests.append(False)

print("\n3. Testing XAI libraries...")
try:
    import shap
    import dice_ml
    print(f"   ✓ shap {shap.__version__}")
    print(f"   ✓ dice-ml {dice_ml.__version__}")
    tests.append(True)
except ImportError as e:
    print(f"   ✗ Failed: {e}")
    tests.append(False)

print("\n4. Testing visualization libraries...")
try:
    import matplotlib
    import seaborn
    import plotly
    print(f"   ✓ matplotlib {matplotlib.__version__}")
    print(f"   ✓ seaborn {seaborn.__version__}")
    print(f"   ✓ plotly {plotly.__version__}")
    tests.append(True)
except ImportError as e:
    print(f"   ✗ Failed: {e}")
    tests.append(False)

print("\n5. Testing Streamlit...")
try:
    import streamlit
    print(f"   ✓ streamlit {streamlit.__version__}")
    tests.append(True)
except ImportError as e:
    print(f"   ✗ Failed: {e}")
    tests.append(False)

print("\n6. Testing Google Generative AI (Gemini)...")
try:
    import google.generativeai as genai
    print(f"   ✓ google-generativeai installed")
    tests.append(True)
except ImportError as e:
    print(f"   ✗ Failed: {e}")
    tests.append(False)

print("\n7. Testing custom modules...")
try:
    from src.data.loader import OULADLoader
    from src.data.preprocessing import OULADPreprocessor
    from src.data.feature_engineering import FeatureEngineer
    from src.models.train import ModelTrainer
    from src.explainability.shap_explainer import SHAPExplainer
    from src.prescriptive.dice_explainer import CounterfactualGenerator
    from src.prescriptive.llm_advisor import LLMAdvisor
    print("   ✓ All custom modules imported successfully")
    tests.append(True)
except ImportError as e:
    print(f"   ✗ Failed: {e}")
    tests.append(False)

print("\n8. Checking OULAD dataset...")
import os
if os.path.exists("OULAD dataset"):
    files = os.listdir("OULAD dataset")
    csv_files = [f for f in files if f.endswith('.csv')]
    print(f"   ✓ OULAD dataset folder found")
    print(f"   ✓ Found {len(csv_files)} CSV files")
    tests.append(True)
else:
    print("   ⚠ OULAD dataset folder not found")
    print("   Please download dataset from Kaggle and place in 'OULAD dataset' folder")
    tests.append(False)

print("\n9. Checking .env file for API key...")
if os.path.exists(".env"):
    print("   ✓ .env file exists")
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key and api_key != 'your_api_key_here':
        print("   ✓ GEMINI_API_KEY configured")
        tests.append(True)
    else:
        print("   ⚠ GEMINI_API_KEY not configured (LLM advice will not work)")
        print("   Get API key from https://ai.google.dev/")
        tests.append(False)
else:
    print("   ⚠ .env file not found")
    print("   Copy .env.example to .env and add your API key")
    tests.append(False)

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

passed = sum(tests)
total = len(tests)

print(f"\nTests passed: {passed}/{total}")

if passed == total:
    print("\n✓ All tests passed! System is ready.")
    print("\nNext steps:")
    print("  1. Run pipeline: python run_pipeline.py")
    print("  2. Or use notebook: jupyter notebook")
    print("  3. Launch dashboard: streamlit run src/dashboard/app.py")
elif passed >= 7:
    print("\n⚠ Most tests passed. Minor issues detected.")
    print("You can proceed, but some features may not work.")
else:
    print("\n✗ Multiple failures detected.")
    print("Please fix the errors above before proceeding.")
    print("\nTry:")
    print("  pip install -r requirements.txt")

print("\n" + "="*80)
sys.exit(0 if passed >= 7 else 1)

