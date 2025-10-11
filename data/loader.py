"""
Data loader module for OULAD dataset.

This module handles loading and basic preprocessing of the OULAD dataset files.
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OULADLoader:
    """Load and merge OULAD dataset files."""
    
    def __init__(self, dataset_path: str = "OULAD dataset"):
        """
        Initialize loader with dataset path.
        
        Args:
            dataset_path: Path to OULAD dataset folder
        """
        self.dataset_path = dataset_path
        self.data = {}
        
    def load_all_files(self) -> Dict[str, pd.DataFrame]:
        """
        Load all OULAD CSV files.
        
        Returns:
            Dictionary with filename as key and DataFrame as value
        """
        files = {
            'studentInfo': 'studentInfo.csv',
            'studentAssessment': 'studentAssessment.csv', 
            'assessments': 'assessments.csv',
            'studentRegistration': 'studentRegistration.csv',
            'studentVle': 'studentVle.csv',
            'vle': 'vle.csv',
            'courses': 'courses.csv'
        }
        
        logger.info(f"Loading OULAD files from {self.dataset_path}")
        
        for name, filename in files.items():
            filepath = os.path.join(self.dataset_path, filename)
            
            if not os.path.exists(filepath):
                logger.warning(f"File not found: {filepath}")
                continue
                
            try:
                # Handle large file differently
                if filename == 'studentVle.csv':
                    logger.info("Loading large studentVle file...")
                    df = pd.read_csv(filepath, chunksize=10000)
                    # For now, just load first chunk for testing
                    df = next(df)
                else:
                    df = pd.read_csv(filepath)
                    
                self.data[name] = df
                logger.info(f"Loaded {name}: {df.shape}")
                
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
                
        return self.data
    
    def get_dataset_info(self) -> Dict[str, dict]:
        """
        Get basic info about loaded datasets.
        
        Returns:
            Dictionary with dataset info
        """
        info = {}
        
        for name, df in self.data.items():
            info[name] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'missing_values': df.isnull().sum().to_dict()
            }
            
        return info
    
    def create_target_variable(self) -> pd.DataFrame:
        """
        Create binary target variable from final_result.
        
        Returns:
            DataFrame with is_at_risk column
        """
        if 'studentInfo' not in self.data:
            raise ValueError("studentInfo not loaded")
            
        df = self.data['studentInfo'].copy()
        
        # Create binary target: 1 = at-risk (Fail/Withdrawn), 0 = safe (Pass/Distinction)
        df['is_at_risk'] = df['final_result'].apply(
            lambda x: 1 if x in ['Fail', 'Withdrawn'] else 0
        )
        
        logger.info(f"Target variable created. Distribution:")
        logger.info(df['is_at_risk'].value_counts())
        
        return df


def load_oulad_data(dataset_path: str = "OULAD dataset") -> Tuple[Dict[str, pd.DataFrame], Dict[str, dict]]:
    """
    Convenience function to load OULAD data.
    
    Args:
        dataset_path: Path to dataset folder
        
    Returns:
        Tuple of (data_dict, info_dict)
    """
    loader = OULADLoader(dataset_path)
    data = loader.load_all_files()
    info = loader.get_dataset_info()
    
    return data, info


if __name__ == "__main__":
    # Test the loader
    print("Testing OULAD data loader...")
    
    try:
        data, info = load_oulad_data()
        
        print(f"\nLoaded {len(data)} files:")
        for name, df in data.items():
            print(f"- {name}: {df.shape}")
            
        # Show target distribution
        if 'studentInfo' in data:
            loader = OULADLoader()
            loader.data = data
            student_df = loader.create_target_variable()
            
            print(f"\nTarget distribution:")
            print(student_df['final_result'].value_counts())
            print(f"\nBinary target (is_at_risk):")
            print(student_df['is_at_risk'].value_counts())
            
    except Exception as e:
        print(f"Error: {e}")
