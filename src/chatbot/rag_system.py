"""
RAG (Retrieval-Augmented Generation) system for chatbot.

Uses FAISS for vector similarity search and Gemini for generation.
"""

import numpy as np
from typing import List, Dict, Tuple
import logging
import os
import pickle
import google.generativeai as genai
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    logger.warning("FAISS not available. Install with: pip install faiss-cpu")
    FAISS_AVAILABLE = False


class RAGSystem:
    """RAG system for student chatbot."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize RAG system.
        
        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.embedding_model = genai.GenerativeModel('text-embedding-004') if hasattr(genai, 'text_embedding_004') else None
        
        # Knowledge base
        self.documents = []
        self.embeddings = None
        self.index = None
        
        logger.info("RAG System initialized")
    
    def add_documents(self, documents: List[str]):
        """
        Add documents to knowledge base.
        
        Args:
            documents: List of text documents
        """
        self.documents.extend(documents)
        logger.info(f"Added {len(documents)} documents to knowledge base")
    
    def create_simple_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create simple TF-IDF-like embeddings (fallback if no embedding model).
        
        Args:
            texts: List of texts
            
        Returns:
            Embeddings matrix
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        vectorizer = TfidfVectorizer(max_features=384)
        embeddings = vectorizer.fit_transform(texts).toarray()
        
        self.vectorizer = vectorizer
        return embeddings.astype('float32')
    
    def build_index(self):
        """Build index for similarity search."""
        if not self.documents:
            logger.warning("No documents to index")
            return
        
        # Create embeddings
        logger.info("Creating embeddings...")
        self.embeddings = self.create_simple_embeddings(self.documents)
        
        # Don't use FAISS for now - use simple search
        logger.info(f"Built search index with {len(self.documents)} documents")
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of (document, score) tuples
        """
        if not self.documents:
            return []
        
        # Create query embedding using the same vectorizer
        if hasattr(self, 'vectorizer') and self.vectorizer is not None:
            query_embedding = self.vectorizer.transform([query]).toarray().astype('float32')
        else:
            query_embedding = self.create_simple_embeddings([query])
        
        # Use simple cosine similarity (more stable than FAISS)
        from sklearn.metrics.pairwise import cosine_similarity
        
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((self.documents[idx], float(similarities[idx])))
        
        return results
    
    def generate_response(self, query: str, context: List[str], student_data: Dict = None) -> str:
        """
        Generate response using RAG.
        
        Args:
            query: User query
            context: Retrieved context documents
            student_data: Student information for personalization
            
        Returns:
            Generated response
        """
        # Build prompt with context
        context_text = "\n\n".join(context) if context else "No specific context available."
        
        student_info = ""
        if student_data:
            student_info = f"""
Student Information:
- Name: {student_data.get('first_name', '')} {student_data.get('last_name', '')}
- Course: {student_data.get('code_module', '')}
- At-Risk: {'Yes' if student_data.get('is_at_risk') else 'No'}
- Risk Level: {student_data.get('risk_probability', 0)*100:.1f}%
"""
        
        prompt = f"""You are a friendly and supportive AI academic advisor for students.

{student_info}

Context from knowledge base:
{context_text}

Student Question: {query}

Please provide a helpful, encouraging, and actionable response. Be specific and reference the context when relevant.
Keep the response concise (2-3 paragraphs maximum).

Response:"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Strip any HTML tags that might be in the response
            import re
            response_text = re.sub(r'<[^>]+>', '', response_text)
            
            return response_text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error. Please try asking your question again."
    
    def chat(self, query: str, student_data: Dict = None, top_k: int = 3) -> Dict:
        """
        Complete RAG chat workflow.
        
        Args:
            query: User query
            student_data: Student information
            top_k: Number of context documents to retrieve
            
        Returns:
            Dictionary with response and metadata
        """
        # Search for relevant context
        search_results = self.search(query, top_k=top_k)
        context_docs = [doc for doc, score in search_results]
        
        # Generate response
        response = self.generate_response(query, context_docs, student_data)
        
        return {
            'query': query,
            'response': response,
            'context_used': context_docs,
            'num_contexts': len(context_docs)
        }
    
    def save_index(self, path: str = "data/rag_index.pkl"):
        """Save RAG index to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        data = {
            'documents': self.documents,
            'embeddings': self.embeddings,
            'vectorizer': getattr(self, 'vectorizer', None)
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        
        if FAISS_AVAILABLE and self.index is not None:
            faiss.write_index(self.index, path.replace('.pkl', '.faiss'))
        
        logger.info(f"Saved RAG index to {path}")
    
    def load_index(self, path: str = "data/rag_index.pkl"):
        """Load RAG index from disk."""
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            self.documents = data['documents']
            self.embeddings = data['embeddings']
            self.vectorizer = data.get('vectorizer')
            
            if FAISS_AVAILABLE:
                faiss_path = path.replace('.pkl', '.faiss')
                if os.path.exists(faiss_path):
                    self.index = faiss.read_index(faiss_path)
            
            logger.info(f"Loaded RAG index from {path}")
            return True
        except FileNotFoundError:
            logger.warning(f"Index file not found: {path}")
            return False


def initialize_knowledge_base() -> RAGSystem:
    """Initialize RAG system with course knowledge."""
    rag = RAGSystem()
    
    # Add course materials (example)
    course_docs = [
        # General study tips
        "Effective study techniques include: active recall, spaced repetition, and practice testing. Review your notes regularly and test yourself frequently.",
        
        "Time management is crucial for academic success. Create a study schedule, break large tasks into smaller ones, and avoid procrastination.",
        
        "If you're struggling with a course, don't hesitate to ask for help. Attend office hours, join study groups, and use online resources.",
        
        # VLE engagement
        "Regularly accessing the Virtual Learning Environment (VLE) is associated with better grades. Check the VLE daily for announcements, materials, and assignments.",
        
        "Engage with all types of course materials - videos, readings, quizzes, and forums. Diverse engagement helps reinforce learning.",
        
        # Assessments
        "Start assignments early to avoid last-minute stress. Read the requirements carefully and plan your work.",
        
        "Late submissions can significantly impact your grade. Set reminders for deadlines and submit work early when possible.",
        
        "If you're concerned about an upcoming assessment, review past materials and practice problems. Seek clarification on confusing topics.",
        
        # At-risk support
        "Students who fall behind should: 1) Contact their advisor immediately, 2) Create a catch-up plan, 3) Prioritize the most important tasks.",
        
        "If you're feeling overwhelmed, remember that many students experience similar challenges. Reach out to student support services for help.",
        
        # Course-specific (OULAD)
        "For module AAA (Arts and Humanities): Focus on critical reading and writing skills. Engage deeply with primary sources.",
        
        "For module BBB (Social Sciences): Understand research methods and data analysis. Practice interpreting statistics and graphs.",
        
        "For module CCC (STEM): Build strong foundational knowledge. Complete practice problems and understand underlying concepts.",
        
        # General advice
        "Maintaining a balanced lifestyle improves academic performance. Get adequate sleep, exercise regularly, and manage stress.",
        
        "Connect with classmates through forums and study groups. Peer learning can clarify difficult concepts and provide motivation.",
    ]
    
    rag.add_documents(course_docs)
    rag.build_index()
    
    # Try to save index
    try:
        rag.save_index()
    except Exception as e:
        logger.warning(f"Could not save index: {e}")
    
    return rag


if __name__ == "__main__":
    # Test RAG system
    print("Initializing RAG system...")
    rag = initialize_knowledge_base()
    
    # Test search
    print("\nTesting search...")
    results = rag.search("How can I improve my grades?", top_k=3)
    for i, (doc, score) in enumerate(results):
        print(f"\n{i+1}. Score: {score:.4f}")
        print(f"   {doc[:100]}...")
    
    # Test chat
    print("\nTesting chat...")
    student_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'code_module': 'AAA',
        'is_at_risk': True,
        'risk_probability': 0.75
    }
    
    response = rag.chat(
        "I'm struggling with my assignments and feeling overwhelmed. What should I do?",
        student_data=student_data
    )
    
    print(f"\nQuery: {response['query']}")
    print(f"\nResponse: {response['response']}")
    print(f"\nUsed {response['num_contexts']} context documents")

