"""
DiCE counterfactual explainer for PLAF.

This module generates counterfactual explanations using DiCE.
"""

import pandas as pd
import numpy as np
import dice_ml
from dice_ml import Dice
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CounterfactualGenerator:
    """Generate counterfactual explanations using DiCE."""
    
    def __init__(self, model, X_train: pd.DataFrame, y_train: pd.Series,
                 feature_names: List[str], continuous_features: List[str],
                 outcome_name: str = 'is_at_risk'):
        """
        Initialize counterfactual generator.
        
        Args:
            model: Trained model
            X_train: Training features
            y_train: Training target
            feature_names: List of feature names
            continuous_features: List of continuous feature names
            outcome_name: Name of outcome variable
        """
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
        self.feature_names = feature_names
        self.continuous_features = continuous_features
        self.outcome_name = outcome_name
        self.dice_data = None
        self.dice_model = None
        self.explainer = None
        
    def setup_dice(self):
        """Setup DiCE data and model objects."""
        logger.info("Setting up DiCE...")
        
        # Combine X and y for DiCE
        train_df = self.X_train.copy()
        train_df[self.outcome_name] = self.y_train.values
        
        # Create DiCE data object
        self.dice_data = dice_ml.Data(
            dataframe=train_df,
            continuous_features=self.continuous_features,
            outcome_name=self.outcome_name
        )
        
        # Create DiCE model object
        self.dice_model = dice_ml.Model(
            model=self.model,
            backend='sklearn'
        )
        
        # Create explainer
        self.explainer = Dice(
            self.dice_data,
            self.dice_model,
            method='random'  # Can use 'genetic' for better quality but slower
        )
        
        logger.info("DiCE setup complete")
        
    def generate_counterfactuals(self, instance: pd.DataFrame,
                                total_CFs: int = 3,
                                desired_class: int = 0,
                                features_to_vary: List[str] = None,
                                permitted_range: Dict[str, List] = None) -> Dict:
        """
        Generate counterfactual explanations for an instance.
        
        Args:
            instance: Instance to explain (single row DataFrame)
            total_CFs: Number of counterfactuals to generate
            desired_class: Desired outcome (0 = safe, 1 = at-risk)
            features_to_vary: List of features that can be changed (None = all continuous)
            permitted_range: Dictionary of allowed ranges for features
            
        Returns:
            Dictionary with counterfactual explanations
        """
        if self.explainer is None:
            self.setup_dice()
        
        logger.info(f"Generating {total_CFs} counterfactuals...")
        
        try:
            # Generate counterfactuals
            dice_exp = self.explainer.generate_counterfactuals(
                query_instances=instance,
                total_CFs=total_CFs,
                desired_class=desired_class,
                features_to_vary=features_to_vary if features_to_vary else 'all',
                permitted_range=permitted_range
            )
            
            # Extract counterfactual dataframe
            cf_df = dice_exp.cf_examples_list[0].final_cfs_df
            
            if cf_df is None or len(cf_df) == 0:
                logger.warning("No counterfactuals found")
                return {
                    'found': False,
                    'original_instance': instance.to_dict('records')[0],
                    'counterfactuals': []
                }
            
            # Get feature changes
            original_values = instance.iloc[0]
            changes = []
            
            for idx, cf_row in cf_df.iterrows():
                feature_changes = {}
                for feature in self.feature_names:
                    if feature in cf_row.index and feature in original_values.index:
                        original_val = original_values[feature]
                        cf_val = cf_row[feature]
                        
                        if abs(cf_val - original_val) > 1e-6:  # Changed
                            feature_changes[feature] = {
                                'original': float(original_val),
                                'counterfactual': float(cf_val),
                                'change': float(cf_val - original_val)
                            }
                
                changes.append({
                    'counterfactual_values': cf_row[self.feature_names].to_dict(),
                    'changes': feature_changes
                })
            
            result = {
                'found': True,
                'original_instance': instance.to_dict('records')[0],
                'counterfactuals': changes,
                'num_cfs': len(changes)
            }
            
            logger.info(f"Generated {len(changes)} counterfactuals")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating counterfactuals: {e}")
            return {
                'found': False,
                'original_instance': instance.to_dict('records')[0],
                'counterfactuals': [],
                'error': str(e)
            }
    
    def generate_for_atrisk_students(self, X: pd.DataFrame, y_pred: np.ndarray,
                                    n_students: int = 10,
                                    features_to_vary: List[str] = None) -> List[Dict]:
        """
        Generate counterfactuals for at-risk students.
        
        Args:
            X: Feature matrix
            y_pred: Predicted labels
            n_students: Number of students to generate CFs for
            features_to_vary: Features that can be changed
            
        Returns:
            List of counterfactual explanations
        """
        # Get at-risk students
        atrisk_indices = np.where(y_pred == 1)[0]
        
        if len(atrisk_indices) == 0:
            logger.warning("No at-risk students found")
            return []
        
        # Sample if too many
        if len(atrisk_indices) > n_students:
            sample_indices = np.random.choice(atrisk_indices, n_students, replace=False)
        else:
            sample_indices = atrisk_indices
        
        all_counterfactuals = []
        
        for idx in sample_indices:
            instance = X.iloc[[idx]]  # Keep as DataFrame
            
            cf_result = self.generate_counterfactuals(
                instance,
                total_CFs=3,
                desired_class=0,  # Want to flip to "safe"
                features_to_vary=features_to_vary
            )
            
            cf_result['instance_idx'] = int(idx)
            all_counterfactuals.append(cf_result)
        
        return all_counterfactuals
    
    def get_actionable_features(self) -> List[str]:
        """
        Get list of actionable features (can be changed by student).
        
        Returns:
            List of actionable feature names
        """
        # Features that students CAN change
        actionable = [f for f in self.feature_names if any([
            '_z' in f and any(keyword in f for keyword in [
                'score', 'click', 'vle', 'resource', 'submission',
                'engagement', 'active', 'diversity'
            ])
        ])]
        
        # Features students CANNOT change (demographics, etc.)
        # Exclude these from counterfactuals
        
        logger.info(f"Identified {len(actionable)} actionable features")
        
        return actionable


def generate_counterfactual_advice(model, X_train: pd.DataFrame, y_train: pd.Series,
                                   X_test: pd.DataFrame, y_pred: np.ndarray,
                                   feature_names: List[str],
                                   continuous_features: List[str],
                                   n_students: int = 10) -> List[Dict]:
    """
    Convenience function to generate counterfactual advice.
    
    Args:
        model: Trained model
        X_train: Training features
        y_train: Training target
        X_test: Test features
        y_pred: Predictions for test data
        feature_names: List of feature names
        continuous_features: List of continuous features
        n_students: Number of students to generate advice for
        
    Returns:
        List of counterfactual explanations
    """
    generator = CounterfactualGenerator(
        model, X_train, y_train,
        feature_names, continuous_features
    )
    
    # Get actionable features
    actionable_features = generator.get_actionable_features()
    
    # Generate counterfactuals
    counterfactuals = generator.generate_for_atrisk_students(
        X_test, y_pred,
        n_students=n_students,
        features_to_vary=actionable_features
    )
    
    return counterfactuals


if __name__ == "__main__":
    print("DiCE counterfactual generator module")

