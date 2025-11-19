"""
Fallback advisor for when Gemini API quota is exceeded.
Provides rule-based responses without requiring API calls.
"""

from typing import Dict

class FallbackAdvisor:
    """Simple rule-based advisor for quota exceeded situations"""
    
    @staticmethod
    def generate_response(query: str, full_context: Dict = None, explainability_data: Dict = None) -> str:
        """
        Generate a simple response without LLM API.
        
        Args:
            query: User's question
            full_context: Student context from database
            explainability_data: SHAP/DiCE data
            
        Returns:
            Rule-based response string
        """
        query_lower = query.lower()
        
        # Get student info
        stats = full_context.get('stats', {}) if full_context else {}
        student = full_context.get('student', {}) if full_context else {}
        
        risk_prob = stats.get('risk_probability', 0) * 100
        is_at_risk = stats.get('is_at_risk', 0)
        avg_score = stats.get('avg_score', 0)
        days_active = stats.get('days_active', 0)
        total_clicks = stats.get('total_engagement', 0)
        
        # Pattern matching for common questions
        
        # Question: Why am I at risk?
        if any(word in query_lower for word in ['why', 'risk', 'at-risk', 'at risk']):
            response = f"Based on your current performance data:\n\n"
            
            if is_at_risk:
                response += f"**Your Risk Status:** {risk_prob:.1f}% probability of not completing successfully\n\n"
                response += "**Key Factors Contributing to Risk:**\n\n"
                
                if avg_score < 60:
                    response += f"1. **Low Assessment Scores ({avg_score:.1f}%)**: Your current average is below the 60% threshold for success. Focus on improving your understanding of course materials.\n\n"
                
                if days_active < 30:
                    response += f"2. **Limited Engagement ({days_active} days active)**: Successful students typically engage with the platform 40+ days. Increase your daily study time.\n\n"
                
                if total_clicks < 500:
                    response += f"3. **Low Activity Level ({total_clicks:,} interactions)**: More interaction with course materials correlates with better outcomes. Aim for 800+ total clicks.\n\n"
                
                response += "**Recommended Actions:**\n"
                response += "- Log in daily and spend at least 30 minutes on course materials\n"
                response += "- Complete all assignments on time\n"
                response += "- Review materials you struggled with\n"
                response += "- Participate in forums and discussions\n"
            else:
                response += f"Good news! Your current risk level is {risk_prob:.1f}%, which means you're on track.\n\n"
                response += "**Your Strengths:**\n"
                response += f"- Average Score: {avg_score:.1f}%\n"
                response += f"- Days Active: {days_active}\n"
                response += f"- Total Engagement: {total_clicks:,} clicks\n\n"
                response += "Keep up the good work!"
            
            return response
        
        # Question: How can I improve?
        elif any(word in query_lower for word in ['improve', 'better', 'help', 'do']):
            response = "**Personalized Improvement Recommendations:**\n\n"
            
            if avg_score < 70:
                response += "**1. Focus on Assessments:**\n"
                response += f"   Current: {avg_score:.1f}% | Target: 75%+\n"
                response += "   - Review failed assessments and identify gaps\n"
                response += "   - Practice with sample problems\n"
                response += "   - Start assignments 5-7 days early\n\n"
            
            if days_active < 40:
                response += "**2. Increase Daily Engagement:**\n"
                response += f"   Current: {days_active} days | Target: 40+ days\n"
                response += "   - Set daily study reminders\n"
                response += "   - Spend 30-60 minutes daily on materials\n"
                response += "   - Make it a habit to check in daily\n\n"
            
            if total_clicks < 800:
                response += "**3. Interact More with Materials:**\n"
                response += f"   Current: {total_clicks:,} clicks | Target: 800+ clicks\n"
                response += "   - Watch all lecture videos\n"
                response += "   - Complete interactive exercises\n"
                response += "   - Explore supplementary resources\n\n"
            
            response += "**General Tips:**\n"
            response += "- Break study sessions into 25-minute focused blocks\n"
            response += "- Take notes while watching videos\n"
            response += "- Test yourself regularly with quizzes\n"
            response += "- Ask questions in forums when stuck\n"
            
            return response
        
        # Question: What should I do next?
        elif any(word in query_lower for word in ['next', 'now', 'today', 'start']):
            response = "**Your Action Plan for Today:**\n\n"
            
            response += "**Immediate Actions (Next 30 minutes):**\n"
            response += "1. Log into the course platform\n"
            response += "2. Check for any upcoming deadlines\n"
            response += "3. Review the current week's materials\n\n"
            
            response += "**This Week:**\n"
            response += "- Complete all assigned readings\n"
            response += "- Watch lecture videos and take notes\n"
            response += "- Start any assignments that are due soon\n"
            response += "- Participate in at least 2 forum discussions\n\n"
            
            if is_at_risk:
                response += "**⚠️ Priority Items (You're At-Risk):**\n"
                response += "- Reach out to your instructor or advisor\n"
                response += "- Review any failed assessments\n"
                response += "- Create a catch-up schedule\n"
                response += "- Consider joining a study group\n"
            
            return response
        
        # Question: About grades/scores
        elif any(word in query_lower for word in ['grade', 'score', 'exam', 'test', 'assessment']):
            response = f"**Your Assessment Performance:**\n\n"
            response += f"Current Average: {avg_score:.1f}%\n\n"
            
            if avg_score < 60:
                response += "**Status:** Below passing threshold (needs improvement)\n\n"
                response += "**To Improve Your Grades:**\n"
                response += "1. Identify your weakest topics\n"
                response += "2. Spend extra time reviewing those areas\n"
                response += "3. Complete all practice problems\n"
                response += "4. Ask for help on concepts you don't understand\n"
                response += "5. Start exam preparation 1 week early\n"
            elif avg_score < 80:
                response += "**Status:** Passing, but room for improvement\n\n"
                response += "**To Boost Your Performance:**\n"
                response += "1. Review feedback on previous assignments\n"
                response += "2. Focus on consistent study habits\n"
                response += "3. Deepen understanding of key concepts\n"
            else:
                response += "**Status:** Excellent performance!\n\n"
                response += "**Maintain Your Success:**\n"
                response += "1. Continue your current study approach\n"
                response += "2. Help peers who are struggling\n"
                response += "3. Challenge yourself with advanced materials\n"
            
            return response
        
        # Question: About time/schedule
        elif any(word in query_lower for word in ['time', 'schedule', 'busy', 'manage', 'organize']):
            response = "**Time Management Strategies:**\n\n"
            response += "**Weekly Study Schedule:**\n"
            response += "- Monday-Friday: 1 hour per day (review materials, watch videos)\n"
            response += "- Weekend: 2-3 hours (complete assignments, practice)\n"
            response += "- Total: 9-10 hours per week minimum\n\n"
            
            response += "**Daily Routine:**\n"
            response += "1. Morning: Check for announcements (5 min)\n"
            response += "2. Afternoon: Study session (30-60 min)\n"
            response += "3. Evening: Review notes (15 min)\n\n"
            
            response += "**Time-Saving Tips:**\n"
            response += "- Use Pomodoro technique (25 min focus, 5 min break)\n"
            response += "- Eliminate distractions during study time\n"
            response += "- Study most difficult subjects when you're most alert\n"
            response += "- Use commute time for watching lecture videos\n"
            
            return response
        
        # Default response
        else:
            response = f"**Your Current Status Summary:**\n\n"
            response += f"- Average Score: {avg_score:.1f}%\n"
            response += f"- Days Active: {days_active}\n"
            response += f"- Engagement Level: {total_clicks:,} interactions\n"
            response += f"- Risk Level: {risk_prob:.1f}%\n\n"
            
            response += "**I can help you with:**\n"
            response += "- Understanding why you might be at risk\n"
            response += "- Suggesting ways to improve your performance\n"
            response += "- Creating an action plan\n"
            response += "- Time management strategies\n"
            response += "- Study tips and techniques\n\n"
            
            response += "**Try asking:**\n"
            response += "- 'Why am I at risk?'\n"
            response += "- 'How can I improve my grades?'\n"
            response += "- 'What should I do today?'\n"
            response += "- 'How can I manage my time better?'\n"
            
            return response

def get_fallback_advisor():
    """Get fallback advisor instance"""
    return FallbackAdvisor()

