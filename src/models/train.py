"""
Model training module for PLAF.

This module trains multiple ML models and performs cross-validation.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = False  # Force disable for Python 3.14 compatibility
except ImportError:
    XGBOOST_AVAILABLE = False
try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, classification_report, confusion_matrix
)
import joblib
from typing import Dict, Tuple, List
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train and evaluate multiple ML models."""
    
    def __init__(self, X: pd.DataFrame, y: pd.Series, random_state: int = 42, use_smote: bool = True):
        """
        Initialize model trainer.
        
        Args:
            X: Feature matrix
            y: Target variable
            random_state: Random seed for reproducibility
            use_smote: Whether to apply SMOTE for balancing (default: True)
        """
        self.X = X
        self.y = y
        self.random_state = random_state
        self.use_smote = use_smote and SMOTE_AVAILABLE
        self.models = {}
        self.results = {}
        self.best_model = None
        self.best_model_name = None
        
        # Apply SMOTE if requested
        if self.use_smote:
            logger.info("Applying SMOTE to balance dataset...")
            self._apply_smote()
        else:
            if use_smote and not SMOTE_AVAILABLE:
                logger.warning("SMOTE requested but not available. Install imbalanced-learn: pip install imbalanced-learn")
    
    def _apply_smote(self):
        """Apply SMOTE to balance the dataset."""
        if not SMOTE_AVAILABLE:
            return
        
        original_counts = self.y.value_counts()
        original_size = len(self.y)
        logger.info(f"Original class distribution: {original_counts.to_dict()}")
        
        try:
            smote = SMOTE(random_state=self.random_state, k_neighbors=5)
            X_resampled, y_resampled = smote.fit_resample(self.X, self.y)
            
            # Convert back to DataFrame/Series to maintain column names
            self.X = pd.DataFrame(X_resampled, columns=self.X.columns)
            self.y = pd.Series(y_resampled, name=self.y.name)
            
            new_counts = self.y.value_counts()
            logger.info(f"After SMOTE class distribution: {new_counts.to_dict()}")
            logger.info(f"Dataset size: {original_size} -> {len(self.y)}")
            
        except Exception as e:
            logger.error(f"SMOTE failed: {e}")
            logger.warning("Continuing without SMOTE...")
        
    def initialize_models(self) -> Dict:
        """
        Initialize all models to train.
        
        Returns:
            Dictionary of model instances
        """
        logger.info("Initializing models...")
        
        self.models = {
            'Logistic Regression': LogisticRegression(
                max_iter=1000,
                random_state=self.random_state,
                class_weight='balanced'
            ),
            
            'Random Forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=self.random_state,
                class_weight='balanced',
                n_jobs=-1
            ),
            
            # CatBoost only if available
            **({'CatBoost': CatBoostClassifier(
                iterations=500,
                learning_rate=0.1,
                depth=6,
                random_state=self.random_state,
                auto_class_weights='Balanced',
                verbose=False
            )} if CATBOOST_AVAILABLE else {}),
            
            # XGBoost only if available
            **({'XGBoost': XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=self.random_state,
                scale_pos_weight=len(self.y[self.y==0]) / len(self.y[self.y==1]),  # Handle imbalance
                n_jobs=-1,
                eval_metric='logloss'
            )} if XGBOOST_AVAILABLE else {}),
            
            'SVM': SVC(
                kernel='rbf',
                C=1.0,
                random_state=self.random_state,
                class_weight='balanced',
                probability=True  # Enable probability estimates for AUC
            )
        }
        
        logger.info(f"Initialized {len(self.models)} models")
        return self.models
    
    def train_with_cross_validation(self, n_folds: int = 5) -> Dict:
        """
        Train all models with k-fold cross-validation.
        
        Args:
            n_folds: Number of folds for cross-validation
            
        Returns:
            Dictionary with results for each model
        """
        logger.info(f"Training models with {n_folds}-fold cross-validation...")
        
        # Initialize models if not done yet
        if not self.models:
            self.initialize_models()
        
        # Setup stratified k-fold
        cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=self.random_state)
        
        # Scoring metrics
        scoring = {
            'accuracy': 'accuracy',
            'precision': 'precision',
            'recall': 'recall',
            'f1': 'f1',
            'auc': 'roc_auc'
        }
        
        results = {}
        
        for model_name, model in self.models.items():
            logger.info(f"\nTraining {model_name}...")
            
            # Perform cross-validation
            cv_results = cross_validate(
                model, self.X, self.y,
                cv=cv,
                scoring=scoring,
                return_train_score=True,
                n_jobs=-1 if model_name != 'SVM' else 1  # SVM can be slow with parallel
            )
            
            # Store results
            results[model_name] = {
                'accuracy': cv_results['test_accuracy'].mean(),
                'accuracy_std': cv_results['test_accuracy'].std(),
                'precision': cv_results['test_precision'].mean(),
                'precision_std': cv_results['test_precision'].std(),
                'recall': cv_results['test_recall'].mean(),
                'recall_std': cv_results['test_recall'].std(),
                'f1': cv_results['test_f1'].mean(),
                'f1_std': cv_results['test_f1'].std(),
                'auc': cv_results['test_auc'].mean(),
                'auc_std': cv_results['test_auc'].std(),
            }
            
            logger.info(f"{model_name} - F1: {results[model_name]['f1']:.4f} (+/- {results[model_name]['f1_std']:.4f})")
            logger.info(f"{model_name} - AUC: {results[model_name]['auc']:.4f} (+/- {results[model_name]['auc_std']:.4f})")
        
        self.results = results
        return results
    
    def select_best_model(self, metric: str = 'f1') -> Tuple[str, object]:
        """
        Select the best performing model based on a metric.
        
        Args:
            metric: Metric to use for selection (default: f1)
            
        Returns:
            Tuple of (model_name, model_instance)
        """
        if not self.results:
            raise ValueError("No results available. Run train_with_cross_validation() first.")
        
        # Find best model
        best_score = -1
        best_name = None
        
        for model_name, metrics in self.results.items():
            if metrics[metric] > best_score:
                best_score = metrics[metric]
                best_name = model_name
        
        logger.info(f"\nBest model: {best_name} ({metric}={best_score:.4f})")
        
        # Train best model on full dataset
        best_model = self.models[best_name]
        best_model.fit(self.X, self.y)
        
        self.best_model = best_model
        self.best_model_name = best_name
        
        return best_name, best_model
    
    def get_results_dataframe(self) -> pd.DataFrame:
        """
        Get results as a formatted DataFrame.
        
        Returns:
            DataFrame with model comparison
        """
        if not self.results:
            raise ValueError("No results available. Run train_with_cross_validation() first.")
        
        # Convert to DataFrame
        results_df = pd.DataFrame(self.results).T
        
        # Round for readability
        results_df = results_df.round(4)
        
        # Sort by F1 score
        results_df = results_df.sort_values('f1', ascending=False)
        
        return results_df
    
    def save_model(self, model_path: str = 'models/best_model.pkl'):
        """
        Save the best model to disk.
        
        Args:
            model_path: Path to save the model
        """
        if self.best_model is None:
            raise ValueError("No best model selected. Run select_best_model() first.")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model
        joblib.dump({
            'model': self.best_model,
            'model_name': self.best_model_name,
            'feature_names': list(self.X.columns),
            'results': self.results
        }, model_path)
        
        logger.info(f"Model saved to {model_path}")
        
    def load_model(self, model_path: str = 'models/best_model.pkl'):
        """
        Load a saved model.
        
        Args:
            model_path: Path to the saved model
        """
        model_data = joblib.load(model_path)
        
        self.best_model = model_data['model']
        self.best_model_name = model_data['model_name']
        self.results = model_data.get('results', {})
        
        logger.info(f"Model loaded from {model_path}: {self.best_model_name}")
        
        return self.best_model


def train_models(X: pd.DataFrame, y: pd.Series, 
                n_folds: int = 5, 
                save_path: str = 'models/best_model.pkl',
                use_smote: bool = True) -> Tuple[object, pd.DataFrame]:
    """
    Convenience function to train and select best model.
    
    Args:
        X: Feature matrix
        y: Target variable
        n_folds: Number of CV folds
        save_path: Path to save best model
        use_smote: Whether to apply SMOTE for balancing
        
    Returns:
        Tuple of (best_model, results_dataframe)
    """
    trainer = ModelTrainer(X, y, use_smote=use_smote)
    
    # Train all models
    trainer.initialize_models()
    trainer.train_with_cross_validation(n_folds=n_folds)
    
    # Get results
    results_df = trainer.get_results_dataframe()
    print("\nModel Comparison:")
    print(results_df)
    
    # Select and save best model
    best_name, best_model = trainer.select_best_model(metric='f1')
    trainer.save_model(save_path)
    
    return best_model, results_df


if __name__ == "__main__":
    # Test model training
    import sys
    sys.path.append('..')
    
    from data.loader import load_oulad_data
    from data.preprocessing import preprocess_oulad_data
    from data.feature_engineering import engineer_features
    
    print("Loading data...")
    data, _ = load_oulad_data()
    
    print("Preprocessing...")
    merged_df = preprocess_oulad_data(data)
    
    print("Engineering features...")
    engineered_df, engineer = engineer_features(merged_df)
    
    print("Preparing modeling data...")
    final_df, features, target = engineer.prepare_modeling_data()
    
    # Prepare X and y
    X = final_df[features]
    y = final_df[target]
    
    print(f"\nTraining data shape: X={X.shape}, y={y.shape}")
    print(f"Target distribution: {y.value_counts().to_dict()}")
    
    # Train models
    print("\nTraining models...")
    best_model, results = train_models(X, y, n_folds=5)
    
    print("\nTraining complete!")

