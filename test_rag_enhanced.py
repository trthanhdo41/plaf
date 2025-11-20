"""Test RAG system with enhanced knowledge base"""

import sys
sys.path.insert(0, '.')

from src.chatbot.rag_system import initialize_knowledge_base

def main():
    print("Initializing RAG system with enhanced knowledge base...")
    print("=" * 60)
    
    rag = initialize_knowledge_base()
    
    print(f"\n✅ RAG system initialized")
    print(f"Total documents in knowledge base: {len(rag.documents)}")
    
    # Test search for engagement-related advice
    print("\n" + "=" * 60)
    print("TEST 1: Searching for 'low engagement' advice")
    print("=" * 60)
    results = rag.search("low engagement risk", top_k=3)
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n{i}. Score: {score:.4f}")
        print(f"   {doc[:200]}...")
    
    # Test search for score improvement
    print("\n" + "=" * 60)
    print("TEST 2: Searching for 'improve scores' advice")
    print("=" * 60)
    results = rag.search("improve assessment scores", top_k=3)
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n{i}. Score: {score:.4f}")
        print(f"   {doc[:200]}...")
    
    # Test search for submission advice
    print("\n" + "=" * 60)
    print("TEST 3: Searching for 'assignment submission' advice")
    print("=" * 60)
    results = rag.search("assignment submission late", top_k=3)
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n{i}. Score: {score:.4f}")
        print(f"   {doc[:200]}...")
    
    print("\n" + "=" * 60)
    print("✅ RAG system is working with enhanced knowledge base!")
    print("=" * 60)

if __name__ == "__main__":
    main()
