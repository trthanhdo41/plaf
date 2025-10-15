"""
Anchor explainability module for PLAF.

This module provides rule-based explanations using Anchors.
"""

import pandas as pd
import numpy as np
from anchor import anchor_tabular
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnchorExplainer:
    """Anchor-based rule explanations."""
    
    def __init__(self, model, X_train: pd.DataFrame, feature_names: List[str]):
        """
        Initialize Anchor explainer.
        
        Args:
            model: Trained model with predict_proba method
            X_train: Training data
            feature_names: List of feature names
        """
        self.model = model
        self.X_train = X_train
        self.feature_names = feature_names
        self.explainer = None
        
    def create_explainer(self, categorical_names: Dict = None):
        """
        Create Anchor explainer.
        
        Args:
            categorical_names: Dictionary mapping feature indices to category names
        """
        logger.info("Creating Anchor explainer...")
        
        # Convert to numpy array
        X_array = self.X_train.values
        
        # Create explainer
        self.explainer = anchor_tabular.AnchorTabularExplainer(
            class_names=['Safe', 'At-Risk'],
            feature_names=self.feature_names,
            train_data=X_array,
            categorical_names=categorical_names
        )
        
        logger.info("Anchor explainer created")
        
    def explain_instance(self, instance: pd.Series, threshold: float = 0.95) -> Dict:
        """
        Generate anchor explanation for a single instance.
        
        Args:
            instance: Single instance to explain (as Series or array)
            threshold: Precision threshold for anchor
            
        Returns:
            Dictionary with explanation details
        """
        if self.explainer is None:
            self.create_explainer()
        
        # Convert to array if needed
        if isinstance(instance, pd.Series):
            instance_array = instance.values
        else:
            instance_array = instance
        
        # Predict function for anchor
        def predict_fn(X):
            return self.model.predict(X)
        
        try:
            # Generate explanation
            explanation = self.explainer.explain_instance(
                instance_array,
                predict_fn,
                threshold=threshold
            )
            
            # Extract anchor rules
            anchor_rules = explanation.names()
            precision = explanation.precision()
            coverage = explanation.coverage()
            
            result = {
                'anchor_rules': anchor_rules,
                'precision': float(precision),
                'coverage': float(coverage),
                'prediction': int(predict_fn(instance_array.reshape(1, -1))[0])
            }
            
            logger.info(f"Anchor explanation: {anchor_rules}")
            logger.info(f"Precision: {precision:.3f}, Coverage: {coverage:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating anchor explanation: {e}")
            return {
                'anchor_rules': [],
                'precision': 0.0,
                'coverage': 0.0,
                'prediction': int(predict_fn(instance_array.reshape(1, -1))[0]),
                'error': str(e)
            }
    
    def explain_atrisk_students(self, X: pd.DataFrame, y_pred: np.ndarray, 
                               n_samples: int = 10) -> List[Dict]:
        """
        Generate anchor explanations for at-risk students.
        
        Args:
            X: Feature matrix
            y_pred: Predicted labels
            n_samples: Number of at-risk students to explain
            
        Returns:
            List of explanations
        """
        # Get at-risk students
        atrisk_indices = np.where(y_pred == 1)[0]
        
        if len(atrisk_indices) == 0:
            logger.warning("No at-risk students found")
            return []
        
        # Sample if too many
        if len(atrisk_indices) > n_samples:
            sample_indices = np.random.choice(atrisk_indices, n_samples, replace=False)
        else:
            sample_indices = atrisk_indices
        
        explanations = []
        
        for idx in sample_indices:
            instance = X.iloc[idx]
            explanation = self.explain_instance(instance)
            explanation['instance_idx'] = int(idx)
            explanations.append(explanation)
        
        return explanations


def generate_anchor_explanations(model, X_train: pd.DataFrame, X_test: pd.DataFrame,
                                 y_pred: np.ndarray, feature_names: List[str],
                                 n_samples: int = 10) -> List[Dict]:
    """
    Convenience function to generate anchor explanations.
    
    Args:
        model: Trained model
        X_train: Training data
        X_test: Test data to explain
        y_pred: Predictions for test data
        feature_names: List of feature names
        n_samples: Number of samples to explain
        
    Returns:
        List of anchor explanations
    """
    explainer = AnchorExplainer(model, X_train, feature_names)
    explanations = explainer.explain_atrisk_students(X_test, y_pred, n_samples)
    
    return explanations


if __name__ == "__main__":
    print("Anchor explainer module")

