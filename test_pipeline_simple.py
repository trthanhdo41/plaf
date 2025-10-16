#!/usr/bin/env python3
"""
Simple Pipeline Test - No Dependencies
Test core pipeline functionality without heavy dependencies
"""

import sys
import os
sys.path.append('.')

def main():
    print("=" * 60)
    print("PLAF SIMPLE PIPELINE TEST")
    print("=" * 60)
    
    # Test 1: Data Loading
    print("\n[1/3] Testing Data Loading...")
    try:
        from src.data.loader import load_oulad_data
        data, _ = load_oulad_data()
        print(f"[OK] Data loading: SUCCESS - {len(data)} tables loaded")
    except Exception as e:
        print(f"[ERROR] Data loading: FAILED - {e}")
        return False
    
    # Test 2: Preprocessing
    print("\n[2/3] Testing Preprocessing...")
    try:
        from src.data.preprocessing import OULADPreprocessor
        preprocessor = OULADPreprocessor(data)
        df = preprocessor.merge_all_tables()
        print(f"[OK] Preprocessing: SUCCESS - {df.shape[0]} students, {df.shape[1]} features")
    except Exception as e:
        print(f"[ERROR] Preprocessing: FAILED - {e}")
        return False
    
    # Test 3: Simple Model Training
    print("\n[3/3] Testing Model Training...")
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        import numpy as np
        
        # Prepare features
        numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [col for col in numeric_features if col not in ['is_at_risk', 'id_student']]
        X = df[feature_cols].fillna(0)
        y = df['is_at_risk']
        
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"[OK] Model training: SUCCESS - Accuracy: {accuracy:.3f}")
    except Exception as e:
        print(f"[ERROR] Model training: FAILED - {e}")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE TEST SUMMARY")
    print("=" * 60)
    print("[SUCCESS] ALL TESTS PASSED!")
    print("[OK] Data loading works")
    print("[OK] Preprocessing works") 
    print("[OK] Model training works")
    print("[OK] Pipeline is functional!")
    print("\nNext steps:")
    print("1. Run Student Portal: streamlit run src/lms_portal/student_app.py")
    print("2. Run Advisor Dashboard: streamlit run src/dashboard/app.py")
    print("3. Run Benchmark Dashboard: streamlit run src/dashboard/benchmark_dashboard.py")
    print("\n" + "=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
