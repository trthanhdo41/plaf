"""
Main pipeline script for PLAF.

This script runs the complete pipeline from data loading to advice generation.
"""

import pandas as pd
import numpy as np
import joblib
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import modules
from src.data.loader import load_oulad_data
from src.data.preprocessing import preprocess_oulad_data
from src.data.feature_engineering import engineer_features
from src.models.train import train_models
from src.explainability.shap_explainer import explain_model_globally
from src.prescriptive.dice_explainer import generate_counterfactual_advice
from src.prescriptive.llm_advisor import generate_llm_advice


def run_pipeline(
    dataset_path: str = "OULAD dataset",
    n_folds: int = 5,
    generate_llm: bool = False,  # Set to False to skip LLM (requires API key)
    save_results: bool = True
):
    """
    Run the complete PLAF pipeline.
    
    Args:
        dataset_path: Path to OULAD dataset
        n_folds: Number of cross-validation folds
        generate_llm: Whether to generate LLM advice (requires Gemini API key)
        save_results: Whether to save intermediate results
    """
    
    logger.info("="*80)
    logger.info("PLAF Pipeline Started")
    logger.info("="*80)
    
    # ===== STEP 1: Load Data =====
    logger.info("\n" + "="*80)
    logger.info("STEP 1: Loading OULAD Dataset")
    logger.info("="*80)
    
    data, info = load_oulad_data(dataset_path)
    
    logger.info(f"Loaded {len(data)} tables")
    for name, df in data.items():
        logger.info(f"  - {name}: {df.shape}")
    
    # ===== STEP 2: Preprocessing =====
    logger.info("\n" + "="*80)
    logger.info("STEP 2: Data Preprocessing & Merging")
    logger.info("="*80)
    
    merged_df = preprocess_oulad_data(data)
    logger.info(f"Merged dataset shape: {merged_df.shape}")
    logger.info(f"Target distribution:\n{merged_df['is_at_risk'].value_counts()}")
    
    if save_results:
        os.makedirs('data/processed', exist_ok=True)
        merged_df.to_csv('data/processed/merged_data.csv', index=False)
        logger.info("Saved merged data to data/processed/merged_data.csv")
    
    # ===== STEP 3: Feature Engineering =====
    logger.info("\n" + "="*80)
    logger.info("STEP 3: Feature Engineering & Z-Score Standardization")
    logger.info("="*80)
    
    engineered_df, engineer = engineer_features(merged_df)
    logger.info(f"Engineered dataset shape: {engineered_df.shape}")
    
    # Prepare modeling data
    final_df, features, target = engineer.prepare_modeling_data()
    logger.info(f"Final modeling data: {final_df.shape}")
    logger.info(f"Number of features: {len(features)}")
    
    if save_results:
        os.makedirs('data/features', exist_ok=True)
        final_df.to_csv('data/features/modeling_data.csv', index=False)
        logger.info("Saved feature-engineered data to data/features/modeling_data.csv")
    
    # ===== STEP 4: Train Models =====
    logger.info("\n" + "="*80)
    logger.info("STEP 4: Training Machine Learning Models")
    logger.info("="*80)
    
    X = final_df[features]
    y = final_df[target]
    
    logger.info(f"Training data: X={X.shape}, y={y.shape}")
    logger.info(f"Class distribution: {y.value_counts().to_dict()}")
    
    # Split train/test (80/20)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Train models
    best_model, results_df = train_models(X_train, y_train, n_folds=n_folds)
    
    logger.info("\n" + "Model Comparison Results:")
    logger.info("\n" + results_df.to_string())
    
    # Evaluate on test set
    y_pred = best_model.predict(X_test)
    y_pred_proba = best_model.predict_proba(X_test)[:, 1]
    
    from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
    
    logger.info("\n" + "Test Set Performance:")
    logger.info(f"AUC: {roc_auc_score(y_test, y_pred_proba):.4f}")
    logger.info("\n" + classification_report(y_test, y_pred))
    logger.info("\nConfusion Matrix:")
    logger.info(f"\n{confusion_matrix(y_test, y_pred)}")
    
    # ===== STEP 5: SHAP Explainability =====
    logger.info("\n" + "="*80)
    logger.info("STEP 5: Generating SHAP Explanations")
    logger.info("="*80)
    
    # Use sample for faster SHAP computation
    sample_size = min(1000, len(X_train))
    X_sample = X_train.sample(n=sample_size, random_state=42)
    
    explainer, importance_df = explain_model_globally(
        best_model, X_sample, features, plots_dir='plots/shap'
    )
    
    if importance_df is not None:
        logger.info("Top 10 Most Important Features:")
        logger.info("\n" + importance_df.head(10).to_string())
    else:
        logger.info("Feature importance not available (SHAP disabled)")
    
    # ===== STEP 6: Generate Counterfactuals =====
    logger.info("\n" + "="*80)
    logger.info("STEP 6: Generating Counterfactual Explanations")
    logger.info("="*80)
    
    # Get continuous features (z-score features)
    continuous_features = [f for f in features if f.endswith('_z')]
    
    logger.info(f"Using {len(continuous_features)} continuous features for counterfactuals")
    
    # Generate counterfactuals for at-risk students in test set
    counterfactuals = generate_counterfactual_advice(
        best_model, X_train, y_train, X_test, y_pred,
        features, continuous_features,
        n_students=min(10, (y_pred == 1).sum())
    )
    
    logger.info(f"Generated counterfactuals for {len(counterfactuals)} at-risk students")
    
    if save_results:
        import json
        os.makedirs('results', exist_ok=True)
        with open('results/counterfactuals.json', 'w') as f:
            json.dump(counterfactuals, f, indent=2)
        logger.info("Saved counterfactuals to results/counterfactuals.json")
    
    # ===== STEP 7: Generate LLM Advice (Optional) =====
    if generate_llm:
        logger.info("\n" + "="*80)
        logger.info("STEP 7: Generating LLM Advice with Gemini")
        logger.info("="*80)
        
        try:
            llm_advice = generate_llm_advice(counterfactuals)
            
            logger.info(f"Generated LLM advice for {len(llm_advice)} students")
            
            if save_results:
                with open('results/llm_advice.json', 'w') as f:
                    json.dump(llm_advice, f, indent=2)
                logger.info("Saved LLM advice to results/llm_advice.json")
                
        except Exception as e:
            logger.error(f"Failed to generate LLM advice: {e}")
            logger.info("Continuing without LLM advice...")
    else:
        logger.info("\n" + "Skipping LLM advice generation (set generate_llm=True to enable)")
    
    # ===== STEP 8: Save Final Predictions =====
    logger.info("\n" + "="*80)
    logger.info("STEP 8: Saving Final Predictions")
    logger.info("="*80)
    
    # Create predictions dataframe
    test_indices = X_test.index
    predictions_df = final_df.loc[test_indices].copy()
    predictions_df['risk_probability'] = y_pred_proba
    predictions_df['predicted_at_risk'] = y_pred
    
    if save_results:
        os.makedirs('data/processed', exist_ok=True)
        predictions_df.to_csv('data/processed/student_predictions.csv', index=False)
        logger.info("Saved predictions to data/processed/student_predictions.csv")
    
    # ===== Pipeline Complete =====
    logger.info("\n" + "="*80)
    logger.info("PLAF Pipeline Completed Successfully!")
    logger.info("="*80)
    
    logger.info("\nSummary:")
    logger.info(f"  - Total students processed: {len(final_df)}")
    logger.info(f"  - Test set size: {len(y_test)}")
    logger.info(f"  - At-risk students identified: {y_pred.sum()}")
    logger.info(f"  - Best model: {joblib.load('models/best_model.pkl')['model_name']}")
    logger.info(f"  - Test AUC: {roc_auc_score(y_test, y_pred_proba):.4f}")
    
    logger.info("\nNext Steps:")
    logger.info("  1. Review SHAP plots in plots/shap/")
    logger.info("  2. Check counterfactuals in results/counterfactuals.json")
    if generate_llm:
        logger.info("  3. Review LLM advice in results/llm_advice.json")
    logger.info("  4. Run Streamlit dashboard: streamlit run src/dashboard/app.py")
    
    return {
        'model': best_model,
        'results': results_df,
        'predictions': predictions_df,
        'counterfactuals': counterfactuals,
        'explainer': explainer
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run PLAF pipeline')
    parser.add_argument('--dataset', type=str, default='OULAD dataset',
                       help='Path to OULAD dataset')
    parser.add_argument('--folds', type=int, default=5,
                       help='Number of CV folds')
    parser.add_argument('--llm', action='store_true',
                       help='Generate LLM advice (requires API key)')
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save intermediate results')
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    os.makedirs('plots', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    
    # Run pipeline
    try:
        results = run_pipeline(
            dataset_path=args.dataset,
            n_folds=args.folds,
            generate_llm=args.llm,
            save_results=not args.no_save
        )
        
        print("\n" + "="*80)
        print("Pipeline completed successfully!")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

