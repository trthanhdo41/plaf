"""
Student LMS Portal - Web interface for students.

Features:
- Login/Register
- Personal dashboard (grades, progress, risk level)
- VLE materials access
- AI Chatbot for academic support
- Real-time activity tracking
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_db
from chatbot.rag_system import initialize_knowledge_base

# Page config
st.set_page_config(
    page_title="Student Learning Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .risk-high {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #f44336;
        margin: 10px 0;
    }
    .risk-low {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #4caf50;
        margin: 10px 0;
        color: #1b5e20;
    }
    .risk-low h3 {
        color: #2e7d32;
    }
    .risk-low p {
        color: #1b5e20;
    }
    .chat-message {
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
    .user-message {
        background-color: #e3f2fd;
        text-align: right;
    }
    .bot-message {
        background-color: #f5f5f5;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'student_id' not in st.session_state:
    st.session_state.student_id = None
if 'student_data' not in st.session_state:
    st.session_state.student_data = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None


def login_page():
    """Login/Register page."""
    st.markdown('<p class="main-header">Student Learning Portal</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary"):
            if email and password:
                db = get_db()
                student = db.authenticate_student(email, password)
                
                if student:
                    st.session_state.logged_in = True
                    st.session_state.student_id = student['id_student']
                    st.session_state.student_data = student
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
            else:
                st.warning("Please enter email and password")
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                reg_email = st.text_input("Email*")
                reg_password = st.text_input("Password*", type="password")
                reg_first_name = st.text_input("First Name*")
                reg_last_name = st.text_input("Last Name*")
            
            with col2:
                reg_module = st.selectbox("Course Module", ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG"])
                reg_presentation = st.selectbox("Presentation", ["2013J", "2014J", "2013B", "2014B"])
                reg_gender = st.selectbox("Gender", ["M", "F", "Other"])
                reg_region = st.text_input("Region")
            
            submitted = st.form_submit_button("Register", type="primary")
            
            if submitted:
                if reg_email and reg_password and reg_first_name and reg_last_name:
                    db = get_db()
                    student_id = db.create_student(
                        email=reg_email,
                        password=reg_password,
                        first_name=reg_first_name,
                        last_name=reg_last_name,
                        code_module=reg_module,
                        code_presentation=reg_presentation,
                        gender=reg_gender,
                        region=reg_region
                    )
                    
                    if student_id:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Email already exists or registration failed")
                else:
                    st.warning("Please fill in all required fields")


def dashboard_page():
    """Student dashboard."""
    db = get_db()
    student = st.session_state.student_data
    student_id = st.session_state.student_id
    
    # Header
    st.markdown(f'<p class="main-header">Welcome, {student["first_name"]}!</p>', unsafe_allow_html=True)
    
    # Get stats
    stats = db.get_student_stats(student_id)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Activities", f"{stats.get('total_activities', 0) or 0:,}")
    
    with col2:
        st.metric("VLE Clicks", f"{stats.get('total_clicks', 0) or 0:,}")
    
    with col3:
        avg_score = stats.get('avg_score', 0) or 0
        st.metric("Average Score", f"{avg_score:.1f}%" if avg_score else "N/A")
    
    with col4:
        st.metric("Assessments", f"{stats.get('total_assessments', 0) or 0}")
    
    st.markdown("---")
    
    # Risk assessment
    risk_prob = student.get('risk_probability', 0)
    is_at_risk = student.get('is_at_risk', 0)
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # Risk gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_prob * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Academic Risk Level"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "#4caf50"},
                    {'range': [30, 70], 'color': "#ff9800"},
                    {'range': [70, 100], 'color': "#f44336"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if is_at_risk:
            st.markdown(f"""
            <div class="risk-high">
                <h3>You're Flagged as At-Risk</h3>
                <p>Your current risk level is <strong>{risk_prob*100:.1f}%</strong>.</p>
                <p><strong>What this means:</strong> Based on your current performance and engagement, 
                our AI predicts you may face challenges completing this course.</p>
                <p><strong>Don't worry!</strong> We're here to help. Check out the AI Advisor tab for 
                personalized recommendations.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="risk-low">
                <h3>You're On Track</h3>
                <p>Your current risk level is <strong>{risk_prob*100:.1f}%</strong>.</p>
                <p>Great job! Keep up the good work. Continue engaging with course materials 
                and maintaining your current study habits.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Activity chart
    st.subheader("Your Activity Overview")
    
    # Create sample activity data
    activity_data = pd.DataFrame({
        'Metric': ['VLE Clicks', 'Assessments', 'Days Active', 'Late Submissions'],
        'Value': [
            stats.get('total_clicks', 0),
            stats.get('total_assessments', 0),
            stats.get('days_active', 0),
            stats.get('late_submissions', 0)
        ]
    })
    
    fig = px.bar(activity_data, x='Metric', y='Value', 
                 title='Your Engagement Metrics',
                 color='Value',
                 color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)


def materials_page():
    """Course materials page with VLE activities from OULAD."""
    st.markdown('<p class="main-header">Course Materials</p>', unsafe_allow_html=True)
    
    student = st.session_state.student_data
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    
    # Get VLE activities from OULAD for student's module
    cursor.execute("""
        SELECT activity_type, COUNT(*) as count
        FROM vle
        WHERE code_module = ? AND code_presentation = ?
        GROUP BY activity_type
        ORDER BY count DESC
    """, (student['code_module'], student['code_presentation']))
    
    activity_summary = cursor.fetchall()
    
    if not activity_summary:
        st.warning("No VLE activities found for your course. Please contact your instructor.")
        return
    
    # Display course info
    st.info(f"**Course:** {student['code_module']} - {student['code_presentation']}")
    
    # Create two columns: Materials (left) + Chatbot (right)
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Learning Activities")
        
        # Activity type filter
        activity_types = [row[0] for row in activity_summary]
        selected_type = st.selectbox(
            "Filter by activity type:",
            ["All"] + activity_types,
            key="activity_filter"
        )
        
        # Get activities
        if selected_type == "All":
            cursor.execute("""
                SELECT id_site, activity_type, week_from, week_to
                FROM vle
                WHERE code_module = ? AND code_presentation = ?
                ORDER BY activity_type, id_site
                LIMIT 50
            """, (student['code_module'], student['code_presentation']))
        else:
            cursor.execute("""
                SELECT id_site, activity_type, week_from, week_to
                FROM vle
                WHERE code_module = ? AND code_presentation = ? AND activity_type = ?
                ORDER BY id_site
                LIMIT 50
            """, (student['code_module'], student['code_presentation'], selected_type))
        
        activities = cursor.fetchall()
        
        # Display activity summary
        st.write(f"**Total activities:** {len(activities)}")
        
        # Group activities by type
        activity_groups = {}
        for activity in activities:
            id_site, act_type, week_from, week_to = activity
            if act_type not in activity_groups:
                activity_groups[act_type] = []
            activity_groups[act_type].append({
                'id_site': id_site,
                'week_from': week_from,
                'week_to': week_to
            })
        
        # Display activities
        for act_type, items in activity_groups.items():
            with st.expander(f"{act_type.upper()} ({len(items)} items)", expanded=(selected_type == act_type)):
                for idx, item in enumerate(items[:20]):  # Limit to 20 per type
                    col_a, col_b = st.columns([4, 1])
                    
                    with col_a:
                        week_info = ""
                        if item['week_from']:
                            week_info = f" (Week {item['week_from']}"
                            if item['week_to'] and item['week_to'] != item['week_from']:
                                week_info += f"-{item['week_to']}"
                            week_info += ")"
                        
                        st.write(f"**{act_type.capitalize()} #{idx+1}**{week_info}")
                        
                        # Activity description based on type
                        descriptions = {
                            'resource': 'Course resource material',
                            'oucontent': 'Open University course content',
                            'url': 'External web resource',
                            'forumng': 'Discussion forum',
                            'homepage': 'Course homepage',
                            'quiz': 'Assessment quiz',
                            'subpage': 'Course subpage',
                            'dataplus': 'Data repository',
                            'oucollaborate': 'Collaboration tool',
                            'glossary': 'Course glossary'
                        }
                        st.caption(descriptions.get(act_type, 'Learning activity'))
                    
                    with col_b:
                        # Check if this was just viewed
                        viewed_key = f"viewed_{item['id_site']}"
                        if viewed_key in st.session_state:
                            st.success("✓ Logged")
                        elif st.button("View", key=f"view_{item['id_site']}"):
                            # Log activity to database
                            db.log_activity(
                                st.session_state.student_id,
                                'view_material',
                                resource_id=item['id_site'],
                                resource_type=act_type,
                                clicks=1,
                                date=datetime.now().day
                            )
                            st.session_state[viewed_key] = True
                            st.rerun()
    
    with col2:
        st.subheader("AI Study Assistant")
        st.caption("Ask questions about course materials")
        
        # Initialize RAG system
        if st.session_state.rag_system is None:
            with st.spinner("Loading AI..."):
                try:
                    st.session_state.rag_system = initialize_knowledge_base()
                except Exception as e:
                    st.error(f"AI unavailable: {e}")
                    return
        
        rag = st.session_state.rag_system
        
        # Mini chat interface
        if 'materials_chat' not in st.session_state:
            st.session_state.materials_chat = []
        
        # Display recent messages with better styling
        chat_container = st.container()
        with chat_container:
            if not st.session_state.materials_chat:
                st.info("💬 Ask me anything about the course materials!")
            else:
                for msg in st.session_state.materials_chat[-5:]:  # Show last 5
                    if msg['role'] == 'user':
                        st.markdown(f"""
                        <div style='background: #e3f2fd; padding: 10px; border-radius: 8px; margin: 5px 0;'>
                            <strong>You:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background: #f5f5f5; padding: 10px; border-radius: 8px; margin: 5px 0;'>
                            <strong>AI:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
        
        # Chat input
        with st.form(key="materials_chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Ask about course content:",
                placeholder="e.g., What resources are available?",
                key="materials_chat_input"
            )
            submit = st.form_submit_button("Send", use_container_width=True)
            
            if submit and user_input:
                # Add user message
                st.session_state.materials_chat.append({
                    'role': 'user',
                    'content': user_input
                })
                
                # Get AI response
                try:
                    # Show loading state
                    with st.spinner("🤖 AI is thinking... Please wait"):
                        response = rag.query(
                            user_input,
                            student_context=student
                        )
                        
                        st.session_state.materials_chat.append({
                            'role': 'assistant',
                            'content': response
                        })
                        
                        # Log chat
                        db.log_chat(
                            st.session_state.student_id,
                            user_input,
                            response,
                            context=f"materials_{student['code_module']}"
                        )
                        
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.session_state.materials_chat.append({
                        'role': 'assistant',
                        'content': error_msg
                    })
                    st.error(f"AI Error: {e}")
                
                st.rerun()
        
        # Quick questions
        st.caption("Quick questions:")
        quick_questions = [
            "What activities should I focus on?",
            "How can I improve my grade?",
            "What resources are most important?"
        ]
        
        for q in quick_questions:
            if st.button(q, key=f"quick_{hash(q)}", use_container_width=True):
                st.session_state.materials_chat.append({'role': 'user', 'content': q})
                try:
                    with st.spinner("🤖 AI is thinking..."):
                        response = rag.query(q, student_context=student)
                        st.session_state.materials_chat.append({'role': 'assistant', 'content': response})
                        db.log_chat(st.session_state.student_id, q, response, context=f"materials_{student['code_module']}")
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.session_state.materials_chat.append({'role': 'assistant', 'content': error_msg})
                st.rerun()


def chatbot_page():
    """AI Chatbot page."""
    st.markdown('<p class="main-header">🤖 AI Academic Advisor</p>', unsafe_allow_html=True)
    
    # Initialize RAG system
    if st.session_state.rag_system is None:
        with st.spinner("Initializing AI Advisor..."):
            try:
                st.session_state.rag_system = initialize_knowledge_base()
                st.success("AI Advisor ready!")
            except Exception as e:
                st.error(f"Failed to initialize AI: {e}")
                return
    
    rag = st.session_state.rag_system
    db = get_db()
    
    # Load chat history with context
    if not st.session_state.chat_history:
        history = db.get_chat_history(st.session_state.student_id, limit=10)
        st.session_state.chat_history = list(reversed(history))
    
    # Display chat history with better formatting
    st.subheader("💬 Conversation History")
    
    # Show conversation context
    if st.session_state.chat_history:
        st.info(f"📚 **Context:** I remember our previous {len(st.session_state.chat_history)} conversations. I can refer to our earlier discussions to provide more personalized advice.")
    
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for i, chat in enumerate(st.session_state.chat_history):
                # Show timestamp
                timestamp = chat.get('timestamp', 'Unknown time')
                if hasattr(timestamp, 'strftime'):
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M")
                else:
                    time_str = str(timestamp)
            
            st.markdown(f"""
                <div class="chat-message-container" style="margin-bottom: 15px; padding: 10px; border-radius: 8px; background-color: #f8f9fa;">
                    <div style="font-size: 0.8em; color: #666; margin-bottom: 5px;">{time_str}</div>
                    <div class="chat-message user-message" style="margin-bottom: 8px;">
                        <strong>👤 You:</strong> {chat['message']}
                    </div>
            <div class="chat-message bot-message">
                        <strong>🤖 AI Advisor:</strong> {chat['response']}
                    </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("💬 **Start a conversation!** Ask me anything about your studies, and I'll remember our chat for better future advice.")
    
    # Chat input
    st.markdown("---")
    st.subheader("Ask a Question")
    
    # Use form to avoid session_state error
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Your question:", 
            placeholder="e.g., How can I improve my study habits?",
            label_visibility="collapsed"
        )
        
        send_button = st.form_submit_button("Send", use_container_width=False)
    
    if send_button and user_input:
        with st.spinner("AI is thinking..."):
            # Build context from previous conversations
            conversation_context = ""
            if st.session_state.chat_history:
                recent_chats = st.session_state.chat_history[-3:]  # Last 3 conversations
                conversation_context = "\n\nPrevious conversation context:\n"
                for chat in recent_chats:
                    conversation_context += f"Student: {chat['message']}\n"
                    conversation_context += f"Advisor: {chat['response']}\n"
            
            # Get response from RAG with context
            result = rag.chat(
                user_input, 
                student_data=st.session_state.student_data,
                conversation_context=conversation_context
            )
            
            # Save to database with enhanced context
            db.log_chat(
                st.session_state.student_id,
                user_input,
                result['response'],
                context=f"conversation_history_{len(st.session_state.chat_history)}"
            )
            
            # Add to session with timestamp
            st.session_state.chat_history.append({
                'message': user_input,
                'response': result['response'],
                'timestamp': datetime.now(),
                'context_used': result.get('context_used', [])
            })
            
            # Keep only last 10 conversations to avoid memory issues
            if len(st.session_state.chat_history) > 10:
                st.session_state.chat_history = st.session_state.chat_history[-10:]
            
            st.rerun()
    
    # Chat management and suggestions
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
    st.write("💡 Suggested Questions:")
    suggestions = [
        "How can I improve my grades?",
        "I'm feeling overwhelmed with assignments. What should I do?",
        "What study techniques work best?",
        "How can I manage my time better?",
        "I'm struggling with the course material. Where can I get help?"
    ]
    
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                    # Manually add suggestion as a chat with context
                with st.spinner("AI is thinking..."):
                        # Build context from previous conversations
                        conversation_context = ""
                        if st.session_state.chat_history:
                            recent_chats = st.session_state.chat_history[-3:]
                            conversation_context = "\n\nPrevious conversation context:\n"
                            for chat in recent_chats:
                                conversation_context += f"Student: {chat['message']}\n"
                                conversation_context += f"Advisor: {chat['response']}\n"
                        
                        result = rag.chat(
                            suggestion, 
                            student_data=st.session_state.student_data,
                            conversation_context=conversation_context
                        )
                    db.log_chat(
                        st.session_state.student_id,
                        suggestion,
                        result['response'],
                            context=f"suggestion_with_history_{len(st.session_state.chat_history)}"
                    )
                    st.session_state.chat_history.append({
                        'message': suggestion,
                        'response': result['response'],
                            'timestamp': datetime.now(),
                            'context_used': result.get('context_used', [])
                        })
                        st.rerun()
    
    with col2:
        st.write("🗑️ Chat Management")
        if st.button("Clear Chat History", help="Clear all previous conversations", use_container_width=True):
            st.session_state.chat_history = []
            # Clear from database if method exists
            try:
                db.clear_chat_history(st.session_state.student_id)
            except:
                pass  # Method might not exist yet
            st.success("Chat history cleared!")
                    st.rerun()


def main():
    """Main application."""
    
    if not st.session_state.logged_in:
        login_page()
    else:
        # Sidebar
        st.sidebar.title("🎓 Student Portal")
        st.sidebar.write(f"Welcome, **{st.session_state.student_data['first_name']}**")
        st.sidebar.write(f"Course: {st.session_state.student_data['code_module']}")
        
        # Navigation
        page = st.sidebar.radio(
            "Navigate",
            ["Dashboard", "Course Materials", "AI Advisor", "Profile"]
        )
        
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.student_id = None
            st.session_state.student_data = None
            st.session_state.chat_history = []
            st.rerun()
        
        # Route to pages
        if page == "Dashboard":
            dashboard_page()
        elif page == "Course Materials":
            materials_page()
        elif page == "AI Advisor":
            chatbot_page()
        elif page == "Profile":
            st.markdown('<p class="main-header">👤 My Profile</p>', unsafe_allow_html=True)
            student = st.session_state.student_data
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Personal Information**")
                st.write(f"Name: {student['first_name']} {student['last_name']}")
                st.write(f"Email: {student['email']}")
                st.write(f"Gender: {student.get('gender', 'N/A')}")
                st.write(f"Region: {student.get('region', 'N/A')}")
            
            with col2:
                st.write("**Academic Information**")
                st.write(f"Course Module: {student['code_module']}")
                st.write(f"Presentation: {student['code_presentation']}")
                st.write(f"Education Level: {student.get('highest_education', 'N/A')}")
                st.write(f"Risk Status: {'At-Risk' if student.get('is_at_risk') else 'On Track'}")


if __name__ == "__main__":
    main()

