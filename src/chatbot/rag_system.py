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
    
    def __init__(self, api_key: str = None, knowledge_base_path: str = "data/knowledge_base.pkl", index_path: str = "data/faiss_index.faiss"):
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
        self.model = genai.GenerativeModel('gemini-2.5-flash')
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
    
    def create_semantic_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create semantic embeddings using Gemini embedding model.
        
        Args:
            texts: List of texts
            
        Returns:
            Embeddings matrix (numpy array)
        """
        logger.info(f"Creating semantic embeddings for {len(texts)} documents...")
        embeddings = []
        
        try:
            # Use Gemini embedding model
            for i, text in enumerate(texts):
                if i % 10 == 0:
                    logger.info(f"Processing embedding {i+1}/{len(texts)}")
                
                try:
                    # Use Gemini embedding API
                    result = genai.embed_content(
                        model="models/text-embedding-004",
                        content=text,
                        task_type="retrieval_document"
                    )
                    embedding = result['embedding']
                    embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"Error creating embedding for text {i}: {e}")
                    # Fallback to simple zero embedding
                    embeddings.append(np.zeros(768))
            
            embeddings = np.array(embeddings, dtype='float32')
            logger.info(f"Created {len(embeddings)} embeddings with shape {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.warning(f"Failed to create semantic embeddings: {e}. Using fallback TF-IDF.")
            return self.create_simple_embeddings(texts)
    
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
        """Build FAISS index for fast similarity search."""
        if not self.documents:
            logger.warning("No documents to index")
            return
        
        # Create semantic embeddings
        logger.info("Creating semantic embeddings...")
        self.embeddings = self.create_semantic_embeddings(self.documents)
        
        # Build FAISS index for fast search
        if FAISS_AVAILABLE:
            try:
                dimension = self.embeddings.shape[1]
                # Use IndexFlatL2 for exact search (can upgrade to IndexIVFFlat for approximate search with large datasets)
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(self.embeddings.astype('float32'))
                logger.info(f"Built FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.warning(f"Failed to build FAISS index: {e}. Using simple search.")
                self.index = None
        else:
            logger.warning("FAISS not available. Using simple search.")
            self.index = None
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Search for relevant documents using FAISS (if available) or simple search.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of (document, score) tuples
        """
        if not self.documents:
            return []
        
        # Create query embedding
        try:
            # Use semantic embedding for query
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )
            query_embedding = np.array([result['embedding']], dtype='float32')
            logger.info(f"Created query embedding with shape {query_embedding.shape}")
        except Exception as e:
            logger.warning(f"Failed to create semantic embedding for query: {e}")
            # Fallback
        if hasattr(self, 'vectorizer') and self.vectorizer is not None:
            query_embedding = self.vectorizer.transform([query]).toarray().astype('float32')
        else:
            query_embedding = self.create_simple_embeddings([query])
        
        # Use FAISS for fast similarity search
        if self.index is not None:
            try:
                # Search using FAISS
                k = min(top_k, len(self.documents))
                distances, indices = self.index.search(query_embedding, k)
                
                results = []
                for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    if idx < len(self.documents):
                        # Convert L2 distance to similarity score (1 / (1 + distance))
                        similarity = 1.0 / (1.0 + distance)
                        results.append((self.documents[idx], float(similarity)))
                
                logger.info(f"FAISS search returned {len(results)} results")
                return results
            except Exception as e:
                logger.warning(f"FAISS search failed: {e}. Using fallback search.")
        
        # Fallback: Use simple cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((self.documents[idx], float(similarities[idx])))
        
        return results
    
    def generate_response(self, query: str, context: List[str], student_data: Dict = None, conversation_context: str = None, full_context: Dict = None, explainability_data: Dict = None) -> str:
        """
        Generate response using RAG with comprehensive student context and explainability.
        
        Args:
            query: User query
            context: Retrieved context documents
            student_data: Basic student information (deprecated, use full_context)
            conversation_context: Previous conversation summary
            full_context: Complete student context from database
            explainability_data: SHAP/DiCE explanations for targeted interventions
            
        Returns:
            Generated response
        """
        # Build prompt with context
        context_text = "\n\n".join(context) if context else "No specific context available."
        
        # Build comprehensive student information section
        student_info = ""
        if full_context:
            student = full_context.get('student', {})
            courses = full_context.get('courses', [])
            quiz_results = full_context.get('quiz_results', [])
            stats = full_context.get('stats', {})
            
            # Check if we have OULAD data (from students table)
            has_oulad_data = stats.get('has_oulad_data', False)
            
            # Basic info
            student_info = f"""
=== STUDENT PROFILE ===
Name: {student.get('first_name', '')} {student.get('last_name', '')}
Email: {student.get('email', '')}
Student ID: {student.get('id_student', 'N/A')}
Course Module: {student.get('code_module', 'N/A')}
"""
            
            if has_oulad_data:
                # Use OULAD data (real academic performance data)
                risk_prob = stats.get('risk_probability', 0) * 100
                avg_score = stats.get('avg_score', 0)
                days_active = stats.get('days_active', 0)
                total_engagement = stats.get('total_engagement', 0)
                is_at_risk = stats.get('is_at_risk', 0)
                
                student_info += f"""
=== ACADEMIC PERFORMANCE (OULAD Data) ===
Risk Level: {risk_prob:.1f}% ({'HIGH RISK - Needs Attention' if is_at_risk else 'On Track'})
Average Score: {avg_score:.1f}% ({'Excellent' if avg_score >= 80 else 'Good' if avg_score >= 60 else 'Needs Improvement'})
Days Active: {days_active} days ({'Highly Engaged' if days_active >= 40 else 'Moderate' if days_active >= 20 else 'Low Engagement'})
Total Interactions: {total_engagement:,} clicks ({'Very Active' if total_engagement >= 1000 else 'Active' if total_engagement >= 500 else 'Limited Activity'})

=== LEARNING INSIGHTS ===
Academic Status: {'At-Risk Student - Requires Support' if is_at_risk else 'Performing Well'}
Engagement Level: {'High' if days_active >= 40 and total_engagement >= 1000 else 'Moderate' if days_active >= 20 else 'Low'}
Performance Trend: {'Strong Performance' if avg_score >= 70 else 'Needs Academic Support'}
"""
            else:
                # Use course enrollment data
                student_info += f"""
=== CURRENT LEARNING STATUS ===
Enrolled Courses: {stats.get('total_courses', 0)}
Total Lessons: {stats.get('total_lessons', 0)}
Completed Lessons: {stats.get('completed_lessons', 0)}
Overall Progress: {stats.get('course_progress', 0):.1f}%
"""
            
            # Always show quiz and forum data if available
            student_info += f"""
=== QUIZ PERFORMANCE ===
Total Quizzes Taken: {stats.get('total_quizzes', 0)}
Quizzes Passed: {stats.get('passed_quizzes', 0)}
Average Quiz Score: {stats.get('quiz_avg_score', 0):.1f}%

=== FORUM ACTIVITY ===
Forum Posts Created: {stats.get('forum_activity', 0)}
"""
            
            # Add current courses details
            if courses:
                student_info += "\n=== ENROLLED COURSES ===\n"
                for course in courses:
                    completed = course.get('completed_lessons', 0) or 0
                    total = course.get('total_lessons', 0) or 0
                    progress = (completed / total * 100) if total > 0 else 0
                    student_info += f"- {course.get('course_title', 'N/A')}: {completed}/{total} lessons ({progress:.1f}% complete)\n"
            
            # Add recent quiz results
            if quiz_results:
                student_info += "\n=== RECENT QUIZ RESULTS ===\n"
                for quiz in quiz_results[:3]:  # Show last 3 quizzes
                    status = "✅ PASSED" if quiz.get('passed') else "❌ FAILED"
                    student_info += f"- {quiz.get('course_title', 'N/A')} - {quiz.get('title', 'Quiz')}: {quiz.get('score', 0):.1f}% {status}\n"
        
        elif student_data:
            # Fallback to basic student data
            student_info = f"""
=== STUDENT PROFILE ===
Name: {student_data.get('first_name', '')} {student_data.get('last_name', '')}
Course: {student_data.get('code_module', '')}
At-Risk: {'Yes' if student_data.get('is_at_risk') else 'No'}
Risk Level: {student_data.get('risk_probability', 0)*100:.1f}%
"""
        
        # Add conversation context if available
        conversation_info = ""
        if conversation_context:
            conversation_info = f"""
=== PREVIOUS CONVERSATION CONTEXT ===
{conversation_context}

Use this context to provide more personalized and consistent advice. Reference previous discussions when relevant.
"""
        
        # Add explainability insights for targeted interventions
        explainability_info = ""
        if explainability_data:
            shap_data = explainability_data.get('shap_explanation', {})
            dice_data = explainability_data.get('dice_counterfactuals', {})
            
            explainability_info = "\n=== RISK ANALYSIS & INTERVENTION INSIGHTS ===\n"
            
            # Add SHAP top risk factors
            top_factors = shap_data.get('top_factors', [])
            if top_factors:
                explainability_info += "**Key Risk Factors Identified:**\n"
                for i, factor in enumerate(top_factors[:3], 1):
                    feature = factor.get('feature', 'Unknown')
                    explanation = factor.get('explanation', '')
                    explainability_info += f"{i}. {explanation}\n"
                
                explainability_info += "\n**What This Means:**\n"
                explainability_info += shap_data.get('interpretation', 'Analysis of key factors affecting student risk.')
                explainability_info += "\n"
            
            # ★★★ NEW: Use ActionMapper to get specific actions instead of numerical targets ★★★
            specific_actions_text = ""
            if full_context:
                student_id = full_context.get('student', {}).get('id_student')
                required_changes = dice_data.get('required_changes', {})
                
                if student_id and required_changes:
                    try:
                        from src.prescriptive.action_mapper import ActionMapper
                        action_mapper = ActionMapper()
                        specific_actions = action_mapper.map_actions(student_id, required_changes)
                        
                        # Format actions into human-readable list
                        action_items = []
                        
                        if specific_actions.get('recommended_resources'):
                            for r in specific_actions['recommended_resources'][:3]:
                                activity = r.get('activity_type', 'resource')
                                week = r.get('week_from')
                                week_text = f"Week {week}" if week else "the course materials"
                                action_items.append(f"Access the {activity} in {week_text}")
                        
                        if specific_actions.get('review_assessments'):
                            for a in specific_actions['review_assessments'][:2]:
                                assess_type = a.get('assessment_type', 'assignment')
                                score = a.get('score', 0)
                                action_items.append(f"Review your {assess_type} where you scored {score:.0f}%")
                        
                        if specific_actions.get('upcoming_assessments'):
                            for a in specific_actions['upcoming_assessments'][:2]:
                                assess_type = a.get('assessment_type', 'assessment')
                                action_items.append(f"Prepare for your upcoming {assess_type}")
                        
                        if action_items:
                            specific_actions_text = "\n**SPECIFIC ACTIONS THIS STUDENT MUST DO:**\n"
                            for i, action in enumerate(action_items, 1):
                                specific_actions_text += f"{i}. {action}\n"
                            
                            specific_actions_text += "\n⚠️ CRITICAL: You MUST recommend these SPECIFIC actions, not generic advice like 'increase clicks'.\n"
                    except Exception as e:
                        logger.warning(f"Could not get specific actions: {e}")
            
            # If we have specific actions, use them; otherwise fall back to generic recommendations
            if specific_actions_text:
                explainability_info += specific_actions_text
            else:
                # Fallback: Use DiCE recommendations but warn to be specific
                recommendations = dice_data.get('recommendations', [])
                if recommendations:
                    explainability_info += "\n**Targeted Improvement Strategies:**\n"
                    for i, rec in enumerate(recommendations[:3], 1):
                        explainability_info += f"{i}. {rec}\n"
            
            explainability_info += "\n**IMPORTANT:** Provide SPECIFIC, ACTIONABLE advice. Instead of saying 'increase interaction', say 'review the lecture notes' or 'complete the quiz'. Be a caring tutor, not a statistician.\n"
        
        prompt = f"""You are an experienced AI academic advisor helping students succeed in their online learning journey. You have access to comprehensive data about this student's learning behavior, progress, and performance, including advanced predictive analytics.

{student_info}

{conversation_info}

{explainability_info}

=== KNOWLEDGE BASE CONTEXT ===
{context_text}

=== STUDENT QUESTION ===
{query}

=== INSTRUCTIONS ===
Based on the student's complete profile above, provide:
1. A personalized, data-driven response that references their specific situation
2. Concrete, actionable advice tailored to their progress and performance
3. If specific actions are listed above, recommend those EXACT actions (e.g., "Review your TMA where you scored 22%")
4. ABSOLUTELY FORBIDDEN: Do NOT mention numerical targets like "increase from X to Y" or "raise by Z%"
5. Encouragement and motivation appropriate to their current status

If the student is at-risk, be especially supportive and provide clear guidance on improvement.
If they're doing well, acknowledge their progress and suggest ways to maintain momentum.
Reference specific actions from their profile when provided.
If risk factors are identified, explain how addressing them will improve their outcomes.

Keep the response conversational, encouraging, and focused (2-3 paragraphs).

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
            
            # Check if it's a quota error - use fallback advisor
            error_str = str(e)
            if '429' in error_str or 'quota' in error_str.lower() or 'rate limit' in error_str.lower():
                logger.info("Using fallback advisor due to API quota limit")
                
                try:
                    from src.chatbot.fallback_advisor import get_fallback_advisor
                    fallback = get_fallback_advisor()
                    fallback_response = fallback.generate_response(
                        query=query,
                        full_context=full_context,
                        explainability_data=explainability_data
                    )
                    
                    # Add note about fallback
                    fallback_response = (
                        "**Note:** AI service is temporarily at capacity (daily quota reached). "
                        "Using simplified advisor until tomorrow. For full AI features, please check back in 24 hours.\n\n---\n\n"
                        + fallback_response
                    )
                    
                    return fallback_response
                except Exception as fallback_error:
                    logger.error(f"Fallback advisor also failed: {fallback_error}")
                    return (
                        "I apologize, but the AI service has reached its daily usage limit (Gemini API quota). "
                        "This limit resets every 24 hours. Please try again later, or contact your administrator "
                        "to upgrade the API plan. In the meantime, you can still view your dashboard and course materials."
                    )
            
            return "I'm sorry, I encountered an error. Please try asking your question again."
    
    def query(self, query: str, student_context: Dict = None, top_k: int = 3) -> str:
        """
        Simple query method that returns just the response text.
        
        Args:
            query: User query
            student_context: Student information
            top_k: Number of context documents to retrieve
            
        Returns:
            Response text (string)
        """
        result = self.chat(query, student_data=student_context, top_k=top_k)
        return result['response']
    
    def chat(self, query: str, student_data: Dict = None, top_k: int = 3, conversation_context: str = None, full_context: Dict = None, explainability_data: Dict = None) -> Dict:
        """
        Complete RAG chat workflow with comprehensive student context and explainability.
        
        Args:
            query: User query
            student_data: Basic student information (deprecated)
            top_k: Number of context documents to retrieve
            conversation_context: Previous conversation context
            full_context: Complete student context from database
            explainability_data: SHAP/DiCE explanations for targeted interventions
            
        Returns:
            Dictionary with response and metadata
        """
        # Enhanced search with explainability-derived queries
        search_queries = [query]
        
        # Add explanation-derived search queries for better targeting
        if explainability_data:
            shap_data = explainability_data.get('shap_explanation', {})
            dice_data = explainability_data.get('dice_counterfactuals', {})
            
            # Extract top risk factors from SHAP
            top_factors = shap_data.get('top_factors', [])
            for factor in top_factors[:2]:  # Top 2 risk factors
                feature_name = factor.get('feature', '')
                # Convert feature names to search queries
                if 'score' in feature_name.lower():
                    search_queries.append("improve assessment scores study strategies")
                elif 'click' in feature_name.lower() or 'engagement' in feature_name.lower():
                    search_queries.append("increase VLE engagement participation tips")
                elif 'submission' in feature_name.lower():
                    search_queries.append("assignment submission time management")
            
            # Add DiCE recommendations as queries
            recommendations = dice_data.get('recommendations', [])
            for rec in recommendations[:2]:  # Top 2 recommendations
                if 'score' in rec.lower():
                    search_queries.append("boost grades academic performance")
                elif 'engagement' in rec.lower():
                    search_queries.append("active learning engagement strategies")
        
        # Search with multiple queries and combine results
        all_results = []
        for search_query in search_queries:
            results = self.search(search_query, top_k=top_k)
            all_results.extend(results)
        
        # Deduplicate and get top results
        seen_docs = set()
        unique_results = []
        for doc, score in all_results:
            if doc not in seen_docs:
                seen_docs.add(doc)
                unique_results.append((doc, score))
        
        # Sort by score and take top_k
        unique_results.sort(key=lambda x: x[1], reverse=True)
        search_results = unique_results[:top_k * 2]  # Get more context when using explainability
        context_docs = [doc for doc, score in search_results]
        
        # Generate response with full context + explainability
        response = self.generate_response(
            query, 
            context_docs, 
            student_data=student_data,
            conversation_context=conversation_context,
            full_context=full_context,
            explainability_data=explainability_data
        )
        
        return {
            'query': query,
            'response': response,
            'context_used': context_docs,
            'num_contexts': len(context_docs),
            'has_conversation_context': conversation_context is not None,
            'has_full_context': full_context is not None,
            'has_explainability': explainability_data is not None
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


def load_course_materials_from_db() -> List[str]:
    """Load course materials dynamically from database."""
    docs = []
    try:
        import sqlite3
        conn = sqlite3.connect("data/lms.db")
        cursor = conn.cursor()
        
        # Get all VLE materials with descriptions
        cursor.execute("""
            SELECT activity_type, COUNT(*) as count, code_module
            FROM vle
            GROUP BY activity_type, code_module
            ORDER BY count DESC
        """)
        
        vle_data = cursor.fetchall()
        for activity_type, count, module in vle_data:
            docs.append(
                f"Module {module} has {count} {activity_type} activities. "
                f"Access these {activity_type} materials regularly to stay engaged with the course content."
            )
        
        # Get assessment information
        cursor.execute("""
            SELECT DISTINCT assessment_type, code_module
            FROM assessments
        """)
        
        assessments = cursor.fetchall()
        for assessment_type, module in assessments:
            docs.append(
                f"Module {module} includes {assessment_type} assessments. "
                f"Prepare thoroughly for {assessment_type} by reviewing course materials and practicing regularly."
            )
        
        conn.close()
        logger.info(f"Loaded {len(docs)} documents from database")
        
    except Exception as e:
        logger.warning(f"Could not load course materials from database: {e}")
    
    return docs


def initialize_knowledge_base() -> RAGSystem:
    """Initialize RAG system with dynamic course knowledge from OULAD database."""
    rag = RAGSystem()
    
    # Core study strategies (generic knowledge)
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
        
        # General advice
        "Maintaining a balanced lifestyle improves academic performance. Get adequate sleep, exercise regularly, and manage stress.",
        
        "Connect with classmates through forums and study groups. Peer learning can clarify difficult concepts and provide motivation.",
    ]
    
    # Load dynamic content from database
    dynamic_docs = load_course_materials_from_db()
    course_docs.extend(dynamic_docs)
    
    # Load enhanced data-driven knowledge base
    enhanced_kb_path = 'data/enhanced_knowledge_base.txt'
    if os.path.exists(enhanced_kb_path):
        try:
            with open(enhanced_kb_path, 'r') as f:
                content = f.read()
            
            # Parse the numbered documents
            import re
            # Split by numbered items (e.g., "1. ", "2. ", etc.)
            pattern = r'\d+\.\s+'
            enhanced_docs = re.split(pattern, content)
            # Remove empty strings and header
            enhanced_docs = [doc.strip() for doc in enhanced_docs if doc.strip() and not doc.startswith('#')]
            
            course_docs.extend(enhanced_docs)
            logger.info(f"Loaded {len(enhanced_docs)} data-driven documents from enhanced knowledge base")
        except Exception as e:
            logger.warning(f"Could not load enhanced knowledge base: {e}")
    else:
        logger.warning(f"Enhanced knowledge base not found at {enhanced_kb_path}. Run enhance_knowledge_base.py to generate it.")
        
    # Note: VLE content is now loaded dynamically via load_course_materials_from_db()
    
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

