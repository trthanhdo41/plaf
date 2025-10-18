"""
LLM Advice Benchmark

Evaluate quality of LLM-generated advice for at-risk students.
"""

import sys
import os
import time
import pandas as pd
import numpy as np
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.prescriptive.llm_advisor import LLMAdvisor


class LLMBenchmark:
    """Benchmark LLM advice generation."""
    
    def __init__(self):
        """Initialize benchmark."""
        print("="*70)
        print("LLM ADVICE BENCHMARK")
        print("="*70)
        
        # Test student profiles with counterfactuals
        self.test_profiles = [
            {
                "student_id": 1,
                "profile": {
                    "total_clicks": 120,
                    "avg_score": 58.5,
                    "num_assessments": 4,
                    "risk_probability": 0.75
                },
                "counterfactual": {
                    "total_clicks": 250,
                    "avg_score": 75.0,
                    "num_assessments": 4
                },
                "risk_level": "high"
            },
            {
                "student_id": 2,
                "profile": {
                    "total_clicks": 180,
                    "avg_score": 65.0,
                    "num_assessments": 5,
                    "risk_probability": 0.45
                },
                "counterfactual": {
                    "total_clicks": 220,
                    "avg_score": 72.0,
                    "num_assessments": 5
                },
                "risk_level": "medium"
            },
            {
                "student_id": 3,
                "profile": {
                    "total_clicks": 90,
                    "avg_score": 52.0,
                    "num_assessments": 3,
                    "risk_probability": 0.85
                },
                "counterfactual": {
                    "total_clicks": 200,
                    "avg_score": 70.0,
                    "num_assessments": 3
                },
                "risk_level": "high"
            },
            {
                "student_id": 4,
                "profile": {
                    "total_clicks": 160,
                    "avg_score": 68.0,
                    "num_assessments": 6,
                    "risk_probability": 0.35
                },
                "counterfactual": {
                    "total_clicks": 190,
                    "avg_score": 73.0,
                    "num_assessments": 6
                },
                "risk_level": "low"
            },
            {
                "student_id": 5,
                "profile": {
                    "total_clicks": 100,
                    "avg_score": 55.0,
                    "num_assessments": 4,
                    "risk_probability": 0.68
                },
                "counterfactual": {
                    "total_clicks": 240,
                    "avg_score": 78.0,
                    "num_assessments": 4
                },
                "risk_level": "high"
            }
        ]
        
        self.results = []
        
    def benchmark_response_time(self, advisor: LLMAdvisor):
        """Benchmark LLM response time."""
        print("\n[1/4] Benchmarking Response Time...")
        print("-"*70)
        
        response_times = []
        
        for i, profile in enumerate(self.test_profiles):
            start_time = time.time()
            
            advice = advisor.generate_advice(
                student_data=profile["profile"],
                counterfactual_changes=profile["counterfactual"]
            )
            
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            print(f"  [{i+1}/{len(self.test_profiles)}] Student {profile['student_id']}: "
                  f"{response_time:.2f}s")
        
        avg_time = np.mean(response_times)
        std_time = np.std(response_times)
        
        print(f"\n  Average Response Time: {avg_time:.2f}s ± {std_time:.2f}s")
        print(f"  Min/Max: {min(response_times):.2f}s / {max(response_times):.2f}s")
        
        return {
            "response_times": response_times,
            "avg_time": avg_time,
            "std_time": std_time
        }
    
    def benchmark_advice_quality(self, advisor: LLMAdvisor):
        """Benchmark advice quality based on criteria."""
        print("\n[2/4] Benchmarking Advice Quality...")
        print("-"*70)
        
        quality_scores = []
        
        for i, profile in enumerate(self.test_profiles):
            advice = advisor.generate_advice(
                student_data=profile["profile"],
                counterfactual_changes=profile["counterfactual"]
            )
            
            # Quality criteria
            scores = {
                "student_id": profile["student_id"],
                "risk_level": profile["risk_level"],
                "advice_length": len(advice),
                "has_specific_numbers": self._check_specific_numbers(advice, profile),
                "has_actionable_steps": self._check_actionable_steps(advice),
                "mentions_engagement": "engagement" in advice.lower() or "clicks" in advice.lower(),
                "mentions_grades": "grade" in advice.lower() or "score" in advice.lower(),
                "is_personalized": self._check_personalization(advice, profile),
                "has_encouragement": self._check_encouragement(advice),
                "readability": self._assess_readability(advice)
            }
            
            # Calculate overall quality score (0-1)
            quality_score = (
                (1.0 if scores["has_specific_numbers"] else 0.0) * 0.20 +
                (1.0 if scores["has_actionable_steps"] else 0.0) * 0.25 +
                (1.0 if scores["mentions_engagement"] else 0.0) * 0.15 +
                (1.0 if scores["mentions_grades"] else 0.0) * 0.15 +
                (1.0 if scores["is_personalized"] else 0.0) * 0.10 +
                (1.0 if scores["has_encouragement"] else 0.0) * 0.05 +
                scores["readability"] * 0.10
            )
            
            scores["overall_quality"] = quality_score
            quality_scores.append(scores)
            
            print(f"  [{i+1}/{len(self.test_profiles)}] Student {profile['student_id']}: "
                  f"Quality={quality_score:.2f}")
        
        avg_quality = np.mean([s["overall_quality"] for s in quality_scores])
        
        print(f"\n  Average Quality Score: {avg_quality:.3f}")
        
        return {
            "quality_scores": quality_scores,
            "avg_quality": avg_quality
        }
    
    def benchmark_consistency(self, advisor: LLMAdvisor, n_runs: int = 3):
        """Benchmark advice consistency across multiple runs."""
        print(f"\n[3/4] Benchmarking Consistency ({n_runs} runs per profile)...")
        print("-"*70)
        
        consistency_scores = []
        
        for i, profile in enumerate(self.test_profiles):
            # Generate advice multiple times
            advices = []
            for _ in range(n_runs):
                advice = advisor.generate_advice(
                    student_data=profile["profile"],
                    counterfactual_changes=profile["counterfactual"]
                )
                advices.append(advice)
            
            # Check consistency
            # 1. Length consistency
            lengths = [len(a) for a in advices]
            length_std = np.std(lengths) / np.mean(lengths)  # Coefficient of variation
            
            # 2. Content consistency (check if key terms appear consistently)
            key_terms = ["engagement", "clicks", "grade", "score", "improve"]
            term_consistency = []
            for term in key_terms:
                appearances = sum(1 for a in advices if term in a.lower())
                term_consistency.append(appearances / n_runs)
            
            avg_term_consistency = np.mean(term_consistency)
            
            # Overall consistency score
            consistency = (
                (1.0 - min(length_std, 1.0)) * 0.3 +  # Lower variation is better
                avg_term_consistency * 0.7
            )
            
            consistency_scores.append({
                "student_id": profile["student_id"],
                "consistency_score": consistency,
                "length_variation": length_std,
                "term_consistency": avg_term_consistency
            })
            
            print(f"  [{i+1}/{len(self.test_profiles)}] Student {profile['student_id']}: "
                  f"Consistency={consistency:.2f}")
        
        avg_consistency = np.mean([s["consistency_score"] for s in consistency_scores])
        
        print(f"\n  Average Consistency: {avg_consistency:.3f}")
        
        return {
            "consistency_scores": consistency_scores,
            "avg_consistency": avg_consistency
        }
    
    def benchmark_relevance(self, advisor: LLMAdvisor):
        """Benchmark advice relevance to student's risk level."""
        print("\n[4/4] Benchmarking Advice Relevance...")
        print("-"*70)
        
        relevance_scores = []
        
        for i, profile in enumerate(self.test_profiles):
            advice = advisor.generate_advice(
                student_data=profile["profile"],
                counterfactual_changes=profile["counterfactual"]
            )
            
            risk_level = profile["risk_level"]
            
            # Check if advice matches risk level
            if risk_level == "high":
                # High risk should mention urgency, immediate action
                relevant = (
                    ("urgent" in advice.lower() or "immediately" in advice.lower() or
                     "critical" in advice.lower() or "important" in advice.lower()) and
                    "improve" in advice.lower()
                )
            elif risk_level == "medium":
                # Medium risk should be balanced
                relevant = (
                    "improve" in advice.lower() and
                    ("focus" in advice.lower() or "increase" in advice.lower())
                )
            else:  # low
                # Low risk should be encouraging
                relevant = (
                    "good" in advice.lower() or "maintain" in advice.lower() or
                    "continue" in advice.lower()
                )
            
            relevance_score = 1.0 if relevant else 0.5
            
            relevance_scores.append({
                "student_id": profile["student_id"],
                "risk_level": risk_level,
                "relevance_score": relevance_score
            })
            
            print(f"  [{i+1}/{len(self.test_profiles)}] Student {profile['student_id']} "
                  f"({risk_level} risk): Relevant={'Yes' if relevant else 'Partial'}")
        
        avg_relevance = np.mean([s["relevance_score"] for s in relevance_scores])
        
        print(f"\n  Average Relevance: {avg_relevance:.3f}")
        
        return {
            "relevance_scores": relevance_scores,
            "avg_relevance": avg_relevance
        }
    
    def _check_specific_numbers(self, advice: str, profile: Dict) -> bool:
        """Check if advice contains specific numbers from profile."""
        counterfactual = profile["counterfactual"]
        return (
            str(counterfactual.get("total_clicks", "")) in advice or
            str(counterfactual.get("avg_score", "")) in advice
        )
    
    def _check_actionable_steps(self, advice: str) -> bool:
        """Check if advice contains actionable steps."""
        action_words = ["should", "need to", "try to", "focus on", "increase", 
                       "improve", "engage", "complete", "participate"]
        return any(word in advice.lower() for word in action_words)
    
    def _check_personalization(self, advice: str, profile: Dict) -> bool:
        """Check if advice is personalized to student."""
        student_data = profile["profile"]
        risk_level = "high" if student_data.get("risk_probability", 0) > 0.6 else "low"
        
        # Check if mentions current performance
        mentions_current = (
            str(int(student_data.get("total_clicks", 0))) in advice or
            str(int(student_data.get("avg_score", 0))) in advice
        )
        
        return mentions_current
    
    def _check_encouragement(self, advice: str) -> bool:
        """Check if advice is encouraging."""
        encouraging_words = ["you can", "help you", "support", "improve", "achieve", "succeed"]
        return any(word in advice.lower() for word in encouraging_words)
    
    def _assess_readability(self, advice: str) -> float:
        """Assess readability (simple heuristic)."""
        # Good length: 100-300 characters
        length = len(advice)
        if 100 <= length <= 300:
            length_score = 1.0
        elif length < 100:
            length_score = length / 100
        else:
            length_score = max(0.5, 1.0 - (length - 300) / 500)
        
        # Not too many long words
        words = advice.split()
        avg_word_length = np.mean([len(w) for w in words])
        word_score = 1.0 if avg_word_length < 7 else 0.7
        
        return (length_score + word_score) / 2
    
    def run_full_benchmark(self):
        """Run complete LLM benchmark."""
        print("\nInitializing LLM Advisor...")
        
        try:
            advisor = LLMAdvisor()
            print("[OK] LLM Advisor initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize LLM advisor: {e}")
            print("[TIP] Make sure GEMINI_API_KEY is set")
            return None
        
        # Run benchmarks
        time_results = self.benchmark_response_time(advisor)
        quality_results = self.benchmark_advice_quality(advisor)
        consistency_results = self.benchmark_consistency(advisor, n_runs=3)
        relevance_results = self.benchmark_relevance(advisor)
        
        # Compile results
        results = {
            "response_time": time_results,
            "quality": quality_results,
            "consistency": consistency_results,
            "relevance": relevance_results,
            "summary": {
                "avg_response_time": time_results["avg_time"],
                "avg_quality": quality_results["avg_quality"],
                "avg_consistency": consistency_results["avg_consistency"],
                "avg_relevance": relevance_results["avg_relevance"]
            }
        }
        
        # Print summary
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY")
        print("="*70)
        print(f"Response Time:  {results['summary']['avg_response_time']:.2f}s")
        print(f"Advice Quality: {results['summary']['avg_quality']:.3f}")
        print(f"Consistency:    {results['summary']['avg_consistency']:.3f}")
        print(f"Relevance:      {results['summary']['avg_relevance']:.3f}")
        print("="*70)
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _save_results(self, results: Dict):
        """Save benchmark results to file."""
        import json
        os.makedirs("results", exist_ok=True)
        
        output_file = f"results/llm_benchmark_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n[SAVED] Results saved to: {output_file}")


if __name__ == "__main__":
    benchmark = LLMBenchmark()
    results = benchmark.run_full_benchmark()
    
    if results:
        print("\n[SUCCESS] LLM Benchmark completed successfully!")
    else:
        print("\n[FAILED] LLM Benchmark failed")

