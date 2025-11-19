"""Generate comprehensive model evaluation report"""

import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    roc_auc_score, roc_curve, precision_recall_curve
)
import os
import sys

def main():
    # Check if predictions file exists
    if not os.path.exists('data/processed/student_predictions.csv'):
        print("ERROR: Predictions file not found!")
        print("Please run: python run_pipeline.py first")
        sys.exit(1)
    
    # Load data
    print("Loading evaluation data...")
    df = pd.read_csv('data/processed/student_predictions.csv')
    
    # Get predictions - handle different column names
    if 'is_at_risk' in df.columns:
        y_true = df['is_at_risk'].values
    else:
        print("ERROR: 'is_at_risk' column not found in predictions file")
        sys.exit(1)
    
    if 'predicted_at_risk' in df.columns:
        y_pred = df['predicted_at_risk'].values
    elif 'prediction' in df.columns:
        y_pred = df['prediction'].values
    else:
        print("ERROR: No prediction column found")
        sys.exit(1)
    
    if 'risk_probability' in df.columns:
        y_prob = df['risk_probability'].values
    elif 'probability' in df.columns:
        y_prob = df['probability'].values
    else:
        print("WARNING: No probability column found, using predictions as probabilities")
        y_prob = y_pred.astype(float)
    
    # Load model info
    try:
        model_data = joblib.load('models/best_model.pkl')
        model_name = model_data.get('model_name', 'Unknown Model')
    except:
        model_name = 'Unknown Model'
        model_data = {}
    
    print(f"\n{'='*60}")
    print(f"MODEL EVALUATION REPORT")
    print(f"Model: {model_name}")
    print(f"Dataset: {len(y_true):,} students")
    print(f"{'='*60}\n")
    
    # 1. Confusion Matrix
    print("1. CONFUSION MATRIX")
    print("-" * 60)
    cm = confusion_matrix(y_true, y_pred)
    print(f"                  Predicted")
    print(f"                  Safe    At-Risk")
    tn, fp = cm[0,0], cm[0,1]
    fn, tp = cm[1,0], cm[1,1]
    print(f"Actual Safe       {tn:,}    {fp:,}     ({tn/(tn+fp)*100:.1f}% correct)")
    print(f"       At-Risk    {fn:,}     {tp:,}     ({tp/(fn+tp)*100:.1f}% correct)")
    
    # 2. Metrics
    print(f"\n2. PERFORMANCE METRICS")
    print("-" * 60)
    print(classification_report(y_true, y_pred, target_names=['Safe', 'At-Risk']))
    
    # 3. AUC
    try:
        auc = roc_auc_score(y_true, y_prob)
        print(f"AUC-ROC Score: {auc:.4f}")
    except:
        print("AUC-ROC Score: Could not compute (need probabilities)")
        auc = None
    
    # 4. Cost Analysis
    print(f"\n3. COST-BENEFIT ANALYSIS")
    print("-" * 60)
    print(f"✅ True Positives ({tp:,}): At-risk students correctly identified")
    print(f"   → These students WILL receive interventions")
    print(f"\n❌ False Negatives ({fn:,}): At-risk students MISSED")
    print(f"   → These students WON'T receive help (WORST CASE)")
    print(f"   → Miss rate: {fn/(tp+fn)*100:.1f}%")
    print(f"\n⚠️  False Positives ({fp:,}): Safe students incorrectly flagged")
    print(f"   → These students get unnecessary interventions")
    print(f"   → False alarm rate: {fp/(fp+tn)*100:.1f}%")
    print(f"\n✅ True Negatives ({tn:,}): Safe students correctly identified")
    print(f"   → No action needed")
    
    # 5. Feature Importance (if available)
    if 'feature_names' in model_data and hasattr(model_data.get('model'), 'feature_importances_'):
        print(f"\n4. TOP 10 MOST IMPORTANT FEATURES")
        print("-" * 60)
        features = model_data['feature_names']
        importances = model_data['model'].feature_importances_
        
        # Sort by importance
        indices = np.argsort(importances)[::-1][:10]
        
        for i, idx in enumerate(indices, 1):
            print(f"{i:2d}. {features[idx]:30s} {importances[idx]:.4f}")
    
    # 6. Example Predictions
    print(f"\n5. SAMPLE PREDICTIONS")
    print("-" * 60)
    
    # High risk students (correctly identified)
    high_risk_correct = df[(df[df.columns[df.columns.str.contains('is_at_risk|actual')][0]] == 1) & 
                            (df[df.columns[df.columns.str.contains('predicted')][0]] == 1)].head(3)
    if len(high_risk_correct) > 0:
        print("\n✅ Correctly Identified At-Risk Students:")
        for _, row in high_risk_correct.iterrows():
            student_id = row.get('id_student', row.get('student_id', 'Unknown'))
            risk = row.get('risk_probability', row.get('probability', 0))
            print(f"  Student {student_id}: Risk={risk*100:.1f}% (Actual: At-Risk)")
    
    # False negatives (missed)
    false_neg = df[(df[df.columns[df.columns.str.contains('is_at_risk|actual')][0]] == 1) & 
                    (df[df.columns[df.columns.str.contains('predicted')][0]] == 0)].head(3)
    if len(false_neg) > 0:
        print("\n❌ Missed At-Risk Students (False Negatives):")
        for _, row in false_neg.iterrows():
            student_id = row.get('id_student', row.get('student_id', 'Unknown'))
            risk = row.get('risk_probability', row.get('probability', 0))
            print(f"  Student {student_id}: Risk={risk*100:.1f}% (Predicted Safe, Actually At-Risk!)")
    
    # False positives
    false_pos = df[(df[df.columns[df.columns.str.contains('is_at_risk|actual')][0]] == 0) & 
                    (df[df.columns[df.columns.str.contains('predicted')][0]] == 1)].head(3)
    if len(false_pos) > 0:
        print("\n⚠️  False Alarms (False Positives):")
        for _, row in false_pos.iterrows():
            student_id = row.get('id_student', row.get('student_id', 'Unknown'))
            risk = row.get('risk_probability', row.get('probability', 0))
            print(f"  Student {student_id}: Risk={risk*100:.1f}% (Predicted At-Risk, Actually Safe)")
    
    # 7. Save plots
    print(f"\n6. GENERATING VISUALIZATIONS")
    print("-" * 60)
    
    os.makedirs('plots/evaluation', exist_ok=True)
    
    # Plot 1: Confusion Matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Safe', 'At-Risk'],
                yticklabels=['Safe', 'At-Risk'])
    plt.title(f'Confusion Matrix - {model_name}')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig('plots/evaluation/confusion_matrix.png', dpi=300, bbox_inches='tight')
    print("  ✅ Saved: plots/evaluation/confusion_matrix.png")
    plt.close()
    
    # Plot 2: ROC Curve
    if auc is not None:
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.3f})', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {model_name}')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('plots/evaluation/roc_curve.png', dpi=300, bbox_inches='tight')
        print("  ✅ Saved: plots/evaluation/roc_curve.png")
        plt.close()
    
    # Plot 3: Risk Distribution
    plt.figure(figsize=(10, 6))
    safe_probs = df[df[df.columns[df.columns.str.contains('is_at_risk|actual')][0]]==0]['risk_probability'].values if 'risk_probability' in df.columns else []
    risk_probs = df[df[df.columns[df.columns.str.contains('is_at_risk|actual')][0]]==1]['risk_probability'].values if 'risk_probability' in df.columns else []
    
    if len(safe_probs) > 0 and len(risk_probs) > 0:
        plt.hist(safe_probs, bins=50, alpha=0.5, label='Safe Students', color='green')
        plt.hist(risk_probs, bins=50, alpha=0.5, label='At-Risk Students', color='red')
        plt.xlabel('Predicted Risk Probability')
        plt.ylabel('Count')
        plt.title('Risk Probability Distribution')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('plots/evaluation/risk_distribution.png', dpi=300, bbox_inches='tight')
        print("  ✅ Saved: plots/evaluation/risk_distribution.png")
        plt.close()
    
    print(f"\n{'='*60}")
    print("✅ EVALUATION REPORT COMPLETE!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

