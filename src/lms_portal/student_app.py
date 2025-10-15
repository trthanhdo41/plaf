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
    """Course materials page."""
    st.markdown('<p class="main-header">📚 Course Materials</p>', unsafe_allow_html=True)
    
    student = st.session_state.student_data
    db = get_db()
    
    # Get materials for student's course
    materials = db.get_course_materials(student['code_module'])
    
    if not materials:
        st.info("📝 No materials available yet for your course. Check back later!")
        
        # Add some demo materials
        if st.button("Load Demo Materials"):
            demo_materials = [
                ("Week 1: Introduction", "Welcome to the course! This week we'll cover the fundamentals...", "lecture", 1),
                ("Week 1: Reading Assignment", "Please read Chapters 1-3 of the textbook...", "reading", 1),
                ("Week 2: Video Lecture", "Watch the recorded lecture on advanced topics...", "video", 2),
                ("Week 2: Quiz", "Test your understanding with this week's quiz...", "quiz", 2),
            ]
            
            for title, content, mat_type, week in demo_materials:
                db.add_course_material(student['code_module'], title, content, material_type=mat_type, week=week)
            
            st.success("Demo materials loaded!")
            st.rerun()
    else:
        # Group by week
        weeks = sorted(set(m['week'] for m in materials if m['week']))
        
        for week in weeks:
            st.subheader(f"📅 Week {week}")
            
            week_materials = [m for m in materials if m.get('week') == week]
            
            for material in week_materials:
                with st.expander(f"{material['title']} ({material.get('material_type', 'resource')})"):
                    st.write(material['content'])
                    
                    # Log activity when student views material
                    if st.button(f"Mark as viewed", key=f"view_{material['id']}"):
                        db.log_activity(
                            st.session_state.student_id,
                            'view_material',
                            resource_id=material['id'],
                            resource_type=material.get('material_type'),
                            date=datetime.now().day
                        )
                        st.success("Activity logged!")


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
    
    # Load chat history
    if not st.session_state.chat_history:
        history = db.get_chat_history(st.session_state.student_id, limit=10)
        st.session_state.chat_history = list(reversed(history))
    
    # Display chat history
    st.subheader("Chat History")
    
    chat_container = st.container()
    
    with chat_container:
        for chat in st.session_state.chat_history:
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {chat['message']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>AI Advisor:</strong> {chat['response']}
            </div>
            """, unsafe_allow_html=True)
    
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
            # Get response from RAG
            result = rag.chat(user_input, student_data=st.session_state.student_data)
            
            # Save to database
            db.log_chat(
                st.session_state.student_id,
                user_input,
                result['response'],
                context=str(result.get('context_used', []))
            )
            
            # Add to session
            st.session_state.chat_history.append({
                'message': user_input,
                'response': result['response'],
                'timestamp': datetime.now()
            })
            
            st.rerun()
    
    # Suggested questions
    st.markdown("---")
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
                # Manually add suggestion as a chat
                with st.spinner("AI is thinking..."):
                    result = rag.chat(suggestion, student_data=st.session_state.student_data)
                    db.log_chat(
                        st.session_state.student_id,
                        suggestion,
                        result['response'],
                        context=str(result.get('context_used', []))
                    )
                    st.session_state.chat_history.append({
                        'message': suggestion,
                        'response': result['response'],
                        'timestamp': datetime.now()
                    })
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

