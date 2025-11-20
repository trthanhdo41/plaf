import sys
import os
import logging

# Add src to path
sys.path.append(os.getcwd())

from src.explainability.explainability_bridge import get_explainability_bridge

logging.basicConfig(level=logging.INFO)

def test_bridge():
    print("Initializing ExplainabilityBridge...")
    bridge = get_explainability_bridge()
    
    if bridge.model is None:
        print("ERROR: Model not loaded!")
        return
    
    if bridge.shap_explainer is None:
        print("ERROR: SHAP explainer not initialized!")
        return
        
    print("Model and SHAP explainer loaded successfully.")
    
    student_id = 25572
    print(f"Getting explanation for student {student_id}...")
    
    explanation = bridge.get_student_explainability(student_id)
    
    if explanation:
        print("\n--- SHAP Explanation ---")
        shap = explanation['shap_explanation']
        print(f"Risk Probability: {shap['risk_probability']:.2%}")
        print(f"Explanation Type: {shap['explanation_type']}")
        
        print("\nTop Risk Factors:")
        for factor in shap['top_factors']:
            print(f"- {factor['feature_name']}: {factor['shap_value']:.4f} ({factor['impact_direction']})")
            print(f"  Explanation: {factor['explanation']}")
            
        print("\n--- DiCE Counterfactuals ---")
        dice = explanation['dice_counterfactuals']
        print(f"Recommendations: {dice['recommendations']}")
    else:
        print("No explanation returned.")

if __name__ == "__main__":
    test_bridge()
