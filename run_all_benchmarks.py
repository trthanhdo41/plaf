"""
Master Benchmark Script

Run all benchmarks: RAG, Predictive Models, and LLM Advice.
"""

import sys
import os
import time
from datetime import datetime

# Add tests directory to path
sys.path.append('tests')

from tests.benchmark_rag import RAGBenchmark
from tests.benchmark_predictive import PredictiveBenchmark
from tests.benchmark_llm import LLMBenchmark


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def run_all_benchmarks():
    """Run all benchmarks and generate comprehensive report."""
    
    print_header("PLAF COMPREHENSIVE BENCHMARK SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    start_time = time.time()
    results = {}
    
    # ===== 1. Predictive Models Benchmark =====
    print_header("1/3: PREDICTIVE MODELS BENCHMARK")
    
    try:
        pred_benchmark = PredictiveBenchmark()
        pred_results = pred_benchmark.run_full_benchmark(
            data_path="data/features/modeling_data.csv",
            n_folds=5
        )
        results["predictive"] = {
            "status": "success",
            "results": pred_results
        }
    except Exception as e:
        print(f"❌ Predictive benchmark failed: {e}")
        results["predictive"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # ===== 2. RAG System Benchmark =====
    print_header("2/3: RAG SYSTEM BENCHMARK")
    
    try:
        rag_benchmark = RAGBenchmark()
        rag_results = rag_benchmark.run_full_benchmark()
        results["rag"] = {
            "status": "success",
            "results": rag_results
        }
    except Exception as e:
        print(f"❌ RAG benchmark failed: {e}")
        results["rag"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # ===== 3. LLM Advice Benchmark =====
    print_header("3/3: LLM ADVICE BENCHMARK")
    
    try:
        llm_benchmark = LLMBenchmark()
        llm_results = llm_benchmark.run_full_benchmark()
        results["llm"] = {
            "status": "success",
            "results": llm_results
        }
    except Exception as e:
        print(f"❌ LLM benchmark failed: {e}")
        results["llm"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # ===== Final Summary =====
    elapsed_time = time.time() - start_time
    
    print_header("COMPREHENSIVE BENCHMARK SUMMARY")
    
    print("📊 Benchmark Results:\n")
    
    # Predictive Models
    if results["predictive"]["status"] == "success":
        pred_df = results["predictive"]["results"]
        best_model = pred_df.iloc[0]
        print(f"✅ Predictive Models:")
        print(f"   Best Model: {best_model['model']}")
        print(f"   Test AUC:   {best_model['test_auc']:.4f}")
        print(f"   Test F1:    {best_model['test_f1']:.4f}\n")
    else:
        print(f"❌ Predictive Models: {results['predictive']['error']}\n")
    
    # RAG System
    if results["rag"]["status"] == "success":
        rag_summary = results["rag"]["results"]["summary"]
        print(f"✅ RAG System:")
        print(f"   Retrieval Relevance: {rag_summary['avg_retrieval_relevance']:.3f}")
        print(f"   Response Quality:    {rag_summary['avg_response_quality']:.3f}")
        print(f"   Avg Latency:         {rag_summary['avg_end_to_end_latency']:.2f}s\n")
    else:
        print(f"❌ RAG System: {results['rag']['error']}\n")
    
    # LLM Advice
    if results["llm"]["status"] == "success":
        llm_summary = results["llm"]["results"]["summary"]
        print(f"✅ LLM Advice:")
        print(f"   Advice Quality:   {llm_summary['avg_quality']:.3f}")
        print(f"   Consistency:      {llm_summary['avg_consistency']:.3f}")
        print(f"   Relevance:        {llm_summary['avg_relevance']:.3f}")
        print(f"   Response Time:    {llm_summary['avg_response_time']:.2f}s\n")
    else:
        print(f"❌ LLM Advice: {results['llm']['error']}\n")
    
    print("="*80)
    print(f"Total Time: {elapsed_time/60:.1f} minutes")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Save comprehensive report
    save_comprehensive_report(results, elapsed_time)
    
    return results


def save_comprehensive_report(results: dict, elapsed_time: float):
    """Save comprehensive benchmark report."""
    import json
    
    os.makedirs("results", exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_time": elapsed_time,
        "benchmarks": {}
    }
    
    # Add each benchmark result
    for name, result in results.items():
        if result["status"] == "success":
            if name == "predictive":
                # Convert DataFrame to dict
                report["benchmarks"][name] = {
                    "status": "success",
                    "models": result["results"].to_dict(orient="records")
                }
            else:
                report["benchmarks"][name] = {
                    "status": "success",
                    "summary": result["results"].get("summary", {})
                }
        else:
            report["benchmarks"][name] = {
                "status": "failed",
                "error": result.get("error", "Unknown error")
            }
    
    output_file = f"results/comprehensive_benchmark_{time.strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Comprehensive report saved to: {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run all PLAF benchmarks')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick benchmark (fewer samples)')
    
    args = parser.parse_args()
    
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║            PLAF COMPREHENSIVE BENCHMARK SUITE                     ║
    ║                                                                   ║
    ║  This will benchmark:                                             ║
    ║    1. Predictive Models (CatBoost, RF, XGBoost, SVM, LR)        ║
    ║    2. RAG System (retrieval, response quality, latency)          ║
    ║    3. LLM Advice (quality, consistency, relevance)               ║
    ║                                                                   ║
    ║  Estimated time: 15-30 minutes                                    ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    input("Press Enter to start benchmarking...")
    
    results = run_all_benchmarks()
    
    # Check if all succeeded
    all_success = all(r["status"] == "success" for r in results.values())
    
    if all_success:
        print("\n🎉 All benchmarks completed successfully!")
    else:
        failed = [name for name, r in results.items() if r["status"] == "failed"]
        print(f"\n⚠️  Some benchmarks failed: {', '.join(failed)}")
    
    print("\n📁 Check results/ directory for detailed reports")

