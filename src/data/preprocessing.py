"""
Data preprocessing module for OULAD dataset.

This module handles data cleaning, merging, and initial feature engineering.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OULADPreprocessor:
    """Preprocess and merge OULAD dataset tables."""
    
    def __init__(self, data_dict: Dict[str, pd.DataFrame]):
        """
        Initialize preprocessor with loaded data.
        
        Args:
            data_dict: Dictionary of DataFrames from OULADLoader
        """
        self.data = data_dict
        self.merged_df = None
        
    def clean_data(self) -> Dict[str, pd.DataFrame]:
        """
        Clean all datasets - handle missing values, outliers, etc.
        
        Returns:
            Dictionary of cleaned DataFrames
        """
        logger.info("Starting data cleaning...")
        
        cleaned = {}
        
        for name, df in self.data.items():
            df_clean = df.copy()
            
            # Log missing values
            missing = df_clean.isnull().sum()
            if missing.sum() > 0:
                logger.info(f"{name} missing values:\n{missing[missing > 0]}")
            
            # Handle specific cleaning per table
            if name == 'studentInfo':
                # Fill missing IMD_band with mode
                if 'imd_band' in df_clean.columns and df_clean['imd_band'].isnull().any():
                    df_clean['imd_band'].fillna(df_clean['imd_band'].mode()[0], inplace=True)
                
            elif name == 'studentAssessment':
                # Fill missing scores with 0 (assumed not submitted)
                if 'score' in df_clean.columns:
                    df_clean['score'].fillna(0, inplace=True)
                    
            elif name == 'studentVle':
                # Fill missing sum_click with 0
                if 'sum_click' in df_clean.columns:
                    df_clean['sum_click'].fillna(0, inplace=True)
                    
            cleaned[name] = df_clean
            logger.info(f"Cleaned {name}: {df_clean.shape}")
        
        self.data = cleaned
        return cleaned
    
    def create_target_variable(self, student_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create binary target variable from final_result.
        
        Args:
            student_df: studentInfo DataFrame
            
        Returns:
            DataFrame with is_at_risk column
        """
        df = student_df.copy()
        
        # Create binary target: 1 = at-risk (Fail/Withdrawn), 0 = safe (Pass/Distinction)
        if 'final_result' in df.columns:
            df['is_at_risk'] = df['final_result'].apply(
                lambda x: 1 if x in ['Fail', 'Withdrawn'] else 0
            )
        else:
            logger.warning("final_result column not found, creating dummy target variable")
            df['is_at_risk'] = 0  # Default to safe
        
        logger.info(f"Target variable created:")
        logger.info(f"At-risk: {df['is_at_risk'].sum()} ({df['is_at_risk'].mean():.2%})")
        logger.info(f"Safe: {(df['is_at_risk']==0).sum()} ({(df['is_at_risk']==0).mean():.2%})")
        
        return df
    
    def aggregate_assessment_features(self) -> pd.DataFrame:
        """
        Create assessment-related features from studentAssessment table.
        
        Returns:
            DataFrame with aggregated assessment features per student
        """
        logger.info("Creating assessment features...")
        
        if 'studentAssessment' not in self.data or self.data['studentAssessment'].empty:
            logger.warning("studentAssessment data not found")
            return pd.DataFrame()
        
        student_assess = self.data['studentAssessment']
        
        if 'assessments' not in self.data or self.data['assessments'].empty:
            logger.warning("assessments data not found, using studentAssessment only")
            assessments = None
        else:
            assessments = self.data['assessments']
        
        # Merge to get assessment metadata
        if assessments is not None:
            assess_merged = student_assess.merge(
                assessments,
                on='id_assessment',  # Only merge on id_assessment
                how='left'
            )
        else:
            assess_merged = student_assess.copy()
        
        # Check if required columns exist
        required_cols = ['id_student', 'code_module', 'code_presentation']
        if not all(col in assess_merged.columns for col in required_cols):
            logger.warning(f"Missing required columns: {required_cols}")
            return pd.DataFrame()
        
        # Calculate weighted average if weight column exists
        if 'weight' in assess_merged.columns:
            logger.info("Calculating weighted assessment averages...")
            
            # Calculate weighted average per student
            def weighted_avg(group):
                # Filter out rows with missing score or weight
                valid = group.dropna(subset=['score', 'weight'])
                if len(valid) == 0 or valid['weight'].sum() == 0:
                    return pd.Series({'weighted_avg_score': None})
                return pd.Series({
                    'weighted_avg_score': (valid['score'] * valid['weight']).sum() / valid['weight'].sum()
                })
            
            weighted_scores = assess_merged.groupby(required_cols).apply(weighted_avg).reset_index()
        else:
            weighted_scores = None
            logger.warning("Weight column not found, using simple average")
        
        # Aggregate by student
        agg_features = assess_merged.groupby(required_cols).agg({
            'score': ['mean', 'std', 'min', 'max', 'count'],
            'date': lambda x: (x < 0).sum(),  # Number of late submissions (negative dates)
        }).reset_index()
        
        # Flatten column names
        agg_features.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                                for col in agg_features.columns.values]
        
        # Merge weighted scores if available
        if weighted_scores is not None:
            agg_features = agg_features.merge(weighted_scores, on=required_cols, how='left')
            # Use weighted average as primary, fall back to simple mean
            agg_features['avg_score_final'] = agg_features['weighted_avg_score'].fillna(agg_features['score_mean'])
        else:
            agg_features['avg_score_final'] = agg_features['score_mean']
        
        # Rename for clarity
        agg_features.rename(columns={
            'score_mean': 'simple_avg_score',
            'avg_score_final': 'avg_score',  # This is the primary score to use
            'score_std': 'score_std',
            'score_min': 'min_score',
            'score_max': 'max_score',
            'score_count': 'num_assessments',
            'date_<lambda>': 'num_late_submissions'
        }, inplace=True)
        
        logger.info(f"Assessment features created: {agg_features.shape}")
        
        return agg_features
    
    def aggregate_vle_features(self) -> pd.DataFrame:
        """
        Create VLE engagement features from studentVle table.
        
        Returns:
            DataFrame with aggregated VLE features per student
        """
        logger.info("Creating VLE engagement features...")
        
        if 'studentVle' not in self.data or self.data['studentVle'].empty:
            logger.warning("studentVle data not found")
            return pd.DataFrame()
        
        student_vle = self.data['studentVle']
        
        # Check if required columns exist
        required_cols = ['id_student', 'code_module', 'code_presentation']
        if not all(col in student_vle.columns for col in required_cols):
            logger.warning(f"Missing required columns in VLE data: {required_cols}")
            return pd.DataFrame()
        
        # Aggregate by student
        vle_features = student_vle.groupby(required_cols).agg({
            'sum_click': ['sum', 'mean', 'std', 'max'],
            'date': ['min', 'max', 'count'],  # First access, last access, num days active
            'id_site': 'nunique'  # Number of unique resources accessed
        }).reset_index()
        
        # Flatten column names
        vle_features.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                                for col in vle_features.columns.values]
        
        # Rename for clarity
        vle_features.rename(columns={
            'sum_click_sum': 'total_clicks',
            'sum_click_mean': 'avg_clicks_per_day',
            'sum_click_std': 'std_clicks',
            'sum_click_max': 'max_clicks_per_day',
            'date_min': 'first_vle_access',
            'date_max': 'last_vle_access',
            'date_count': 'num_days_active',
            'id_site_nunique': 'num_unique_resources'
        }, inplace=True)
        
        # Create engagement duration
        vle_features['engagement_duration'] = vle_features['last_vle_access'] - vle_features['first_vle_access']
        
        logger.info(f"VLE features created: {vle_features.shape}")
        
        return vle_features
    
    def aggregate_registration_features(self) -> pd.DataFrame:
        """
        Create registration-related features.
        
        Returns:
            DataFrame with registration features per student
        """
        logger.info("Creating registration features...")
        
        if 'studentRegistration' not in self.data or self.data['studentRegistration'].empty:
            logger.warning("studentRegistration data not found")
            return pd.DataFrame()
        
        student_reg = self.data['studentRegistration']
        
        # Check if required columns exist
        required_cols = ['id_student', 'code_module', 'code_presentation']
        if not all(col in student_reg.columns for col in required_cols):
            logger.warning(f"Missing required columns in registration data: {required_cols}")
            return pd.DataFrame()
        
        # Group by student and create registration features
        reg_features = student_reg.groupby(required_cols).agg({
            'date_registration': 'first',
            'date_unregistration': lambda x: x.notna().sum()  # Count unregistrations
        }).reset_index()
        
        # Create early/late registration features
        # Negative dates = early registration (before course start)
        # Positive dates = late registration (after course start)
        reg_features['registration_date'] = reg_features['date_registration']
        reg_features['registered_early'] = (reg_features['date_registration'] < 0).astype(int)
        reg_features['days_before_start'] = reg_features['date_registration'].apply(
            lambda x: abs(x) if x < 0 else 0
        )
        reg_features['days_after_start'] = reg_features['date_registration'].apply(
            lambda x: x if x > 0 else 0
        )
        
        # Rename columns
        reg_features.rename(columns={
            'date_unregistration': 'num_unregistrations'
        }, inplace=True)
        
        # Drop original date_registration column (we have registration_date now)
        if 'date_registration' in reg_features.columns and 'registration_date' in reg_features.columns:
            reg_features = reg_features.drop(columns=['date_registration'])
        
        logger.info(f"Registration features created: {reg_features.shape}")
        logger.info(f"  - Students registered early: {reg_features['registered_early'].sum()}")
        logger.info(f"  - Average days before start (early): {reg_features['days_before_start'].mean():.1f}")
        logger.info(f"  - Average days after start (late): {reg_features['days_after_start'].mean():.1f}")
        
        return reg_features
    
    def merge_all_tables(self) -> pd.DataFrame:
        """
        Merge all tables into a single DataFrame with all features.
        
        Returns:
            Merged DataFrame ready for feature engineering
        """
        logger.info("Merging all tables...")
        
        # Start with studentInfo
        student_info = self.data['studentInfo'].copy()
        
        # Create target variable
        student_info = self.create_target_variable(student_info)
        
        # Create aggregated features
        assess_features = self.aggregate_assessment_features()
        vle_features = self.aggregate_vle_features()
        reg_features = self.aggregate_registration_features()
        
        # Merge everything
        merged = student_info.copy()
        
        # Merge assessment features
        if not assess_features.empty:
            logger.info(f"Merging assessment features: {assess_features.shape}")
            merged = merged.merge(
                assess_features,
                on=['id_student', 'code_module', 'code_presentation'],
                how='left'
            )
        else:
            logger.warning("Assessment features empty or missing merge keys")
        
        # Merge VLE features
        if not vle_features.empty:
            logger.info(f"Merging VLE features: {vle_features.shape}")
            merged = merged.merge(
                vle_features,
                on=['id_student', 'code_module', 'code_presentation'],
                how='left'
            )
        else:
            logger.warning("VLE features empty or missing merge keys")
        
        # Merge registration features
        if not reg_features.empty:
            logger.info(f"Merging registration features: {reg_features.shape}")
            merged = merged.merge(
                reg_features,
                on=['id_student', 'code_module', 'code_presentation'],
                how='left'
            )
        else:
            logger.warning("Registration features empty or missing merge keys")
        
        # Fill NaN values (students with no activity)
        numeric_cols = merged.select_dtypes(include=[np.number]).columns
        merged[numeric_cols] = merged[numeric_cols].fillna(0)
        
        logger.info(f"Final merged dataset: {merged.shape}")
        logger.info(f"Columns: {list(merged.columns)}")
        
        self.merged_df = merged
        return merged
    
    def get_feature_summary(self) -> pd.DataFrame:
        """
        Get summary statistics of all features.
        
        Returns:
            DataFrame with feature statistics
        """
        if self.merged_df is None:
            raise ValueError("No merged data available. Run merge_all_tables() first.")
        
        return self.merged_df.describe()


def preprocess_oulad_data(data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Convenience function to preprocess OULAD data.
    
    Args:
        data_dict: Dictionary of loaded DataFrames
        
    Returns:
        Merged and preprocessed DataFrame
    """
    preprocessor = OULADPreprocessor(data_dict)
    preprocessor.clean_data()
    merged_df = preprocessor.merge_all_tables()
    
    return merged_df


if __name__ == "__main__":
    # Test preprocessing
    from loader import load_oulad_data
    
    print("Loading data...")
    data, info = load_oulad_data()
    
    print("\nPreprocessing...")
    merged_df = preprocess_oulad_data(data)
    
    print(f"\nFinal dataset shape: {merged_df.shape}")
    print(f"\nFeature summary:")
    print(merged_df.describe())
    
    print(f"\nTarget distribution:")
    print(merged_df['is_at_risk'].value_counts())

