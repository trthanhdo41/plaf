"""
SHAP explainability module for PLAF.

This module provides global and local model explanations using SHAP.
"""

import pandas as pd
import numpy as np
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    shap = None
    SHAP_AVAILABLE = False
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
import joblib
from typing import Dict, List, Tuple, Optional
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SHAPExplainer:
    """SHAP-based model explainability."""
    
    def __init__(self, model, X: pd.DataFrame, feature_names: List[str] = None):
        """
        Initialize SHAP explainer.
        
        Args:
            model: Trained model
            X: Feature matrix
            feature_names: List of feature names
        """
        self.model = model
        self.X = X
        self.feature_names = feature_names if feature_names else list(X.columns)
        self.explainer = None
        self.shap_values = None
        
    def create_explainer(self, use_tree_explainer: bool = True):
        """
        Create SHAP explainer appropriate for the model type.
        
        Args:
            use_tree_explainer: Use TreeExplainer (for tree-based models)
        """
        logger.info("Creating SHAP explainer...")
        
        if not SHAP_AVAILABLE:
            logger.warning("SHAP not available, skipping explainer creation")
            return
        
        try:
            if use_tree_explainer:
                # For tree-based models (RF, XGBoost, CatBoost)
                self.explainer = shap.TreeExplainer(self.model)
            else:
                # For other models (use KernelExplainer with sample)
                background = shap.sample(self.X, min(100, len(self.X)))
                self.explainer = shap.KernelExplainer(self.model.predict_proba, background)
        except Exception as e:
            logger.warning(f"TreeExplainer failed: {e}. Using KernelExplainer...")
            background = shap.sample(self.X, min(100, len(self.X)))
            self.explainer = shap.KernelExplainer(self.model.predict_proba, background)
        
        logger.info("SHAP explainer created")
        
    def calculate_shap_values(self, X: pd.DataFrame = None):
        """
        Calculate SHAP values for the dataset.
        
        Args:
            X: Feature matrix (uses self.X if not provided)
        """
        if self.explainer is None:
            self.create_explainer()
        
        if X is None:
            X = self.X
            
        logger.info(f"Calculating SHAP values for {len(X)} instances...")
        
        try:
            self.shap_values = self.explainer.shap_values(X)
            
            # For binary classification, SHAP returns values for both classes
            # We only need the positive class (index 1)
            if isinstance(self.shap_values, list):
                self.shap_values = self.shap_values[1]
                
        except Exception as e:
            logger.error(f"Error calculating SHAP values: {e}")
            raise
        
        logger.info("SHAP values calculated")
        
        return self.shap_values
    
    def plot_summary(self, save_path: str = None, max_display: int = 20):
        """
        Create SHAP summary plot (global feature importance).
        
        Args:
            save_path: Path to save the plot
            max_display: Maximum number of features to display
        """
        if self.shap_values is None:
            self.calculate_shap_values()
        
        logger.info("Creating SHAP summary plot...")
        
        plt.figure(figsize=(10, 8))
        shap.summary_plot(
            self.shap_values, 
            self.X,
            feature_names=self.feature_names,
            max_display=max_display,
            show=False
        )
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Summary plot saved to {save_path}")
        
        plt.close()
    
    def plot_feature_importance(self, save_path: str = None, max_display: int = 20):
        """
        Create bar plot of mean absolute SHAP values (feature importance).
        
        Args:
            save_path: Path to save the plot
            max_display: Maximum number of features to display
        """
        if self.shap_values is None:
            self.calculate_shap_values()
        
        logger.info("Creating feature importance plot...")
        
        # Calculate mean absolute SHAP values
        mean_shap = np.abs(self.shap_values).mean(axis=0)
        
        # Create DataFrame for plotting
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': mean_shap
        }).sort_values('importance', ascending=False).head(max_display)
        
        # Plot
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(importance_df)), importance_df['importance'])
        plt.yticks(range(len(importance_df)), importance_df['feature'])
        plt.xlabel('Mean |SHAP value|')
        plt.title('Feature Importance (SHAP)')
        plt.gca().invert_yaxis()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Feature importance plot saved to {save_path}")
        
        plt.close()
        
        return importance_df
    
    def plot_dependence(self, feature: str, interaction_feature: str = None, 
                       save_path: str = None):
        """
        Create SHAP dependence plot for a specific feature.
        
        Args:
            feature: Feature name to plot
            interaction_feature: Feature to color by (auto-selected if None)
            save_path: Path to save the plot
        """
        if self.shap_values is None:
            self.calculate_shap_values()
        
        logger.info(f"Creating dependence plot for {feature}...")
        
        plt.figure(figsize=(10, 6))
        
        feature_idx = self.feature_names.index(feature)
        
        shap.dependence_plot(
            feature_idx,
            self.shap_values,
            self.X,
            feature_names=self.feature_names,
            interaction_index=interaction_feature,
            show=False
        )
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Dependence plot saved to {save_path}")
        
        plt.close()
    
    def explain_instance(self, instance_idx: int, save_path: str = None) -> Dict:
        """
        Create SHAP force plot for a specific instance (local explanation).
        
        Args:
            instance_idx: Index of the instance to explain
            save_path: Path to save the plot
            
        Returns:
            Dictionary with explanation details
        """
        if self.shap_values is None:
            self.calculate_shap_values()
        
        logger.info(f"Creating force plot for instance {instance_idx}...")
        
        # Get SHAP values for this instance
        instance_shap = self.shap_values[instance_idx]
        instance_features = self.X.iloc[instance_idx]
        
        # Get base value (expected value)
        if hasattr(self.explainer, 'expected_value'):
            base_value = self.explainer.expected_value
            if isinstance(base_value, list):
                base_value = base_value[1]  # For binary classification
        else:
            base_value = self.shap_values.mean()
        
        # Create force plot
        shap.force_plot(
            base_value,
            instance_shap,
            instance_features,
            feature_names=self.feature_names,
            matplotlib=True,
            show=False
        )
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Force plot saved to {save_path}")
        
        plt.close()
        
        # Get top positive and negative contributions
        feature_contributions = list(zip(self.feature_names, instance_shap, instance_features))
        feature_contributions.sort(key=lambda x: abs(x[1]), reverse=True)
        
        explanation = {
            'instance_idx': instance_idx,
            'base_value': float(base_value),
            'prediction': float(base_value + instance_shap.sum()),
            'top_features': [
                {
                    'feature': feat,
                    'shap_value': float(shap_val),
                    'feature_value': float(feat_val)
                }
                for feat, shap_val, feat_val in feature_contributions[:10]
            ]
        }
        
        return explanation
    
    def get_top_features_for_atrisk(self, n_top: int = 10) -> pd.DataFrame:
        """
        Get features that most contribute to at-risk predictions.
        
        Args:
            n_top: Number of top features to return
            
        Returns:
            DataFrame with top features
        """
        if self.shap_values is None:
            self.calculate_shap_values()
        
        # Mean SHAP value per feature (positive values push towards at-risk)
        mean_shap = self.shap_values.mean(axis=0)
        
        top_features_df = pd.DataFrame({
            'feature': self.feature_names,
            'mean_shap': mean_shap,
            'abs_mean_shap': np.abs(mean_shap)
        }).sort_values('mean_shap', ascending=False).head(n_top)
        
        return top_features_df


def explain_model_globally(model, X: pd.DataFrame, 
                          feature_names: List[str],
                          plots_dir: str = 'plots/shap'):
    """
    Generate global SHAP explanations.
    
    Args:
        model: Trained model
        X: Feature matrix
        feature_names: List of feature names
        plots_dir: Directory to save plots
    """
    if not SHAP_AVAILABLE:
        logger.warning("SHAP not available, skipping global explanations")
        return None, None
        
    explainer = SHAPExplainer(model, X, feature_names)
    explainer.calculate_shap_values()
    
    if explainer.explainer is None:
        logger.warning("SHAP explainer not available, skipping plots")
        return explainer, None
    
    # Create plots
    explainer.plot_summary(save_path=f'{plots_dir}/summary_plot.png')
    importance_df = explainer.plot_feature_importance(save_path=f'{plots_dir}/feature_importance.png')
    
    logger.info(f"Global explanations saved to {plots_dir}")
    
    return explainer, importance_df


if __name__ == "__main__":
    # Test SHAP explainer
    print("Testing SHAP explainer...")
    
    # This would need actual trained model and data
    # See notebooks for full example

