"""
Explainability Bridge: Connects SHAP/DiCE to RAG System
Implementation of Section 5 from SYSTEM_IMPROVEMENT_ANALYSIS.md
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
import os
import joblib
from src.explainability.shap_explainer import SHAPExplainer
from src.prescriptive.dice_explainer import CounterfactualGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExplainabilityBridge:
    """Bridge between explainability (SHAP/DiCE) and RAG system"""
    
    def __init__(self):
        """Initialize explainability bridge"""
        self.model = None
        self.shap_explainer = None
        self.dice_explainer = None
        self.feature_names = None
        self.modeling_data = None
        self.load_model_and_explainers()
    
    def load_model_and_explainers(self):
        """Load trained model and create explainers"""
        try:
            # Load model
            model_path = 'models/best_model.pkl'
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                if isinstance(model_data, dict) and 'model' in model_data:
                    self.model = model_data['model']
                else:
                    self.model = model_data
                logger.info(f"Loaded model from {model_path}")
            else:
                logger.warning(f"Model not found at {model_path}")
                return
            
            # Load modeling data for SHAP background and student lookup
            data_path = 'data/features/modeling_data.csv'
            if os.path.exists(data_path):
                self.modeling_data = pd.read_csv(data_path)
                logger.info(f"Loaded modeling data with {len(self.modeling_data)} students")
                
                # Load feature names or infer from data
                feature_path = 'models/feature_names.pkl'
                if os.path.exists(feature_path):
                    self.feature_names = joblib.load(feature_path)
                    logger.info(f"Loaded {len(self.feature_names)} feature names from file")
                else:
                    # Infer features: all columns except identifiers and target
                    excluded_cols = ['id_student', 'code_module', 'code_presentation', 'is_at_risk']
                    self.feature_names = [col for col in self.modeling_data.columns if col not in excluded_cols]
                    logger.info(f"Inferred {len(self.feature_names)} feature names from data")
                
                # Initialize SHAP explainer with background data
                if self.model is not None and self.feature_names is not None:
                    # Use a sample for background data
                    X_background = self.modeling_data[self.feature_names].sample(min(100, len(self.modeling_data)), random_state=42)
                    self.shap_explainer = SHAPExplainer(self.model, X_background, self.feature_names)
                    self.shap_explainer.create_explainer()
                    logger.info("Initialized SHAP explainer")
                    
                    # Initialize DiCE explainer
                    try:
                        continuous_features = [f for f in self.feature_names if f.endswith('_z')]
                        X_train = self.modeling_data[self.feature_names]
                        y_train = self.modeling_data['is_at_risk']
                        
                        self.dice_explainer = CounterfactualGenerator(
                            self.model, X_train, y_train,
                            self.feature_names, continuous_features
                        )
                        # Defer setup_dice() until needed to save startup time
                        logger.info("Initialized DiCE explainer (lazy loading)")
                    except Exception as e:
                        logger.warning(f"Failed to initialize DiCE: {e}")
            else:
                logger.warning(f"Modeling data not found at {data_path}")
            
        except Exception as e:
            logger.error(f"Failed to load model/explainers: {e}")
            import traceback
            traceback.print_exc()
    
    def get_student_shap_explanation(self, student_data: Dict) -> Dict:
        """
        Get SHAP explanation for a student using REAL model values
        
        Args:
            student_data: Student features dictionary
            
        Returns:
            Dictionary with top risk factors and their SHAP values
        """
        try:
            student_id = student_data.get('id_student')
            
            if self.model is None or self.feature_names is None or self.shap_explainer is None:
                logger.warning("Model or explainer not loaded, using fallback")
                return self._generate_fallback_explanation(student_data)
            
            # 1. Try to find student in modeling data (best for existing students)
            student_features = None
            if self.modeling_data is not None and student_id:
                student_row = self.modeling_data[self.modeling_data['id_student'] == student_id]
                if not student_row.empty:
                    student_features = student_row[self.feature_names]
            
            # 2. If not found, try to construct from student_data (harder due to z-scores)
            if student_features is None:
                logger.warning(f"Student {student_id} not found in modeling data, using fallback")
                return self._generate_fallback_explanation(student_data)
            
            # 3. Calculate REAL SHAP values
            shap_values = self.shap_explainer.explainer.shap_values(student_features)
            
            # Handle different SHAP return types (list for classification, array for regression)
            if isinstance(shap_values, list):
                # Binary classification: index 1 is positive class (at-risk)
                shap_values = shap_values[1]
            
            # Flatten if needed
            if len(shap_values.shape) > 1:
                shap_values = shap_values[0]
                
            # Get feature values
            feature_values = student_features.iloc[0].values
            
            # Create risk factors list
            risk_factors = []
            
            # Get risk probability from model
            risk_probability = self.model.predict_proba(student_features)[0][1]
            
            for i, feature_name in enumerate(self.feature_names):
                shap_val = shap_values[i]
                feat_val = feature_values[i]
                
                # Skip negligible contributions
                if abs(shap_val) < 0.01:
                    continue
                
                # Determine impact direction
                impact_direction = 'increases_risk' if shap_val > 0 else 'decreases_risk'
                
                # Create human-readable explanation
                explanation = self._generate_natural_language_explanation(feature_name, feat_val, shap_val)
                
                risk_factors.append({
                    'feature': feature_name,
                    'feature_name': self._prettify_feature_name(feature_name),
                    'value': float(feat_val),
                    'shap_value': float(shap_val),
                    'impact_direction': impact_direction,
                    'explanation': explanation['text'],
                    'recommendation': explanation['recommendation']
                })
            
            # Sort by absolute SHAP value (impact)
            risk_factors.sort(key=lambda x: abs(x['shap_value']), reverse=True)
            
            # Calculate impact percentages
            total_impact = sum(abs(f['shap_value']) for f in risk_factors)
            for factor in risk_factors:
                if total_impact > 0:
                    factor['impact_percentage'] = (abs(factor['shap_value']) / total_impact) * 100
                else:
                    factor['impact_percentage'] = 0
            
            # Generate interpretation
            interpretation = f"Student has {risk_probability*100:.1f}% risk probability. "
            if risk_probability > 0.7:
                interpretation += "HIGH RISK: Critical issues detected based on model analysis. "
            elif risk_probability > 0.4:
                interpretation += "MODERATE RISK: Some concerning patterns detected. "
            else:
                interpretation += "LOW RISK: Student is performing well. "
                
            return {
                'risk_probability': float(risk_probability),
                'top_factors': risk_factors[:5],  # Top 5 factors
                'total_factors': len(risk_factors),
                'interpretation': interpretation,
                'explanation_type': 'real_shap',
                'model_type': type(self.model).__name__
            }
            
        except Exception as e:
            logger.error(f"Error getting SHAP explanation: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_fallback_explanation(student_data)
    
    def _prettify_feature_name(self, feature: str) -> str:
        """Make feature names human-readable"""
        name_map = {
            'avg_score_z': 'Average Assessment Score',
            'total_clicks_z': 'Total Platform Interactions',
            'num_days_active_z': 'Days Active on Platform',
            'submission_rate_z': 'Assignment Submission Rate',
            'study_intensity_z': 'Study Intensity',
            'clicks_per_active_day_z': 'Daily Engagement Level',
            'resource_diversity_z': 'Resource Variety',
            'registered_early': 'Early Registration',
            'gender_encoded': 'Gender',
            'region_encoded': 'Region',
            'highest_education_encoded': 'Education Level',
            'imd_band_encoded': 'Deprivation Index',
            'age_band_encoded': 'Age Group',
            'disability_encoded': 'Disability Status'
        }
        return name_map.get(feature, feature.replace('_z', '').replace('_', ' ').title())

    def _generate_natural_language_explanation(self, feature: str, value: float, shap_value: float) -> Dict:
        """Generate text explanation for a feature contribution"""
        
        # Direction
        direction = "increases" if shap_value > 0 else "decreases"
        risk_status = "risk"
        
        # Magnitude
        abs_shap = abs(shap_value)
        if abs_shap > 0.5: strength = "significantly"
        elif abs_shap > 0.2: strength = "moderately"
        else: strength = "slightly"
        
        # Feature specific logic
        text = f"{self._prettify_feature_name(feature)} {strength} {direction} {risk_status}."
        recommendation = "Review this area."
        
        if 'score' in feature:
            if shap_value > 0: # Increasing risk
                text = f"Lower assessment scores are {strength} increasing risk."
                recommendation = "Focus on improving assessment performance through targeted study."
            else:
                text = f"Good assessment scores are {strength} reducing risk."
                recommendation = "Maintain current performance."
                
        elif 'click' in feature or 'active' in feature:
            if shap_value > 0:
                text = f"Low engagement level is {strength} increasing risk."
                recommendation = "Increase daily activity and interaction with course materials."
            else:
                text = f"High engagement level is {strength} reducing risk."
                recommendation = "Continue active participation."
                
        elif 'submission' in feature:
            if shap_value > 0:
                text = f"Missed assignments are {strength} increasing risk."
                recommendation = "Ensure all future assignments are submitted on time."
        
        return {'text': text, 'recommendation': recommendation}

    def _generate_fallback_explanation(self, student_data: Dict) -> Dict:
        """Generate fallback explanation based on rules (legacy method)"""
        # ... (Keep the old logic as fallback)
        risk_factors = []
        risk_probability = student_data.get('risk_probability', 0)
        
        # Get REAL values from student data
        avg_score = float(student_data.get('avg_score', 0))
        days_active = int(student_data.get('num_days_active', 0))
        total_clicks = int(student_data.get('total_clicks', 0))
        
        # Analyze average score
        if avg_score < 70:
            impact = (70 - avg_score) / 70 * 0.3
            risk_factors.append({
                'feature': 'avg_score',
                'feature_name': 'Average Assessment Score',
                'value': avg_score,
                'shap_value': impact,
                'impact_direction': 'increases_risk',
                'explanation': f'Low average score ({avg_score:.1f}%) significantly increases risk',
                'recommendation': 'Focus on improving assessment performance through targeted study'
            })
        
        # Analyze engagement
        if days_active < 30:
            impact = (30 - days_active) / 30 * 0.35
            risk_factors.append({
                'feature': 'num_days_active',
                'feature_name': 'Days Active on Platform',
                'value': days_active,
                'shap_value': impact,
                'impact_direction': 'increases_risk',
                'explanation': f'Low engagement ({days_active} days) is a MAJOR risk factor',
                'recommendation': 'Establish consistent daily study routine'
            })
            
        # Analyze activity
        if total_clicks < 500:
            impact = (500 - total_clicks) / 500 * 0.30
            risk_factors.append({
                'feature': 'total_clicks',
                'feature_name': 'Total Platform Interactions',
                'value': total_clicks,
                'shap_value': impact,
                'impact_direction': 'increases_risk',
                'explanation': f'Very limited activity ({total_clicks:,} clicks) is a MAJOR risk indicator',
                'recommendation': 'Significantly increase interaction with course materials'
            })
            
        return {
            'risk_probability': risk_probability,
            'top_factors': risk_factors,
            'total_factors': len(risk_factors),
            'interpretation': "Fallback explanation (Model data not available)",
            'explanation_type': 'rule_based_fallback',
            'model_type': 'fallback'
        }
    
    def get_dice_counterfactuals(self, student_data: Dict) -> Dict:
        """
        Get DiCE counterfactual explanations based on REAL student data
        
        Args:
            student_data: Student features dictionary
            
        Returns:
            Dictionary with counterfactual scenarios
        """
        student_id = student_data.get('id_student')
        risk_probability = float(student_data.get('risk_probability', 0))
        
        # Only generate if at risk (> 50%)
        if risk_probability < 0.5:
            return {
                'current_risk': risk_probability,
                'target_risk': 0.3,
                'recommendations': [],
                'required_changes': {},
                'explanation_type': 'real_dice',
                'feasibility': 'high',
                'message': 'Student is not at risk, no counterfactuals needed.'
            }
            
        if self.dice_explainer is None:
            logger.warning("DiCE explainer not initialized, using fallback")
            return self._generate_fallback_dice(student_data)
            
        try:
            # Find student features
            student_features = None
            if self.modeling_data is not None and student_id:
                student_row = self.modeling_data[self.modeling_data['id_student'] == student_id]
                if not student_row.empty:
                    student_features = student_row[self.feature_names]
            
            if student_features is None:
                return self._generate_fallback_dice(student_data)
                
            # Generate counterfactuals
            actionable_features = self.dice_explainer.get_actionable_features()
            
            result = self.dice_explainer.generate_counterfactuals(
                student_features,
                total_CFs=3,
                desired_class=0, # Safe
                features_to_vary=actionable_features
            )
            
            if not result['found']:
                return self._generate_fallback_dice(student_data)
                
            # Process results into recommendations
            recommendations = []
            required_changes = {}
            
            # Take the first (best) counterfactual
            cf = result['counterfactuals'][0]
            changes = cf['changes']
            
            for feature, change_data in changes.items():
                feature_name = self._prettify_feature_name(feature)
                original = change_data['original']
                target = change_data['counterfactual']
                diff = change_data['change']
                
                # Format recommendation based on feature type
                if 'score' in feature:
                    rec = f"Increase {feature_name} by {diff:.2f} standard deviations"
                elif 'days' in feature:
                    rec = f"Increase {feature_name} by {diff:.2f} standard deviations"
                else:
                    rec = f"Adjust {feature_name} by {diff:.2f} units"
                    
                recommendations.append(rec)
                required_changes[feature] = {
                    'current': original,
                    'target': target,
                    'change_needed': diff,
                    'feature_name': feature_name
                }
                
            return {
                'current_risk': risk_probability,
                'target_risk': 0.3, # Approximate
                'recommendations': recommendations,
                'required_changes': required_changes,
                'explanation_type': 'real_dice',
                'feasibility': 'verified'
            }
            
        except Exception as e:
            logger.error(f"Error generating DiCE counterfactuals: {e}")
            return self._generate_fallback_dice(student_data)

    def _generate_fallback_dice(self, student_data: Dict) -> Dict:
        """Fallback rule-based DiCE"""
        recommendations = []
        required_changes = {}
        
        # Get REAL values
        current_risk = float(student_data.get('risk_probability', 0))
        avg_score = float(student_data.get('avg_score', 0))
        days_active = int(student_data.get('num_days_active', 0))
        total_clicks = int(student_data.get('total_clicks', 0))
        
        target_risk = 0.3  # Target: reduce to 30% risk
        
        # Feasibility checks
        max_possible_clicks = total_clicks + 1000 # Unlikely to do more than +1000 in short time
        max_possible_score = min(100, avg_score + 20)
        
        # 1. If low engagement
        if days_active < 30:
            target_days = min(40, days_active + 15) # Realistic increase
            recommendations.append(
                f"Increase platform engagement from {days_active} to {target_days} days active"
            )
            required_changes['num_days_active'] = {
                'current': days_active,
                'target': target_days,
                'change_needed': f'+{target_days - days_active} days'
            }
        
        # 2. If low activity
        if total_clicks < 500:
            target_clicks = min(800, total_clicks + 300) # Realistic increase
            recommendations.append(
                f"Increase platform interactions from {total_clicks:,} to {target_clicks:,} clicks"
            )
            required_changes['total_clicks'] = {
                'current': total_clicks,
                'target': target_clicks,
                'change_needed': f'+{target_clicks - total_clicks:,} clicks'
            }
        
        # 3. If low score
        if avg_score < 70:
            target_score = min(75, avg_score + 10) # Realistic increase
            recommendations.append(
                f"Improve assessment scores from {avg_score:.1f}% to {target_score}%"
            )
            required_changes['avg_score'] = {
                'current': f"{avg_score:.1f}%",
                'target': f"{target_score}%",
                'change_needed': f'+{target_score - avg_score:.1f}%'
            }
        
        return {
            'current_risk': current_risk,
            'target_risk': target_risk,
            'recommendations': recommendations,
            'required_changes': required_changes,
            'explanation_type': 'dice_based_heuristic',
            'feasibility': 'high'
        }
    
    def get_student_explainability(self, student_id: int) -> Dict:
        """
        Get complete explainability data for a student (SHAP + DiCE)
        This is the main method called by API endpoints
        
        Args:
            student_id: Student ID
            
        Returns:
            Dictionary with shap_explanation and dice_counterfactuals
        """
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        from src.database.models import get_db
        db = get_db()
        full_context = db.get_student_full_context(student_id)
        
        if not full_context:
            return None
        
        # Merge student data with stats for explainability
        student_data = {**full_context['student'], **full_context['stats']}
        
        # Get SHAP explanation
        shap_explanation = self.get_student_shap_explanation(student_data)
        
        # Get DiCE counterfactuals
        dice_counterfactuals = self.get_dice_counterfactuals(student_data)
        
        return {
            'shap_explanation': shap_explanation,
            'dice_counterfactuals': dice_counterfactuals
        }


# Global instance
_explainability_bridge = None

def get_explainability_bridge() -> ExplainabilityBridge:
    """Get singleton explainability bridge"""
    global _explainability_bridge
    if _explainability_bridge is None:
        _explainability_bridge = ExplainabilityBridge()
    return _explainability_bridge