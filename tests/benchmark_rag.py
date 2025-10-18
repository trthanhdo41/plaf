"""
RAG System Benchmark

Test RAG retrieval quality, response accuracy, and latency.
"""

import sys
import os
import time
import pandas as pd
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chatbot.rag_system import RAGSystem


class RAGBenchmark:
    """Benchmark RAG system performance."""
    
    def __init__(self):
        """Initialize benchmark."""
        print("="*70)
        print("RAG SYSTEM BENCHMARK")
        print("="*70)
        
        # Test questions with expected topics
        self.test_cases = [
            {
                "question": "How can I improve my grades?",
                "expected_topics": ["study", "grades", "assessment", "engagement"],
                "category": "academic_advice"
            },
            {
                "question": "What is VLE engagement?",
                "expected_topics": ["vle", "engagement", "activity", "learning"],
                "category": "concept_explanation"
            },
            {
                "question": "How do I manage my time better?",
                "expected_topics": ["time", "management", "planning", "study"],
                "category": "study_skills"
            },
            {
                "question": "Why am I at risk of failing?",
                "expected_topics": ["risk", "failing", "grades", "engagement"],
                "category": "risk_factors"
            },
            {
                "question": "What are the most important factors for success?",
                "expected_topics": ["success", "factors", "engagement", "grades"],
                "category": "success_factors"
            },
            {
                "question": "How can I increase my VLE clicks?",
                "expected_topics": ["vle", "engagement", "activity", "clicks"],
                "category": "engagement_advice"
            },
            {
                "question": "What should I do if I'm struggling with assignments?",
                "expected_topics": ["assignment", "help", "support", "study"],
                "category": "academic_support"
            },
            {
                "question": "How does my demographic affect my success?",
                "expected_topics": ["demographic", "factors", "success", "region"],
                "category": "demographic_analysis"
            }
        ]
        
        self.results = []
        
    def benchmark_retrieval(self, chatbot: RAGSystem) -> Dict:
        """Benchmark retrieval quality."""
        print("\n[1/3] Benchmarking Retrieval Quality...")
        print("-"*70)
        
        retrieval_scores = []
        
        for i, test in enumerate(self.test_cases):
            question = test["question"]
            expected_topics = test["expected_topics"]
            
            # Retrieve documents
            start_time = time.time()
            results = chatbot.search(question, top_k=3)
            retrieval_time = time.time() - start_time
            
            # Check if expected topics are in retrieved docs
            retrieved_text = " ".join([doc.lower() for doc, score in results])
            
            topic_matches = sum(1 for topic in expected_topics if topic in retrieved_text)
            relevance_score = topic_matches / len(expected_topics)
            
            retrieval_scores.append({
                "question": question,
                "category": test["category"],
                "relevance_score": relevance_score,
                "retrieval_time": retrieval_time,
                "num_docs_retrieved": len(results)
            })
            
            print(f"  [{i+1}/{len(self.test_cases)}] {test['category']}: "
                  f"Relevance={relevance_score:.2f}, Time={retrieval_time*1000:.1f}ms")
        
        avg_relevance = sum(s["relevance_score"] for s in retrieval_scores) / len(retrieval_scores)
        avg_time = sum(s["retrieval_time"] for s in retrieval_scores) / len(retrieval_scores)
        
        print(f"\n  Average Relevance Score: {avg_relevance:.3f}")
        print(f"  Average Retrieval Time: {avg_time*1000:.1f}ms")
        
        return {
            "scores": retrieval_scores,
            "avg_relevance": avg_relevance,
            "avg_retrieval_time": avg_time
        }
    
    def benchmark_response_quality(self, chatbot: RAGSystem, student_data: Dict = None) -> Dict:
        """Benchmark response generation quality."""
        print("\n[2/3] Benchmarking Response Quality...")
        print("-"*70)
        
        if student_data is None:
            student_data = {
                "id_student": 12345,
                "first_name": "Test",
                "total_clicks": 150,
                "avg_score": 65.0,
                "risk_probability": 0.35
            }
        
        response_scores = []
        
        for i, test in enumerate(self.test_cases):
            question = test["question"]
            
            # Generate response
            start_time = time.time()
            result = chatbot.chat(question, student_data=student_data)
            response = result['response']
            response_time = time.time() - start_time
            
            # Quality metrics
            response_length = len(response)
            has_context = any(topic in response.lower() for topic in test["expected_topics"])
            is_personalized = any(str(student_data[k]) in response for k in ["first_name", "total_clicks", "avg_score"])
            
            quality_score = (
                (1.0 if has_context else 0.0) * 0.6 +
                (1.0 if is_personalized else 0.0) * 0.2 +
                (min(response_length / 200, 1.0)) * 0.2  # Good length ~200 chars
            )
            
            response_scores.append({
                "question": question,
                "category": test["category"],
                "quality_score": quality_score,
                "response_time": response_time,
                "response_length": response_length,
                "has_context": has_context,
                "is_personalized": is_personalized
            })
            
            print(f"  [{i+1}/{len(self.test_cases)}] {test['category']}: "
                  f"Quality={quality_score:.2f}, Time={response_time:.2f}s")
        
        avg_quality = sum(s["quality_score"] for s in response_scores) / len(response_scores)
        avg_time = sum(s["response_time"] for s in response_scores) / len(response_scores)
        
        print(f"\n  Average Quality Score: {avg_quality:.3f}")
        print(f"  Average Response Time: {avg_time:.2f}s")
        
        return {
            "scores": response_scores,
            "avg_quality": avg_quality,
            "avg_response_time": avg_time
        }
    
    def benchmark_end_to_end(self, chatbot: RAGSystem) -> Dict:
        """Benchmark end-to-end latency."""
        print("\n[3/3] Benchmarking End-to-End Latency...")
        print("-"*70)
        
        latencies = []
        
        for i, test in enumerate(self.test_cases):
            start_time = time.time()
            response = chatbot.get_response(test["question"], {})
            latency = time.time() - start_time
            
            latencies.append(latency)
            print(f"  [{i+1}/{len(self.test_cases)}] {test['category']}: {latency:.2f}s")
        
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        print(f"\n  Average Latency: {avg_latency:.2f}s")
        print(f"  Min/Max: {min_latency:.2f}s / {max_latency:.2f}s")
        
        return {
            "latencies": latencies,
            "avg_latency": avg_latency,
            "min_latency": min_latency,
            "max_latency": max_latency
        }
    
    def run_full_benchmark(self) -> Dict:
        """Run complete RAG benchmark."""
        print("\nInitializing RAG chatbot...")
        
        try:
            chatbot = RAGSystem()
            print("[OK] RAG chatbot initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize chatbot: {e}")
            return None
        
        # Run benchmarks
        retrieval_results = self.benchmark_retrieval(chatbot)
        response_results = self.benchmark_response_quality(chatbot)
        latency_results = self.benchmark_end_to_end(chatbot)
        
        # Compile results
        results = {
            "retrieval": retrieval_results,
            "response_quality": response_results,
            "latency": latency_results,
            "summary": {
                "avg_retrieval_relevance": retrieval_results["avg_relevance"],
                "avg_response_quality": response_results["avg_quality"],
                "avg_end_to_end_latency": latency_results["avg_latency"]
            }
        }
        
        # Print summary
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY")
        print("="*70)
        print(f"Retrieval Relevance:   {results['summary']['avg_retrieval_relevance']:.3f}")
        print(f"Response Quality:      {results['summary']['avg_response_quality']:.3f}")
        print(f"End-to-End Latency:    {results['summary']['avg_end_to_end_latency']:.2f}s")
        print("="*70)
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _save_results(self, results: Dict):
        """Save benchmark results to file."""
        import json
        os.makedirs("results", exist_ok=True)
        
        output_file = f"results/rag_benchmark_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n[SAVED] Results saved to: {output_file}")


if __name__ == "__main__":
    benchmark = RAGBenchmark()
    results = benchmark.run_full_benchmark()
    
    if results:
        print("\n[SUCCESS] RAG Benchmark completed successfully!")
    else:
        print("\n[FAILED] RAG Benchmark failed")

