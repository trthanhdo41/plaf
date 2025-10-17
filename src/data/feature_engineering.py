"""
Feature engineering module for PLAF.

This module handles advanced feature creation and z-score standardization.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering and transformation for student data."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize feature engineer.
        
        Args:
            df: Merged DataFrame from preprocessing
        """
        self.df = df.copy()
        self.label_encoders = {}
        self.z_score_params = {}  # Store mean/std for z-score conversion
        
    def encode_categorical_features(self) -> pd.DataFrame:
        """
        Encode categorical variables.
        
        Returns:
            DataFrame with encoded categorical features
        """
        logger.info("Encoding categorical features...")
        
        categorical_cols = [
            'code_module', 'code_presentation', 'gender', 'region',
            'highest_education', 'imd_band', 'age_band', 'disability'
        ]
        
        for col in categorical_cols:
            if col in self.df.columns:
                le = LabelEncoder()
                self.df[f'{col}_encoded'] = le.fit_transform(self.df[col].astype(str))
                self.label_encoders[col] = le
                logger.info(f"Encoded {col}: {len(le.classes_)} categories")
        
        return self.df
    
    def create_derived_features(self) -> pd.DataFrame:
        """
        Create additional derived features.
        
        Returns:
            DataFrame with new features
        """
        logger.info("Creating derived features...")
        
        # Academic performance features
        if 'avg_score' in self.df.columns and 'num_assessments' in self.df.columns:
            # Submission rate (how many assessments completed)
            self.df['submission_rate'] = self.df['num_assessments'] / (self.df['num_assessments'].max() + 1)
            
        # VLE engagement features
        if 'total_clicks' in self.df.columns and 'num_days_active' in self.df.columns:
            # Average clicks per active day
            self.df['clicks_per_active_day'] = np.where(
                self.df['num_days_active'] > 0,
                self.df['total_clicks'] / self.df['num_days_active'],
                0
            )
            
        # Engagement intensity (resource diversity)
        if 'num_unique_resources' in self.df.columns and 'num_days_active' in self.df.columns:
            self.df['resource_diversity'] = np.where(
                self.df['num_days_active'] > 0,
                self.df['num_unique_resources'] / (self.df['num_days_active'] + 1),
                0
            )
        
        # Early engagement indicator
        if 'first_vle_access' in self.df.columns:
            self.df['early_engagement'] = (self.df['first_vle_access'] <= 7).astype(int)
        
        # Risk indicators
        if 'num_late_submissions' in self.df.columns:
            self.df['has_late_submissions'] = (self.df['num_late_submissions'] > 0).astype(int)
        
        if 'num_unregistrations' in self.df.columns:
            self.df['has_unregistrations'] = (self.df['num_unregistrations'] > 0).astype(int)
        
        # Study behavior composite
        if 'avg_score' in self.df.columns and 'total_clicks' in self.df.columns:
            # Normalize both to 0-1 scale then average
            score_norm = (self.df['avg_score'] - self.df['avg_score'].min()) / (self.df['avg_score'].max() - self.df['avg_score'].min() + 1e-6)
            clicks_norm = (self.df['total_clicks'] - self.df['total_clicks'].min()) / (self.df['total_clicks'].max() - self.df['total_clicks'].min() + 1e-6)
            self.df['study_intensity'] = (score_norm + clicks_norm) / 2
        
        logger.info(f"Created derived features. New shape: {self.df.shape}")
        
        return self.df
    
    def apply_zscore_standardization(self, features_to_standardize: List[str] = None) -> pd.DataFrame:
        """
        Apply z-score standardization by cohort (course + presentation).
        
        This is a key technique from the paper - standardize relative to peers
        rather than absolute values.
        
        Args:
            features_to_standardize: List of feature names to standardize
            
        Returns:
            DataFrame with z-score standardized features
        """
        logger.info("Applying z-score standardization by cohort...")
        
        # Default features to standardize (numeric performance metrics)
        if features_to_standardize is None:
            features_to_standardize = [
                'avg_score', 'score_std', 'min_score', 'max_score',
                'total_clicks', 'avg_clicks_per_day', 'num_days_active',
                'num_unique_resources', 'clicks_per_active_day',
                'resource_diversity', 'submission_rate', 'study_intensity'
            ]
        
        # Only use features that exist in dataframe
        features_to_standardize = [f for f in features_to_standardize if f in self.df.columns]
        
        # Group by cohort (course + presentation)
        groupby_cols = ['code_module', 'code_presentation']
        
        for feature in features_to_standardize:
            # Calculate cohort mean and std
            cohort_stats = self.df.groupby(groupby_cols)[feature].agg(['mean', 'std']).reset_index()
            cohort_stats.columns = groupby_cols + [f'{feature}_mean', f'{feature}_std']
            
            # Merge stats back to main df
            self.df = self.df.merge(cohort_stats, on=groupby_cols, how='left')
            
            # Calculate z-score
            self.df[f'{feature}_z'] = np.where(
                self.df[f'{feature}_std'] > 0,
                (self.df[feature] - self.df[f'{feature}_mean']) / self.df[f'{feature}_std'],
                0  # If std is 0, z-score is 0
            )
            
            # Store params for later conversion back to raw values
            self.z_score_params[feature] = {
                'mean_col': f'{feature}_mean',
                'std_col': f'{feature}_std'
            }
            
            logger.info(f"Standardized {feature} -> {feature}_z")
        
        logger.info(f"Z-score standardization complete. Shape: {self.df.shape}")
        
        return self.df
    
    def get_feature_columns(self) -> Dict[str, List[str]]:
        """
        Get organized lists of feature columns.
        
        Returns:
            Dictionary with categorized feature lists
        """
        feature_cols = {
            'target': ['is_at_risk'],
            'identifiers': ['id_student', 'code_module', 'code_presentation'],
            'demographic': [col for col in self.df.columns if '_encoded' in col and 
                          any(x in col for x in ['gender', 'region', 'education', 'imd', 'age', 'disability'])],
            'academic_raw': [col for col in self.df.columns if 
                           any(x in col for x in ['score', 'assessment']) and '_z' not in col and 'mean' not in col and 'std' not in col],
            'vle_raw': [col for col in self.df.columns if 
                       any(x in col for x in ['click', 'vle', 'resource', 'engagement']) and '_z' not in col and 'mean' not in col and 'std' not in col],
            'behavioral': [col for col in self.df.columns if 
                         any(x in col for x in ['late', 'early', 'unregistration', 'submission_rate'])],
            'z_score_features': [col for col in self.df.columns if col.endswith('_z')]
        }
        
        return feature_cols
    
    def prepare_modeling_data(self) -> Tuple[pd.DataFrame, List[str], List[str]]:
        """
        Prepare final dataset for modeling.
        
        Returns:
            Tuple of (DataFrame, feature_columns, target_column)
        """
        logger.info("Preparing data for modeling...")
        
        feature_cols = self.get_feature_columns()
        
        # Select features for modeling (z-scores + demographics + behavioral)
        modeling_features = (
            feature_cols['z_score_features'] +
            feature_cols['demographic'] +
            feature_cols['behavioral']
        )
        
        # Remove any features with all NaN or constant values
        valid_features = []
        seen_features = set()
        for col in modeling_features:
            if col in self.df.columns and col not in seen_features:
                if self.df[col].notna().sum() > 0 and self.df[col].nunique() > 1:
                    valid_features.append(col)
                    seen_features.add(col)
                else:
                    logger.warning(f"Dropping {col} - constant or all NaN")
            elif col in seen_features:
                logger.warning(f"Skipping duplicate feature: {col}")
        
        # Create final dataframe
        final_cols = ['id_student', 'code_module', 'code_presentation'] + valid_features + ['is_at_risk']
        final_df = self.df[final_cols].copy()
        
        # Fill any remaining NaN with 0
        existing_features = [col for col in valid_features if col in final_df.columns]
        if existing_features:
            # Fill NaN values in place to avoid shape mismatch
            for col in existing_features:
                final_df[col] = final_df[col].fillna(0)
        
        logger.info(f"Final modeling data: {final_df.shape}")
        logger.info(f"Number of features: {len(valid_features)}")
        
        return final_df, valid_features, 'is_at_risk'
    
    def convert_zscore_to_raw(self, z_score: float, feature_name: str, 
                             cohort_mean: float, cohort_std: float) -> float:
        """
        Convert z-score back to raw value.
        
        Args:
            z_score: Z-score value
            feature_name: Original feature name
            cohort_mean: Mean of the cohort
            cohort_std: Standard deviation of the cohort
            
        Returns:
            Raw value
        """
        return z_score * cohort_std + cohort_mean


def engineer_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, FeatureEngineer]:
    """
    Convenience function to engineer all features.
    
    Args:
        df: Preprocessed DataFrame
        
    Returns:
        Tuple of (engineered DataFrame, FeatureEngineer instance)
    """
    engineer = FeatureEngineer(df)
    
    # Apply all transformations
    engineer.encode_categorical_features()
    engineer.create_derived_features()
    engineer.apply_zscore_standardization()
    
    return engineer.df, engineer


if __name__ == "__main__":
    # Test feature engineering
    from loader import load_oulad_data
    from preprocessing import preprocess_oulad_data
    
    print("Loading and preprocessing data...")
    data, _ = load_oulad_data()
    merged_df = preprocess_oulad_data(data)
    
    print("\nEngineering features...")
    engineered_df, engineer = engineer_features(merged_df)
    
    print(f"\nEngineered dataset shape: {engineered_df.shape}")
    
    # Get modeling data
    final_df, features, target = engineer.prepare_modeling_data()
    print(f"\nFinal modeling data: {final_df.shape}")
    print(f"Features: {len(features)}")
    print(f"Target: {target}")
    
    print(f"\nTarget distribution:")
    print(final_df[target].value_counts())

