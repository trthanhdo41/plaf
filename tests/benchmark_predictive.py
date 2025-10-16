"""
Predictive Models Benchmark

Compare performance of all ML models (CatBoost, RF, XGBoost, SVM, LR).
"""

import sys
import os
import time
import pandas as pd
import numpy as np
from typing import Dict, List
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PredictiveBenchmark:
    """Benchmark predictive models."""
    
    def __init__(self):
        """Initialize benchmark."""
        print("="*70)
        print("PREDICTIVE MODELS BENCHMARK")
        print("="*70)
        
        self.models = {}
        self.results = []
        
    def load_data(self, data_path: str = "data/features/modeling_data.csv"):
        """Load modeling data."""
        print("\n[1/5] Loading Data...")
        print("-"*70)
        
        try:
            df = pd.read_csv(data_path)
            print(f"  [OK] Loaded {len(df):,} samples")
            
            # Separate features and target
            target = 'is_at_risk'
            features = [col for col in df.columns if col.endswith('_z') or col in [
                'gender_M', 'region_encoded', 'imd_band_encoded', 
                'age_band_encoded', 'highest_education_encoded'
            ]]
            
            X = df[features]
            y = df[target]
            
            print(f"  Features: {len(features)}")
            print(f"  Target distribution: {y.value_counts().to_dict()}")
            
            return X, y, features
            
        except FileNotFoundError:
            print(f"  [ERROR] Data file not found: {data_path}")
            print("  [TIP] Run: python run_pipeline.py first to generate data")
            return None, None, None
    
    def initialize_models(self):
        """Initialize all models."""
        print("\n[2/5] Initializing Models...")
        print("-"*70)
        
        from catboost import CatBoostClassifier
        from sklearn.ensemble import RandomForestClassifier
        from xgboost import XGBClassifier
        from sklearn.svm import SVC
        from sklearn.linear_model import LogisticRegression
        
        self.models = {
            "CatBoost": CatBoostClassifier(
                iterations=500,
                learning_rate=0.05,
                depth=6,
                verbose=False,
                random_state=42
            ),
            "RandomForest": RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=10,
                random_state=42,
                n_jobs=-1
            ),
            "XGBoost": XGBClassifier(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=6,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            ),
            "SVM": SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=42
            ),
            "LogisticRegression": LogisticRegression(
                C=1.0,
                max_iter=1000,
                random_state=42,
                n_jobs=-1
            )
        }
        
        print(f"  [OK] Initialized {len(self.models)} models")
        for name in self.models.keys():
            print(f"    - {name}")
    
    def train_and_evaluate(self, X, y, n_folds: int = 5):
        """Train and evaluate all models with cross-validation."""
        print(f"\n[3/5] Training & Evaluating Models ({n_folds}-fold CV)...")
        print("-"*70)
        
        from sklearn.model_selection import train_test_split
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"  Train: {len(X_train):,} samples | Test: {len(X_test):,} samples\n")
        
        cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        
        for name, model in self.models.items():
            print(f"  Training {name}...")
            
            # Cross-validation
            start_time = time.time()
            cv_scores = cross_val_score(model, X_train, y_train, cv=cv, 
                                       scoring='roc_auc', n_jobs=-1)
            cv_time = time.time() - start_time
            
            # Train on full training set
            start_time = time.time()
            model.fit(X_train, y_train)
            train_time = time.time() - start_time
            
            # Predict on test set
            start_time = time.time()
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            pred_time = time.time() - start_time
            
            # Calculate metrics
            results = {
                "model": name,
                "cv_auc_mean": cv_scores.mean(),
                "cv_auc_std": cv_scores.std(),
                "test_accuracy": accuracy_score(y_test, y_pred),
                "test_precision": precision_score(y_test, y_pred),
                "test_recall": recall_score(y_test, y_pred),
                "test_f1": f1_score(y_test, y_pred),
                "test_auc": roc_auc_score(y_test, y_pred_proba),
                "cv_time": cv_time,
                "train_time": train_time,
                "pred_time": pred_time,
                "pred_time_per_sample": pred_time / len(X_test)
            }
            
            self.results.append(results)
            
            print(f"    CV AUC: {results['cv_auc_mean']:.4f} ± {results['cv_auc_std']:.4f}")
            print(f"    Test AUC: {results['test_auc']:.4f}")
            print(f"    Test F1: {results['test_f1']:.4f}")
            print(f"    Train Time: {train_time:.2f}s")
            print()
        
        return X_test, y_test
    
    def generate_comparison_table(self):
        """Generate comparison table."""
        print("\n[4/5] Generating Comparison Table...")
        print("-"*70)
        
        df = pd.DataFrame(self.results)
        
        # Sort by test AUC
        df = df.sort_values("test_auc", ascending=False)
        
        # Display table
        print("\nModel Performance Comparison (sorted by Test AUC):\n")
        
        display_cols = ["model", "test_auc", "test_f1", "test_precision", 
                       "test_recall", "test_accuracy", "train_time"]
        
        print(df[display_cols].to_string(index=False))
        
        # Identify best model
        best_model = df.iloc[0]
        print(f"\n>> Best Model: {best_model['model']} (AUC: {best_model['test_auc']:.4f})")
        
        return df
    
    def generate_detailed_report(self, X_test, y_test):
        """Generate detailed report for best model."""
        print("\n[5/5] Generating Detailed Report...")
        print("-"*70)
        
        # Get best model
        best_result = max(self.results, key=lambda x: x['test_auc'])
        best_model_name = best_result['model']
        best_model = self.models[best_model_name]
        
        print(f"\nBest Model: {best_model_name}")
        print("="*70)
        
        # Predictions
        y_pred = best_model.predict(X_test)
        y_pred_proba = best_model.predict_proba(X_test)[:, 1]
        
        # Classification Report
        print("\nClassification Report:\n")
        print(classification_report(y_test, y_pred, target_names=["Not At-Risk", "At-Risk"]))
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print("\nConfusion Matrix:\n")
        print(f"                Predicted Not At-Risk  Predicted At-Risk")
        print(f"Actual Not At-Risk        {cm[0][0]:<20} {cm[0][1]:<20}")
        print(f"Actual At-Risk            {cm[1][0]:<20} {cm[1][1]:<20}")
        
        # Calculate additional metrics
        tn, fp, fn, tp = cm.ravel()
        specificity = tn / (tn + fp)
        sensitivity = tp / (tp + fn)
        
        print(f"\nAdditional Metrics:")
        print(f"  Sensitivity (Recall):  {sensitivity:.4f}")
        print(f"  Specificity:           {specificity:.4f}")
        print(f"  False Positive Rate:   {fp/(fp+tn):.4f}")
        print(f"  False Negative Rate:   {fn/(fn+tp):.4f}")
        
        return best_result
    
    def save_results(self, df: pd.DataFrame):
        """Save benchmark results."""
        os.makedirs("results", exist_ok=True)
        
        output_file = f"results/predictive_benchmark_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False)
        
        print(f"\n[SAVED] Results saved to: {output_file}")
    
    def run_full_benchmark(self, data_path: str = "data/features/modeling_data.csv", n_folds: int = 5):
        """Run complete predictive benchmark."""
        
        # Load data
        X, y, features = self.load_data(data_path)
        if X is None:
            return None
        
        # Initialize models
        self.initialize_models()
        
        # Train and evaluate
        X_test, y_test = self.train_and_evaluate(X, y, n_folds)
        
        # Generate comparison
        df = self.generate_comparison_table()
        
        # Detailed report
        best_result = self.generate_detailed_report(X_test, y_test)
        
        # Save results
        self.save_results(df)
        
        # Summary
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY")
        print("="*70)
        print(f">> Best Model: {best_result['model']}")
        print(f"   Test AUC:   {best_result['test_auc']:.4f}")
        print(f"   Test F1:    {best_result['test_f1']:.4f}")
        print(f"   Train Time: {best_result['train_time']:.2f}s")
        print("="*70)
        
        return df


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark predictive models')
    parser.add_argument('--data', type=str, default='data/features/modeling_data.csv',
                       help='Path to modeling data')
    parser.add_argument('--folds', type=int, default=5,
                       help='Number of CV folds')
    
    args = parser.parse_args()
    
    benchmark = PredictiveBenchmark()
    results = benchmark.run_full_benchmark(data_path=args.data, n_folds=args.folds)
    
    if results is not None:
        print("\n[SUCCESS] Predictive Benchmark completed successfully!")
    else:
        print("\n[FAILED] Predictive Benchmark failed")

