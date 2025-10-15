"""
LLM-based advice generator for PLAF.

This module uses Gemini API to generate natural language advice.
"""

import os
import json
from typing import Dict, List
import logging
import google.generativeai as genai
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class LLMAdvisor:
    """Generate natural language advice using LLM."""
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.5-flash"):
        """
        Initialize LLM advisor.
        
        Args:
            api_key: Gemini API key (reads from env if not provided)
            model_name: Gemini model to use
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Set it in .env file or pass as parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"LLM Advisor initialized with {model_name}")
    
    def create_prompt(self, student_data: Dict, counterfactual_changes: Dict) -> str:
        """
        Create prompt for LLM to generate advice.
        
        Args:
            student_data: Original student feature values
            counterfactual_changes: Recommended changes from DiCE
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an academic advisor AI assistant helping students at risk of not completing their course.

Based on predictive analytics and counterfactual analysis, you need to provide clear, actionable, and supportive advice to help a student improve their outcomes.

## Student Current Situation:
{json.dumps(student_data, indent=2)}

## Recommended Changes to Improve Success:
{json.dumps(counterfactual_changes, indent=2)}

## Your Task:
Generate personalized, evidence-based advice for this student. The advice should:
1. Be supportive and encouraging (not judgmental)
2. Be specific and actionable
3. Prioritize the most impactful changes
4. Be realistic and achievable
5. Explain WHY these changes would help

## Output Format (JSON):
{{
    "summary": "Brief overview of the student's situation",
    "risk_factors": ["List of main risk factors"],
    "recommendations": [
        {{
            "action": "Specific action to take",
            "reason": "Why this will help",
            "priority": "high/medium/low",
            "expected_impact": "What improvement to expect"
        }}
    ],
    "encouragement": "Positive, motivating closing message"
}}

Generate the advice now:"""
        
        return prompt
    
    def generate_advice(self, student_data: Dict, counterfactual_changes: Dict,
                       temperature: float = 0.7) -> Dict:
        """
        Generate advice for a student.
        
        Args:
            student_data: Student's current data
            counterfactual_changes: Recommended changes
            temperature: LLM temperature (0-1, higher = more creative)
            
        Returns:
            Dictionary with generated advice
        """
        try:
            # Create prompt
            prompt = self.create_prompt(student_data, counterfactual_changes)
            
            # Generate response
            logger.info("Generating advice with LLM...")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': temperature,
                    'max_output_tokens': 1024,
                }
            )
            
            # Parse response
            response_text = response.text
            
            # Try to extract JSON from response
            try:
                # Find JSON in response (might have markdown code blocks)
                if '```json' in response_text:
                    json_str = response_text.split('```json')[1].split('```')[0].strip()
                elif '```' in response_text:
                    json_str = response_text.split('```')[1].split('```')[0].strip()
                else:
                    json_str = response_text.strip()
                
                advice = json.loads(json_str)
                advice['raw_response'] = response_text
                advice['success'] = True
                
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw text
                logger.warning("Could not parse LLM response as JSON, returning raw text")
                advice = {
                    'success': False,
                    'raw_response': response_text,
                    'summary': response_text[:200] + '...' if len(response_text) > 200 else response_text
                }
            
            return advice
            
        except Exception as e:
            logger.error(f"Error generating advice: {e}")
            return {
                'success': False,
                'error': str(e),
                'summary': 'Failed to generate advice'
            }
    
    def generate_batch_advice(self, students_data: List[Dict]) -> List[Dict]:
        """
        Generate advice for multiple students.
        
        Args:
            students_data: List of student data with counterfactuals
            
        Returns:
            List of advice for each student
        """
        all_advice = []
        
        for i, student in enumerate(students_data):
            logger.info(f"Generating advice for student {i+1}/{len(students_data)}")
            
            # Extract student data and counterfactuals
            current_data = student.get('original_instance', {})
            cf_changes = student.get('counterfactuals', [])
            
            if cf_changes:
                # Use first counterfactual
                changes = cf_changes[0].get('changes', {})
            else:
                changes = {}
            
            # Generate advice
            advice = self.generate_advice(current_data, changes)
            advice['student_idx'] = student.get('instance_idx', i)
            
            all_advice.append(advice)
        
        return all_advice
    
    def convert_zscore_to_readable(self, feature_name: str, z_value: float,
                                  cohort_mean: float, cohort_std: float) -> str:
        """
        Convert z-score feature to human-readable interpretation.
        
        Args:
            feature_name: Name of the feature
            z_value: Z-score value
            cohort_mean: Cohort mean
            cohort_std: Cohort standard deviation
            
        Returns:
            Human-readable description
        """
        # Convert to raw value
        raw_value = z_value * cohort_std + cohort_mean
        
        # Interpret based on feature type
        if 'score' in feature_name.lower():
            return f"{raw_value:.1f}%"
        elif 'click' in feature_name.lower():
            return f"{raw_value:.0f} clicks"
        elif 'resource' in feature_name.lower():
            return f"{raw_value:.0f} resources"
        elif 'active' in feature_name.lower():
            return f"{raw_value:.0f} days"
        else:
            return f"{raw_value:.2f}"


def generate_llm_advice(counterfactuals: List[Dict], 
                       api_key: str = None) -> List[Dict]:
    """
    Convenience function to generate LLM advice for counterfactuals.
    
    Args:
        counterfactuals: List of counterfactual explanations
        api_key: Gemini API key
        
    Returns:
        List of LLM-generated advice
    """
    advisor = LLMAdvisor(api_key=api_key)
    advice = advisor.generate_batch_advice(counterfactuals)
    
    return advice


# Simple fallback advice generator (rule-based)
def generate_simple_advice(counterfactual_changes: Dict) -> Dict:
    """
    Generate simple rule-based advice (fallback if LLM fails).
    
    Args:
        counterfactual_changes: Dictionary of feature changes
        
    Returns:
        Simple advice dictionary
    """
    recommendations = []
    
    for feature, change_info in counterfactual_changes.items():
        if 'score' in feature:
            recommendations.append({
                'action': f"Improve your average score from {change_info['original']:.1f}% to {change_info['counterfactual']:.1f}%",
                'reason': "Higher grades are strongly associated with course completion",
                'priority': 'high'
            })
        elif 'click' in feature or 'vle' in feature:
            recommendations.append({
                'action': f"Increase your learning platform engagement",
                'reason': "Regular interaction with course materials improves understanding",
                'priority': 'medium'
            })
        elif 'resource' in feature:
            recommendations.append({
                'action': f"Explore more diverse learning resources",
                'reason': "Using varied resources helps reinforce learning",
                'priority': 'medium'
            })
    
    return {
        'success': True,
        'summary': "Based on analysis, here are key areas for improvement",
        'recommendations': recommendations[:5],  # Top 5
        'encouragement': "Small consistent changes can make a big difference in your success!"
    }


if __name__ == "__main__":
    print("LLM Advisor module")
    
    # Test with sample data
    sample_student = {
        'avg_score_z': -0.5,
        'total_clicks_z': -1.2,
        'num_unique_resources_z': -0.8
    }
    
    sample_changes = {
        'avg_score_z': {
            'original': -0.5,
            'counterfactual': 0.3,
            'change': 0.8
        },
        'total_clicks_z': {
            'original': -1.2,
            'counterfactual': 0.1,
            'change': 1.3
        }
    }
    
    # Test simple advice
    simple_advice = generate_simple_advice(sample_changes)
    print("\nSimple advice:")
    print(json.dumps(simple_advice, indent=2))

