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


def main():
    """Main application."""
    
    # Sidebar navigation
    st.sidebar.title("🎓 PLAF Navigation")
    
    page = st.sidebar.radio(
        "Go to",
        ["Overview", "Student List", "Student Details", "About"]
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


if __name__ == "__main__":
    main()

