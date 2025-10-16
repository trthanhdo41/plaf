"""
Cold Start Handler for New Students

Handle predictions for students without historical data using demographic-based approach.
"""

import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ColdStartHandler:
    """Handle cold start problem for new students."""
    
    def __init__(self, historical_data: pd.DataFrame):
        """
        Initialize cold start handler.
        
        Args:
            historical_data: DataFrame with student demographics and outcomes
        """
        self.historical_data = historical_data
        self.demographic_features = [
            'gender', 'region', 'highest_education',
            'imd_band', 'age_band', 'disability'
        ]
        self.label_encoders = {}
        self.knn_model = None
        self.feature_matrix = None
        
        self._prepare_demographic_model()
    
    def _prepare_demographic_model(self):
        """Prepare demographic-based similarity model."""
        logger.info("Preparing demographic model for cold start...")
        
        # Check if demographic features exist
        available_features = [f for f in self.demographic_features 
                            if f in self.historical_data.columns]
        
        if not available_features:
            logger.warning("No demographic features found in data")
            return
        
        self.demographic_features = available_features
        
        # Encode categorical features
        encoded_data = self.historical_data[self.demographic_features].copy()
        
        for feature in self.demographic_features:
            le = LabelEncoder()
            encoded_data[feature] = le.fit_transform(
                encoded_data[feature].astype(str).fillna('Unknown')
            )
            self.label_encoders[feature] = le
        
        # Create feature matrix for KNN
        self.feature_matrix = encoded_data.values
        
        # Train KNN model (cosine similarity)
        self.knn_model = NearestNeighbors(
            n_neighbors=min(20, len(self.historical_data)),
            metric='euclidean'
        )
        self.knn_model.fit(self.feature_matrix)
        
        logger.info(f"Cold start model ready with {len(self.demographic_features)} features")
    
    def predict_new_student(
        self, 
        student_demographics: Dict,
        k_neighbors: int = 10,
        return_confidence: bool = True
    ) -> Dict:
        """
        Predict risk for new student based on demographics.
        
        Args:
            student_demographics: Dict with demographic info
            k_neighbors: Number of similar students to consider
            return_confidence: Whether to return prediction confidence
            
        Returns:
            Dict with prediction and confidence
        """
        if self.knn_model is None:
            logger.warning("Cold start model not initialized")
            return {
                'risk_probability': 0.5,  # Default neutral prediction
                'confidence': 0.0,
                'method': 'default'
            }
        
        # Encode input demographics
        try:
            encoded_input = []
            for feature in self.demographic_features:
                value = str(student_demographics.get(feature, 'Unknown'))
                
                # Handle unseen categories
                if value in self.label_encoders[feature].classes_:
                    encoded_value = self.label_encoders[feature].transform([value])[0]
                else:
                    # Use most common value for unseen category
                    encoded_value = 0
                
                encoded_input.append(encoded_value)
            
            encoded_input = np.array(encoded_input).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error encoding demographics: {e}")
            return {
                'risk_probability': 0.5,
                'confidence': 0.0,
                'method': 'error'
            }
        
        # Find K nearest neighbors
        distances, indices = self.knn_model.kneighbors(
            encoded_input, 
            n_neighbors=min(k_neighbors, len(self.historical_data))
        )
        
        # Get outcomes of similar students
        similar_students = self.historical_data.iloc[indices[0]]
        
        # Calculate weighted average risk
        # Closer students have more weight
        weights = 1 / (distances[0] + 1e-6)  # Avoid division by zero
        weights = weights / weights.sum()  # Normalize
        
        # Get risk probabilities
        if 'risk_probability' in similar_students.columns:
            risk_probs = similar_students['risk_probability'].values
        elif 'is_at_risk' in similar_students.columns:
            risk_probs = similar_students['is_at_risk'].values
        else:
            logger.warning("No risk information in historical data")
            return {
                'risk_probability': 0.5,
                'confidence': 0.0,
                'method': 'no_risk_data'
            }
        
        # Weighted prediction
        predicted_risk = np.average(risk_probs, weights=weights)
        
        # Calculate confidence based on agreement of neighbors
        # High variance = low confidence
        neighbor_variance = np.var(risk_probs)
        confidence = 1.0 - min(neighbor_variance * 2, 1.0)  # Scale to 0-1
        
        # Adjust confidence based on average distance
        avg_distance = distances[0].mean()
        max_distance = np.sqrt(len(self.demographic_features))  # Max possible distance
        distance_confidence = 1.0 - (avg_distance / max_distance)
        
        # Combined confidence
        final_confidence = (confidence + distance_confidence) / 2
        
        result = {
            'risk_probability': float(predicted_risk),
            'confidence': float(final_confidence),
            'method': 'demographic_knn',
            'n_neighbors': k_neighbors,
            'similar_students_count': len(similar_students)
        }
        
        if return_confidence:
            result['neighbor_distances'] = distances[0].tolist()
            result['neighbor_risk_variance'] = float(neighbor_variance)
        
        return result
    
    def get_similar_students(
        self, 
        student_demographics: Dict,
        k: int = 5
    ) -> pd.DataFrame:
        """
        Get K most similar students based on demographics.
        
        Args:
            student_demographics: Dict with demographic info
            k: Number of similar students to return
            
        Returns:
            DataFrame of similar students
        """
        if self.knn_model is None:
            return pd.DataFrame()
        
        # Encode input
        encoded_input = []
        for feature in self.demographic_features:
            value = str(student_demographics.get(feature, 'Unknown'))
            if value in self.label_encoders[feature].classes_:
                encoded_value = self.label_encoders[feature].transform([value])[0]
            else:
                encoded_value = 0
            encoded_input.append(encoded_value)
        
        encoded_input = np.array(encoded_input).reshape(1, -1)
        
        # Find neighbors
        distances, indices = self.knn_model.kneighbors(
            encoded_input,
            n_neighbors=min(k, len(self.historical_data))
        )
        
        # Return similar students
        similar = self.historical_data.iloc[indices[0]].copy()
        similar['similarity_distance'] = distances[0]
        
        return similar
    
    def predict_batch(
        self,
        students_demographics: List[Dict],
        k_neighbors: int = 10
    ) -> List[Dict]:
        """
        Batch prediction for multiple new students.
        
        Args:
            students_demographics: List of demographic dicts
            k_neighbors: Number of neighbors to use
            
        Returns:
            List of prediction dicts
        """
        predictions = []
        
        for student_demo in students_demographics:
            pred = self.predict_new_student(
                student_demo,
                k_neighbors=k_neighbors,
                return_confidence=True
            )
            predictions.append(pred)
        
        return predictions
    
    def evaluate_cold_start_performance(
        self,
        test_data: pd.DataFrame,
        k_neighbors: int = 10
    ) -> Dict:
        """
        Evaluate cold start prediction performance.
        
        Args:
            test_data: DataFrame with demographics and actual outcomes
            k_neighbors: Number of neighbors to use
            
        Returns:
            Dict with evaluation metrics
        """
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        
        predictions = []
        actuals = []
        
        for idx, row in test_data.iterrows():
            # Create demographic dict
            demo = {feat: row[feat] for feat in self.demographic_features 
                   if feat in row}
            
            # Predict
            pred = self.predict_new_student(demo, k_neighbors=k_neighbors)
            predictions.append(pred['risk_probability'])
            
            # Get actual
            if 'risk_probability' in row:
                actuals.append(row['risk_probability'])
            elif 'is_at_risk' in row:
                actuals.append(row['is_at_risk'])
        
        # Calculate metrics
        mae = mean_absolute_error(actuals, predictions)
        rmse = np.sqrt(mean_squared_error(actuals, predictions))
        
        # Calculate accuracy for binary classification
        binary_preds = [1 if p > 0.5 else 0 for p in predictions]
        binary_actuals = [1 if a > 0.5 else 0 for a in actuals]
        accuracy = sum([p == a for p, a in zip(binary_preds, binary_actuals)]) / len(actuals)
        
        return {
            'mae': mae,
            'rmse': rmse,
            'accuracy': accuracy,
            'n_samples': len(test_data)
        }


def create_cold_start_handler(data_path: str = None) -> ColdStartHandler:
    """
    Factory function to create cold start handler.
    
    Args:
        data_path: Path to historical data CSV
        
    Returns:
        Initialized ColdStartHandler
    """
    if data_path:
        historical_data = pd.read_csv(data_path)
    else:
        # Load from database or default location
        try:
            historical_data = pd.read_csv('data/processed/student_predictions.csv')
        except FileNotFoundError:
            logger.warning("No historical data found, using empty handler")
            historical_data = pd.DataFrame()
    
    return ColdStartHandler(historical_data)


if __name__ == "__main__":
    # Test cold start handler
    print("="*70)
    print("COLD START HANDLER TEST")
    print("="*70)
    
    # Create sample historical data
    sample_data = pd.DataFrame({
        'gender': ['M', 'F', 'M', 'F', 'M'] * 20,
        'region': ['Region A', 'Region B', 'Region A', 'Region C', 'Region B'] * 20,
        'highest_education': ['Bachelor', 'Master', 'Bachelor', 'PhD', 'Bachelor'] * 20,
        'imd_band': ['10-20%', '20-30%', '10-20%', '30-40%', '20-30%'] * 20,
        'age_band': ['0-35', '35-55', '0-35', '55+', '35-55'] * 20,
        'disability': ['N', 'N', 'Y', 'N', 'N'] * 20,
        'risk_probability': [0.3, 0.7, 0.4, 0.8, 0.2] * 20,
        'is_at_risk': [0, 1, 0, 1, 0] * 20
    })
    
    # Initialize handler
    handler = ColdStartHandler(sample_data)
    
    # Test prediction for new student
    new_student = {
        'gender': 'M',
        'region': 'Region A',
        'highest_education': 'Bachelor',
        'imd_band': '10-20%',
        'age_band': '0-35',
        'disability': 'N'
    }
    
    print("\nPredicting risk for new student:")
    print(f"Demographics: {new_student}")
    
    prediction = handler.predict_new_student(new_student, k_neighbors=5)
    
    print(f"\nPrediction Results:")
    print(f"  Risk Probability: {prediction['risk_probability']:.3f}")
    print(f"  Confidence: {prediction['confidence']:.3f}")
    print(f"  Method: {prediction['method']}")
    print(f"  N Neighbors: {prediction['n_neighbors']}")
    
    # Get similar students
    similar = handler.get_similar_students(new_student, k=3)
    print(f"\nMost similar students:")
    print(similar[['gender', 'region', 'highest_education', 'risk_probability', 'similarity_distance']].head())
    
    print("\n[SUCCESS] Cold start handler test completed!")

