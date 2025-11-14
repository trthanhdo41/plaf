"""
Streamlit dashboard for PLAF.

Main application for Academic Advisors to view student risk and advice.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import sys
import os
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.train import ModelTrainer
from explainability.shap_explainer import SHAPExplainer
from prescriptive.llm_advisor import generate_simple_advice

# Page config
st.set_page_config(
    page_title="PLAF - Student Risk Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .risk-high {
        background-color: #ffebee;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #f44336;
    }
    .risk-medium {
        background-color: #fff3e0;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ff9800;
    }
    .risk-low {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load processed data and predictions."""
    try:
        # Load your processed data
        data = pd.read_csv('data/processed/student_predictions.csv')
        return data
    except FileNotFoundError:
        st.error("Data file not found. Please run the pipeline first.")
        return None


@st.cache_resource
def load_model():
    """Load trained model."""
    try:
        model_data = joblib.load('models/best_model.pkl')
        return model_data
    except FileNotFoundError:
        st.warning("Model file not found. Using demo mode.")
        return None


def create_risk_gauge(risk_probability: float):
    """Create a gauge chart for risk probability."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Level (%)"},
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
    return fig


def overview_page(data):
    """Overview page with statistics."""
    st.title("📊 PLAF Dashboard - Overview")
    
    if data is None:
        st.info("No data loaded. This is demo mode.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_students = len(data)
    at_risk = data['is_at_risk'].sum() if 'is_at_risk' in data.columns else len(data) * 0.3
    at_risk_pct = (at_risk / total_students) * 100
    
    with col1:
        st.metric("Total Students", f"{total_students:,}")
    
    with col2:
        st.metric("At-Risk Students", f"{int(at_risk):,}", 
                 delta=f"{at_risk_pct:.1f}%", delta_color="inverse")
    
    with col3:
        safe_students = total_students - at_risk
        st.metric("Safe Students", f"{int(safe_students):,}")
    
    with col4:
        high_risk = int(at_risk * 0.4)  # Assume 40% are high risk
        st.metric("High Risk", f"{high_risk:,}", delta="Priority")
    
    # Risk distribution
    st.subheader("Risk Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        risk_counts = pd.DataFrame({
            'Category': ['Safe', 'At-Risk'],
            'Count': [safe_students, at_risk]
        })
        
        fig = px.pie(risk_counts, values='Count', names='Category',
                    color='Category',
                    color_discrete_map={'Safe': '#4caf50', 'At-Risk': '#f44336'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart by course
        if 'code_module' in data.columns:
            course_risk = data.groupby('code_module')['is_at_risk'].agg(['sum', 'count'])
            course_risk['percentage'] = (course_risk['sum'] / course_risk['count']) * 100
            course_risk = course_risk.reset_index()
            
            fig = px.bar(course_risk, x='code_module', y='percentage',
                        title='At-Risk % by Course',
                        labels={'percentage': 'At-Risk %', 'code_module': 'Course'})
            st.plotly_chart(fig, use_container_width=True)


def student_list_page(data):
    """Student list with search and filter."""
    st.title("👥 Student List")
    
    if data is None:
        st.info("Demo mode - No data loaded")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_filter = st.selectbox(
            "Risk Level",
            ["All", "At-Risk Only", "Safe Only"]
        )
    
    with col2:
        if 'code_module' in data.columns:
            courses = ['All'] + list(data['code_module'].unique())
            course_filter = st.selectbox("Course", courses)
    
    with col3:
        search = st.text_input("Search Student ID")
    
    # Apply filters
    filtered_data = data.copy()
    
    if risk_filter == "At-Risk Only":
        filtered_data = filtered_data[filtered_data['is_at_risk'] == 1]
    elif risk_filter == "Safe Only":
        filtered_data = filtered_data[filtered_data['is_at_risk'] == 0]
    
    if course_filter != 'All':
        filtered_data = filtered_data[filtered_data['code_module'] == course_filter]
    
    if search:
        filtered_data = filtered_data[filtered_data['id_student'].astype(str).str.contains(search)]
    
    # Display table
    st.write(f"Showing {len(filtered_data)} students")
    
    # Select columns to display
    display_cols = ['id_student', 'code_module', 'is_at_risk']
    if 'risk_probability' in filtered_data.columns:
        display_cols.append('risk_probability')
    
    display_df = filtered_data[display_cols].copy()
    
    if 'risk_probability' in display_df.columns:
        display_df['risk_probability'] = display_df['risk_probability'].round(3)
    
    st.dataframe(display_df, use_container_width=True)
    
    # Select student for details
    if len(filtered_data) > 0:
        student_id = st.selectbox(
            "Select student for detailed view:",
            filtered_data['id_student'].unique()
        )
        
        if st.button("View Details"):
            st.session_state['selected_student'] = student_id
            st.rerun()


def student_detail_page(data, model_data):
    """Individual student detail page."""
    st.title("🎓 Student Detail View")
    
    if 'selected_student' not in st.session_state:
        st.info("Please select a student from the Student List page")
        return
    
    student_id = st.session_state['selected_student']
    
    if data is None:
        # Demo mode
        st.write(f"**Student ID:** {student_id}")
        st.write("Demo data - showing example layout")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Risk gauge
            demo_risk = 0.75
            fig = create_risk_gauge(demo_risk)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Risk Factors")
            st.markdown("""
            <div class="risk-high">
            <h4>⚠️ Main Risk Factors:</h4>
            <ul>
                <li>Low average score (45%)</li>
                <li>Minimal VLE engagement (20 clicks/week)</li>
                <li>Late submissions (3 assignments)</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.subheader("📋 Recommended Actions")
        
        recommendations = [
            {
                'action': "Increase average score from 45% to 65%",
                'reason': "Higher grades strongly correlate with completion",
                'priority': 'High'
            },
            {
                'action': "Engage with learning platform daily",
                'reason': "Regular interaction improves understanding",
                'priority': 'High'
            },
            {
                'action': "Submit assignments on time",
                'reason': "Avoid falling behind in coursework",
                'priority': 'Medium'
            }
        ]
        
        for i, rec in enumerate(recommendations):
            with st.expander(f"💡 Recommendation {i+1}: {rec['action']}", expanded=(i==0)):
                st.write(f"**Priority:** {rec['priority']}")
                st.write(f"**Reason:** {rec['reason']}")
                st.write(f"**Expected Impact:** Significantly improves completion probability")
        
        return
    
    # Real data mode
    student_data = data[data['id_student'] == student_id].iloc[0]
    
    # Student basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Student ID:** {student_id}")
    with col2:
        st.write(f"**Course:** {student_data.get('code_module', 'N/A')} - {student_data.get('code_presentation', 'N/A')}")
    with col3:
        st.write(f"**Final Result:** {student_data.get('final_result', 'N/A')}")
    
    # Student study duration and participation
    st.subheader("📚 Study Information")
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    
    with info_col1:
        # Use available data fields
        if 'num_days_active' in student_data:
            days_active = int(student_data['num_days_active'])
            st.metric("Days Active", f"{days_active} days")
        elif 'total_clicks' in student_data:
            # Estimate based on clicks (rough calculation)
            total_clicks = int(student_data['total_clicks'])
            estimated_days = max(1, total_clicks // 20)  # Assume 20 clicks per day average
            st.metric("Days Active", f"~{estimated_days} days")
        else:
            st.metric("Days Active", "📊 Calculating...")
    
    with info_col2:
        if 'total_clicks' in student_data:
            total_clicks = int(student_data['total_clicks'])
            if 'num_days_active' in student_data:
                days_active = int(student_data['num_days_active'])
                avg_daily = total_clicks / max(days_active, 1)
            else:
                avg_daily = total_clicks / max(1, total_clicks // 20)
            st.metric("Daily Engagement", f"{avg_daily:.1f} clicks/day")
        else:
            st.metric("Daily Engagement", "📊 Calculating...")
    
    with info_col3:
        if 'num_assessments' in student_data:
            assessments = int(student_data['num_assessments'])
            st.metric("Assessments", f"{assessments} completed")
        elif 'final_result' in student_data and student_data['final_result'] != 'N/A':
            # Use final result as assessment indicator
            result = student_data['final_result']
            st.metric("Course Status", f"{result}")
        else:
            st.metric("Assessments", "📊 In Progress")
    
    with info_col4:
        if 'avg_score' in student_data:
            avg_score = student_data['avg_score']
            score_status = "🟢 Good" if avg_score >= 70 else "🟡 Average" if avg_score >= 50 else "🔴 Low"
            st.metric("Average Score", f"{avg_score:.1f}% {score_status}")
        elif 'final_result' in student_data:
            result = student_data['final_result']
            if result in ['Pass', 'Distinction']:
                st.metric("Course Result", f"✅ {result}")
            elif result in ['Fail', 'Withdrawn']:
                st.metric("Course Result", f"❌ {result}")
            else:
                st.metric("Course Result", f"📊 {result}")
        else:
            st.metric("Course Progress", "📊 Ongoing")
    
    # Risk assessment
    col1, col2 = st.columns([1, 2])
    
    with col1:
        risk_prob = student_data.get('risk_probability', student_data['is_at_risk'])
        fig = create_risk_gauge(risk_prob)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Risk Analysis")
        
        # Risk explanation
        risk_percentage = risk_prob * 100 if risk_prob <= 1 else risk_prob
        
        if risk_percentage >= 70:
            risk_color = "🔴"
            risk_text = "HIGH RISK"
            risk_explanation = "Student shows strong indicators of potential course failure"
        elif risk_percentage >= 40:
            risk_color = "🟡"
            risk_text = "MEDIUM RISK"
            risk_explanation = "Student shows some concerning patterns that need attention"
        else:
            risk_color = "🟢"
            risk_text = "LOW RISK"
            risk_explanation = "Student is performing well and on track for success"
        
        # Better contrast colors
        if risk_percentage >= 70:
            bg_color = "#ffebee"
            text_color = "#c62828"
            border_color = "#f44336"
        elif risk_percentage >= 40:
            bg_color = "#fff3e0"
            text_color = "#ef6c00"
            border_color = "#ff9800"
        else:
            bg_color = "#e8f5e9"
            text_color = "#2e7d32"
            border_color = "#4caf50"
        
        st.markdown(f"""
        <div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; border-left: 4px solid {border_color}; margin: 10px 0;">
        <h4 style="color: {text_color}; margin: 0 0 8px 0;">{risk_color} Risk Level: {risk_text}</h4>
        <p style="color: {text_color}; margin: 0; font-weight: 500;">{risk_explanation}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key performance indicators
        st.subheader("📊 Key Performance Indicators")
        metrics_col1, metrics_col2 = st.columns(2)
        
        with metrics_col1:
            if 'total_clicks' in student_data:
                clicks = int(student_data['total_clicks'])
                click_status = "🟢 Good" if clicks >= 500 else "🟡 Average" if clicks >= 200 else "🔴 Low"
                st.metric("VLE Engagement", f"{clicks} clicks {click_status}")
            
            if 'num_days_active' in student_data:
                days = int(student_data['num_days_active'])
                day_status = "🟢 Good" if days >= 30 else "🟡 Average" if days >= 14 else "🔴 Low"
                st.metric("Activity Level", f"{days} days {day_status}")
        
        with metrics_col2:
            if 'avg_score' in student_data:
                score = student_data['avg_score']
                score_status = "🟢 Good" if score >= 70 else "🟡 Average" if score >= 50 else "🔴 Low"
                st.metric("Academic Performance", f"{score:.1f}% {score_status}")
            
            if 'num_assessments' in student_data:
                assessments = int(student_data['num_assessments'])
                assess_status = "🟢 Good" if assessments >= 5 else "🟡 Average" if assessments >= 3 else "🔴 Low"
                st.metric("Assessment Completion", f"{assessments} {assess_status}")


def quiz_management_page():
    """Quiz Management page for CRUD operations."""
    st.title("🎯 Quiz Management")
    
    # Import database
    from database.models import get_db
    db = get_db()
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📋 View Quizzes", "➕ Create Quiz", "✏️ Edit Quiz"])
    
    with tab1:
        st.subheader("📋 All Quizzes")
        
        # Get all quizzes with course and lesson info
        conn = db.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT q.id, q.title, q.duration_minutes, q.passing_score, q.max_attempts,
                   c.title as course_title, l.title as lesson_title,
                   COUNT(qq.id) as question_count
            FROM quizzes q
            JOIN courses c ON q.course_id = c.id
            JOIN lessons l ON q.lesson_id = l.id
            LEFT JOIN quiz_questions qq ON q.id = qq.quiz_id
            GROUP BY q.id
            ORDER BY c.id, l.id
        """)
        
        quizzes = cursor.fetchall()
        
        if quizzes:
            # Display as dataframe
            quiz_data = []
            for quiz in quizzes:
                quiz_data.append({
                    'ID': quiz['id'],
                    'Course': quiz['course_title'],
                    'Lesson': quiz['lesson_title'],
                    'Quiz Title': quiz['title'],
                    'Duration (min)': quiz['duration_minutes'],
                    'Passing Score (%)': quiz['passing_score'],
                    'Max Attempts': quiz['max_attempts'],
                    'Questions': quiz['question_count']
                })
            
            df = pd.DataFrame(quiz_data)
            st.dataframe(df, use_container_width=True)
            
            # Quiz statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Quizzes", len(quizzes))
            with col2:
                avg_duration = sum(q['duration_minutes'] for q in quizzes) / len(quizzes)
                st.metric("Avg Duration", f"{avg_duration:.1f} min")
            with col3:
                avg_questions = sum(q['question_count'] for q in quizzes) / len(quizzes)
                st.metric("Avg Questions", f"{avg_questions:.1f}")
            with col4:
                quizzes_with_questions = sum(1 for q in quizzes if q['question_count'] > 0)
                st.metric("With Questions", f"{quizzes_with_questions}/{len(quizzes)}")
        else:
            st.info("No quizzes found.")
    
    with tab2:
        st.subheader("➕ Create New Quiz")
        
        # Get courses and lessons for dropdown
        cursor.execute("SELECT id, title FROM courses ORDER BY title")
        courses = cursor.fetchall()
        
        if courses:
            with st.form("create_quiz_form"):
                # Course selection
                course_options = {f"{c['title']} (ID: {c['id']})": c['id'] for c in courses}
                selected_course = st.selectbox("Select Course", options=list(course_options.keys()))
                course_id = course_options[selected_course]
                
                # Lesson selection
                cursor.execute("SELECT id, title FROM lessons WHERE course_id = ? ORDER BY lesson_order", (course_id,))
                lessons = cursor.fetchall()
                
                if lessons:
                    lesson_options = {f"{l['title']} (ID: {l['id']})": l['id'] for l in lessons}
                    selected_lesson = st.selectbox("Select Lesson", options=list(lesson_options.keys()))
                    lesson_id = lesson_options[selected_lesson]
                    
                    # Quiz details
                    quiz_title = st.text_input("Quiz Title", placeholder="e.g., JavaScript Basics Quiz")
                    quiz_description = st.text_area("Description", placeholder="Test your knowledge of JavaScript fundamentals")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        duration = st.number_input("Duration (minutes)", min_value=1, max_value=180, value=15)
                    with col2:
                        passing_score = st.number_input("Passing Score (%)", min_value=0.0, max_value=100.0, value=70.0, step=5.0)
                    with col3:
                        max_attempts = st.number_input("Max Attempts", min_value=1, max_value=10, value=3)
                    
                    if st.form_submit_button("🎯 Create Quiz"):
                        if quiz_title:
                            try:
                                quiz_id = db.create_quiz(
                                    course_id=course_id,
                                    lesson_id=lesson_id,
                                    title=quiz_title,
                                    description=quiz_description,
                                    duration_minutes=duration,
                                    passing_score=passing_score,
                                    max_attempts=max_attempts
                                )
                                st.success(f"✅ Quiz created successfully! Quiz ID: {quiz_id}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to create quiz: {e}")
                        else:
                            st.error("Please enter a quiz title")
                else:
                    st.warning("No lessons found for this course")
        else:
            st.warning("No courses found. Please create courses first.")
    
    with tab3:
        st.subheader("✏️ Edit Quiz")
        
        # Get all quizzes for selection
        cursor.execute("""
            SELECT q.id, q.title, c.title as course_title, l.title as lesson_title
            FROM quizzes q
            JOIN courses c ON q.course_id = c.id
            JOIN lessons l ON q.lesson_id = l.id
            ORDER BY c.title, l.title
        """)
        edit_quizzes = cursor.fetchall()
        
        if edit_quizzes:
            quiz_options = {f"{q['course_title']} → {q['lesson_title']} → {q['title']} (ID: {q['id']})": q['id'] for q in edit_quizzes}
            selected_quiz = st.selectbox("Select Quiz to Edit", options=list(quiz_options.keys()))
            quiz_id = quiz_options[selected_quiz]
            
            # Get quiz details
            cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
            quiz = cursor.fetchone()
            
            if quiz:
                with st.form("edit_quiz_form"):
                    st.write(f"**Editing Quiz ID: {quiz_id}**")
                    
                    new_title = st.text_input("Quiz Title", value=quiz['title'])
                    new_description = st.text_area("Description", value=quiz['description'] if 'description' in quiz.keys() else '')
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_duration = st.number_input("Duration (minutes)", min_value=1, max_value=180, value=quiz['duration_minutes'])
                    with col2:
                        new_passing_score = st.number_input("Passing Score (%)", min_value=0.0, max_value=100.0, value=quiz['passing_score'], step=5.0)
                    with col3:
                        new_max_attempts = st.number_input("Max Attempts", min_value=1, max_value=10, value=quiz['max_attempts'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Update Quiz"):
                            try:
                                cursor.execute("""
                                    UPDATE quizzes 
                                    SET title = ?, description = ?, duration_minutes = ?, 
                                        passing_score = ?, max_attempts = ?
                                    WHERE id = ?
                                """, (new_title, new_description, new_duration, new_passing_score, new_max_attempts, quiz_id))
                                conn.commit()
                                st.success("✅ Quiz updated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to update quiz: {e}")
                    
                    with col2:
                        if st.form_submit_button("🗑️ Delete Quiz", type="secondary"):
                            try:
                                # Delete quiz questions first
                                cursor.execute("DELETE FROM quiz_questions WHERE quiz_id = ?", (quiz_id,))
                                # Delete quiz results
                                cursor.execute("DELETE FROM quiz_results WHERE quiz_id = ?", (quiz_id,))
                                # Delete quiz
                                cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
                                conn.commit()
                                st.success("✅ Quiz deleted successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to delete quiz: {e}")
                
                # Show quiz questions
                st.subheader("📝 Quiz Questions")
                cursor.execute("SELECT * FROM quiz_questions WHERE quiz_id = ? ORDER BY question_order", (quiz_id,))
                questions = cursor.fetchall()
                
                if questions:
                    for i, q in enumerate(questions):
                        with st.expander(f"Question {i+1}: {q['question_text'][:50]}..."):
                            st.write(f"**Question:** {q['question_text']}")
                            if q['options']:
                                options = eval(q['options']) if isinstance(q['options'], str) else q['options']
                                for j, option in enumerate(options):
                                    marker = "✅" if j == q['correct_answer'] else "❌"
                                    st.write(f"{marker} {j+1}. {option}")
                            explanation = q['explanation'] if 'explanation' in q.keys() else 'No explanation provided'
                            points = q['points'] if 'points' in q.keys() else 1
                            st.write(f"**Explanation:** {explanation}")
                            st.write(f"**Points:** {points}")
                else:
                    st.info("No questions found for this quiz.")
                    st.write("💡 **Tip:** Questions are created automatically when quizzes are generated, or you can add them manually through the database.")
        else:
            st.info("No quizzes found to edit.")


def main():
    """Main application."""
    
    # Sidebar navigation
    st.sidebar.title("🎓 PLAF Navigation")
    
    page = st.sidebar.radio(
        "Go to",
        ["Overview", "Student List", "Student Details", "Course Management", "Quiz Management", "About"]
    )
    
    # Load data
    data = load_data()
    model_data = load_model()
    
    # Route to pages
    if page == "Overview":
        overview_page(data)
    
    elif page == "Student List":
        student_list_page(data)
    
    elif page == "Student Details":
        student_detail_page(data, model_data)
    
    elif page == "Course Management":
        course_management_page()
    
    elif page == "Quiz Management":
        quiz_management_page()
    
    elif page == "About":
        st.title("ℹ️ About PLAF")
        st.markdown("""
        ## Prescriptive Learning Analytics Framework
        
        This system uses advanced machine learning and AI to:
        
        1. **Predict** which students are at risk of not completing their course
        2. **Explain** why students are flagged as at-risk using SHAP and Anchors
        3. **Prescribe** specific, actionable advice using counterfactual analysis and LLM
        
        ### Methodology
        
        - **Predictive Models:** Random Forest, CatBoost, XGBoost, Logistic Regression, SVM
        - **Explainability:** SHAP (global & local), Anchors (rule-based)
        - **Prescriptive:** DiCE (counterfactuals), Gemini LLM (natural language advice)
        
        ### Dataset
        
        Open University Learning Analytics Dataset (OULAD) from Kaggle
        
        ### References
        
        Based on research by Teo Susnjak (arXiv:2208.14582)
        
        ---
        
        **Developed for academic purposes**
        """)


def course_management_page():
    """Course Management CRUD interface."""
    st.title("⚙️ Course Management")
    st.markdown("**Admin Panel - Manage Courses, Lessons & Content**")
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📚 View Courses", "➕ Add Course", "🔧 Manage Lessons"])
    
    with tab1:
        view_courses_tab()
    
    with tab2:
        add_course_tab()
    
    with tab3:
        manage_lessons_tab()


def view_courses_tab():
    """View and edit existing courses."""
    st.subheader("📚 All Courses")
    
    try:
        # Get courses from API
        response = requests.get("http://localhost:8000/api/courses", timeout=10)
        
        if response.status_code == 200:
            courses_data = response.json()
            courses = courses_data.get('courses', [])
            
            if courses:
                # Display courses in a nice format
                for course in courses:
                    with st.expander(f"📖 {course['title']} ({course['level']})"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Description:** {course['description']}")
                            st.write(f"**Instructor:** {course['instructor_name']}")
                            st.write(f"**Duration:** {course.get('duration_hours', 0)} hours")
                            st.write(f"**Category:** {course.get('category', 'N/A')}")
                            st.write(f"**Dataset Module Code:** {course.get('code_module') or 'Not linked'}")
                            
                            if course.get('thumbnail_url'):
                                st.image(course['thumbnail_url'], width=200)
                        
                        with col2:
                            st.write("**Actions:**")
                            
                            # Edit button
                            if st.button(f"✏️ Edit", key=f"edit_{course['id']}"):
                                st.session_state[f"editing_course_{course['id']}"] = True
                            
                            # Delete button
                            if st.button(f"🗑️ Delete", key=f"delete_{course['id']}"):
                                if st.session_state.get(f"confirm_delete_{course['id']}", False):
                                    # Actually delete
                                    delete_response = requests.delete(f"http://localhost:8000/api/admin/courses/{course['id']}")
                                    if delete_response.status_code == 200:
                                        st.success(f"Deleted course: {course['title']}")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete course")
                                else:
                                    st.session_state[f"confirm_delete_{course['id']}"] = True
                                    st.warning("Click delete again to confirm")
                        
                        # Edit form (if editing)
                        if st.session_state.get(f"editing_course_{course['id']}", False):
                            st.markdown("---")
                            edit_course_form(course)
            else:
                st.info("No courses found.")
        else:
            st.error("Failed to load courses from API")
            
    except Exception as e:
        st.error(f"Error: {e}")


def edit_course_form(course):
    """Edit course form."""
    st.subheader(f"✏️ Edit: {course['title']}")
    
    with st.form(f"edit_course_{course['id']}"):
        title = st.text_input("Title", value=course['title'])
        description = st.text_area("Description", value=course['description'])
        instructor_name = st.text_input("Instructor Name", value=course['instructor_name'])
        instructor_title = st.text_input("Instructor Title", value=course.get('instructor_title', ''))
        duration_hours = st.number_input("Duration (hours)", value=course.get('duration_hours', 0), min_value=0)
        level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"], 
                            index=["Beginner", "Intermediate", "Advanced"].index(course.get('level', 'Beginner')))
        category = st.text_input("Category", value=course.get('category', ''))

        # Dataset module mapping (code_module from OULAD)
        try:
            from database.models import get_db
            db = get_db()
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT code_module FROM students WHERE code_module != '' ORDER BY code_module")
            modules = [row["code_module"] for row in cursor.fetchall()]
        except Exception:
            modules = []

        module_options = ["(None)"] + modules if modules else ["(None)"]
        current_module = course.get('code_module') or "(None)"
        if current_module not in module_options:
            module_options.append(current_module)
        code_module = st.selectbox("Dataset Module Code (optional)", module_options,
                                   index=module_options.index(current_module) if current_module in module_options else 0)
        
        # Image upload section
        st.markdown("**Course Thumbnail:**")
        uploaded_file = st.file_uploader("Upload new image", type=['png', 'jpg', 'jpeg'], key=f"upload_{course['id']}")
        thumbnail_url = st.text_input("Or paste image URL", value=course.get('thumbnail_url', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save Changes"):
                try:
                    # Handle image upload first
                    final_thumbnail_url = thumbnail_url
                    
                    if uploaded_file is not None:
                        # Upload to ImgBB
                        files = {"file": uploaded_file.getvalue()}
                        upload_response = requests.post("http://localhost:8000/api/upload-image", files=files)
                        
                        if upload_response.status_code == 200:
                            upload_data = upload_response.json()
                            final_thumbnail_url = upload_data['url']
                            st.success(f"✅ Image uploaded: {upload_data['filename']}")
                        else:
                            st.warning("⚠️ Image upload failed, using existing URL")
                    
                    update_data = {
                        "title": title,
                        "description": description,
                        "instructor_name": instructor_name,
                        "instructor_title": instructor_title,
                        "duration_hours": duration_hours,
                        "level": level,
                        "category": category,
                        "thumbnail_url": final_thumbnail_url,
                        "code_module": None if code_module == "(None)" else code_module,
                    }
                    
                    response = requests.put(f"http://localhost:8000/api/admin/courses/{course['id']}", 
                                          json=update_data)
                    
                    if response.status_code == 200:
                        st.success("Course updated successfully!")
                        st.session_state[f"editing_course_{course['id']}"] = False
                        st.rerun()
                    else:
                        st.error("Failed to update course")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state[f"editing_course_{course['id']}"] = False
                st.rerun()


def add_course_tab():
    """Add new course form."""
    st.subheader("➕ Add New Course")
    
    with st.form("add_course"):
        title = st.text_input("Course Title *", placeholder="e.g., Advanced Python Programming")
        description = st.text_area("Description *", placeholder="Course description...")
        instructor_name = st.text_input("Instructor Name *", placeholder="e.g., Dr. John Smith")
        instructor_title = st.text_input("Instructor Title", placeholder="e.g., Senior Software Engineer")
        duration_hours = st.number_input("Duration (hours)", min_value=1, value=10)
        level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
        category = st.text_input("Category *", placeholder="e.g., Programming, Data Science")

        # Dataset module mapping (from OULAD)
        try:
            from database.models import get_db
            db = get_db()
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT code_module FROM students WHERE code_module != '' ORDER BY code_module")
            modules = [row["code_module"] for row in cursor.fetchall()]
        except Exception:
            modules = []

        module_options = ["(None)"] + modules if modules else ["(None)"]
        code_module = st.selectbox("Dataset Module Code (optional)", module_options)
        
        # Image upload
        st.markdown("**Course Thumbnail:**")
        uploaded_file = st.file_uploader("Upload image", type=['png', 'jpg', 'jpeg'])
        thumbnail_url = st.text_input("Or paste image URL", placeholder="https://...")
        
        if st.form_submit_button("🚀 Create Course"):
            if not all([title, description, instructor_name, category]):
                st.error("Please fill in all required fields (*)")
            else:
                try:
                    import requests
                    
                    # Upload image if provided
                    final_thumbnail_url = thumbnail_url
                    
                    if uploaded_file is not None:
                        # Upload to ImgBB
                        files = {"file": uploaded_file.getvalue()}
                        upload_response = requests.post("http://localhost:8000/api/upload-image", files=files)
                        
                        if upload_response.status_code == 200:
                            upload_data = upload_response.json()
                            final_thumbnail_url = upload_data['url']
                            st.success(f"Image uploaded: {upload_data['filename']}")
                        else:
                            st.warning("Image upload failed, proceeding without image")
                    
                    # Create course
                    course_data = {
                        "title": title,
                        "description": description,
                        "instructor_name": instructor_name,
                        "instructor_title": instructor_title,
                        "duration_hours": duration_hours,
                        "level": level,
                        "category": category,
                        "thumbnail_url": final_thumbnail_url,
                        "code_module": None if code_module == "(None)" else code_module,
                    }
                    
                    response = requests.post("http://localhost:8000/api/admin/courses", json=course_data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Course created successfully! ID: {result['course_id']}")
                        st.balloons()
                    else:
                        st.error("Failed to create course")
                        
                except Exception as e:
                    st.error(f"Error: {e}")


def manage_lessons_tab():
    """Manage lessons for courses."""
    st.subheader("🔧 Lesson Management")
    
    try:
        import requests
        
        # Get courses for selection
        response = requests.get("http://localhost:8000/api/courses")
        
        if response.status_code == 200:
            courses_data = response.json()
            courses = courses_data.get('courses', [])
            
            if courses:
                # Course selection
                course_options = {f"{course['title']} (ID: {course['id']})": course['id'] 
                                for course in courses}
                
                selected_course_name = st.selectbox("Select Course:", list(course_options.keys()))
                selected_course_id = course_options[selected_course_name]
                
                # Find selected course info
                selected_course = next((c for c in courses if c['id'] == selected_course_id), None)
                
                # Get course details with lessons
                course_response = requests.get(f"http://localhost:8000/api/courses/{selected_course_id}")
                
                if course_response.status_code == 200:
                    course_data = course_response.json()
                    lessons = course_data.get('lessons', [])
                    
                    # Use course title from the courses list
                    course_title = selected_course['title'] if selected_course else course_data.get('title', 'N/A')
                    st.write(f"**Course:** {course_title}")
                    st.write(f"**Total Lessons:** {len(lessons)}")

                    # Add new lesson form
                    st.markdown("### ➕ Add New Lesson")
                    with st.form(f"add_lesson_{selected_course_id}"):
                        new_title = st.text_input("Lesson Title *", placeholder="e.g., Introduction")
                        new_type = st.selectbox("Type", ["video", "reading", "quiz"], index=0)
                        new_video_url = st.text_input(
                            "Video URL (YouTube)",
                            placeholder="https://www.youtube.com/watch?v=...",
                            help="Supports: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/embed/ID"
                        )
                        new_content = st.text_area(
                            "Content",
                            placeholder="Lesson content or description",
                            height=100
                        )
                        new_duration = st.number_input("Duration (minutes)", min_value=0, value=15)
                        new_is_free = st.checkbox("Free lesson", value=False)

                        if st.form_submit_button("🚀 Create Lesson"):
                            if not new_title:
                                st.error("Please enter a lesson title")
                            else:
                                try:
                                    from database.models import get_db

                                    db = get_db()
                                    conn = db.connect()
                                    cursor = conn.cursor()

                                    # Determine next lesson order
                                    existing_orders = [
                                        l.get('lesson_order') for l in lessons
                                        if l.get('lesson_order') is not None
                                    ]
                                    next_order = max(existing_orders) + 1 if existing_orders else 1

                                    cursor.execute(
                                        """
                                        INSERT INTO lessons (
                                            course_id,
                                            title,
                                            content,
                                            video_url,
                                            lesson_type,
                                            duration_minutes,
                                            lesson_order,
                                            is_free
                                        )
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                        """,
                                        (
                                            selected_course_id,
                                            new_title,
                                            new_content,
                                            new_video_url,
                                            new_type,
                                            new_duration,
                                            next_order,
                                            int(new_is_free),
                                        ),
                                    )
                                    conn.commit()
                                    st.success("✅ Lesson created successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error creating lesson: {e}")

                    # Display lessons
                    if lessons:
                        st.markdown("### 📝 Current Lessons:")
                        for lesson in lessons:
                            with st.expander(f"Lesson {lesson.get('lesson_order', '?')}: {lesson.get('title', 'Untitled')}"):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.write(f"**Type:** {lesson.get('lesson_type', 'N/A')}")
                                    st.write(f"**Duration:** {lesson.get('duration_minutes', 0)} minutes")
                                    st.write(f"**Content:** {lesson.get('content', 'No content')}")
                                    if lesson.get('video_url'):
                                        st.write(f"**Video:** {lesson['video_url']}")
                                    st.write(f"**Free:** {'Yes' if lesson.get('is_free') else 'No'}")
                                
                                with col2:
                                    if st.button(f"✏️ Edit", key=f"edit_lesson_{lesson.get('id')}"):
                                        st.session_state[f"editing_lesson_{lesson.get('id')}"] = True
                                
                                # Edit form
                                if st.session_state.get(f"editing_lesson_{lesson.get('id')}", False):
                                    st.markdown("---")
                                    edit_lesson_form(lesson, selected_course_id)
                    else:
                        st.info("No lessons found for this course.")
                else:
                    st.error("Failed to load course details")
            else:
                st.info("No courses available.")
        else:
            st.error("Failed to load courses")
            
    except Exception as e:
        st.error(f"Error: {e}")


def edit_lesson_form(lesson, course_id):
    """Edit lesson form with video URL and content."""
    st.subheader(f"✏️ Edit Lesson: {lesson.get('title', 'Untitled')}")
    
    with st.form(f"edit_lesson_{lesson.get('id')}"):
        title = st.text_input("Lesson Title", value=lesson.get('title', ''))
        content = st.text_area("Content", value=lesson.get('content', ''), height=100)
        video_url = st.text_input("Video URL (YouTube)", value=lesson.get('video_url', ''), 
                                  help="Supports: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/embed/ID")
        
        # Show current video preview if URL exists
        if lesson.get('video_url'):
            st.write("**Current Video:**")
            video_id = None
            url = lesson.get('video_url', '')
            if 'youtube.com/watch?v=' in url:
                video_id = url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]
            elif 'youtube.com/embed/' in url:
                video_id = url.split('embed/')[1].split('?')[0]
            
            if video_id:
                st.video(f"https://www.youtube.com/watch?v={video_id}")
            else:
                st.write(f"URL: {url}")
        
        st.write("**Preview New URL:**")
        if video_url and video_url != lesson.get('video_url', ''):
            try:
                new_video_id = None
                if 'youtube.com/watch?v=' in video_url:
                    new_video_id = video_url.split('v=')[1].split('&')[0]
                elif 'youtu.be/' in video_url:
                    new_video_id = video_url.split('youtu.be/')[1].split('?')[0]
                elif 'youtube.com/embed/' in video_url:
                    new_video_id = video_url.split('embed/')[1].split('?')[0]
                
                if new_video_id:
                    st.video(f"https://www.youtube.com/watch?v={new_video_id}")
                else:
                    st.warning("Invalid YouTube URL format")
            except:
                st.warning("Could not preview video")
        duration_minutes = st.number_input("Duration (minutes)", value=lesson.get('duration_minutes', 0), min_value=0)
        lesson_type = st.selectbox("Type", ["video", "reading", "quiz"], 
                                  index=["video", "reading", "quiz"].index(lesson.get('lesson_type', 'video')))
        is_free = st.checkbox("Free lesson", value=lesson.get('is_free', False))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save Changes"):
                try:
                    # Update lesson via database (since we don't have lesson API endpoint)
                    from database.models import get_db
                    
                    db = get_db()
                    conn = db.connect()
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        UPDATE lessons 
                        SET title = ?, content = ?, video_url = ?, 
                            duration_minutes = ?, lesson_type = ?, is_free = ?
                        WHERE id = ?
                    """, (title, content, video_url, duration_minutes, lesson_type, is_free, lesson.get('id')))
                    
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        st.success("✅ Lesson updated successfully!")
                        st.session_state[f"editing_lesson_{lesson.get('id')}"] = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to update lesson")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state[f"editing_lesson_{lesson.get('id')}"] = False
                st.rerun()


if __name__ == "__main__":
    main()

