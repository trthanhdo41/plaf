"""
Benchmark Results Dashboard

Web interface to view and compare benchmark results.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from pathlib import Path
from datetime import datetime


def load_predictive_results():
    """Load predictive model benchmark results."""
    results_dir = Path("results")
    csv_files = list(results_dir.glob("predictive_benchmark_*.csv"))
    
    if not csv_files:
        return None
    
    # Get most recent file
    latest_file = max(csv_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    
    return df, latest_file.name


def load_rag_results():
    """Load RAG system benchmark results."""
    results_dir = Path("results")
    json_files = list(results_dir.glob("rag_benchmark_*.json"))
    
    if not json_files:
        return None
    
    # Get most recent file
    latest_file = max(json_files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data, latest_file.name


def load_llm_results():
    """Load LLM advice benchmark results."""
    results_dir = Path("results")
    json_files = list(results_dir.glob("llm_benchmark_*.json"))
    
    if not json_files:
        return None
    
    # Get most recent file
    latest_file = max(json_files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data, latest_file.name


def show_predictive_dashboard(df, filename):
    """Display predictive models benchmark dashboard."""
    st.header("Predictive Models Benchmark")
    st.caption(f"Source: {filename}")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    best_model = df.iloc[0]
    
    with col1:
        st.metric("Best Model", best_model['model'])
    with col2:
        st.metric("Test AUC", f"{best_model['test_auc']:.4f}")
    with col3:
        st.metric("Test F1", f"{best_model['test_f1']:.4f}")
    with col4:
        st.metric("Train Time", f"{best_model['train_time']:.1f}s")
    
    st.divider()
    
    # Model comparison table
    st.subheader("Model Comparison")
    
    display_df = df[['model', 'test_auc', 'test_f1', 'test_precision', 
                     'test_recall', 'test_accuracy', 'train_time']].copy()
    display_df.columns = ['Model', 'AUC', 'F1', 'Precision', 'Recall', 'Accuracy', 'Train Time (s)']
    
    st.dataframe(
        display_df.style.format({
            'AUC': '{:.4f}',
            'F1': '{:.4f}',
            'Precision': '{:.4f}',
            'Recall': '{:.4f}',
            'Accuracy': '{:.4f}',
            'Train Time (s)': '{:.2f}'
        }).highlight_max(subset=['AUC', 'F1'], color='lightgreen'),
        use_container_width=True,
        hide_index=True
    )
    
    # Performance comparison chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("AUC Comparison")
        fig = px.bar(df, x='model', y='test_auc', 
                     title='Test AUC by Model',
                     labels={'model': 'Model', 'test_auc': 'AUC'},
                     color='test_auc',
                     color_continuous_scale='Viridis')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("F1-Score Comparison")
        fig = px.bar(df, x='model', y='test_f1',
                     title='Test F1-Score by Model',
                     labels={'model': 'Model', 'test_f1': 'F1-Score'},
                     color='test_f1',
                     color_continuous_scale='Blues')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Metrics radar chart
    st.subheader("Multi-Metric Comparison")
    
    # Prepare data for radar chart
    metrics = ['test_auc', 'test_f1', 'test_precision', 'test_recall', 'test_accuracy']
    metric_labels = ['AUC', 'F1', 'Precision', 'Recall', 'Accuracy']
    
    fig = go.Figure()
    
    for idx, row in df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row[m] for m in metrics],
            theta=metric_labels,
            fill='toself',
            name=row['model']
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Training time comparison
    st.subheader("Training Time Comparison")
    fig = px.bar(df.sort_values('train_time'), 
                 x='model', y='train_time',
                 title='Training Time by Model',
                 labels={'model': 'Model', 'train_time': 'Time (seconds)'},
                 color='train_time',
                 color_continuous_scale='Reds')
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)


def show_rag_dashboard(data, filename):
    """Display RAG system benchmark dashboard."""
    st.header("RAG System Benchmark")
    st.caption(f"Source: {filename}")
    
    summary = data.get('summary', {})
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Retrieval Relevance", f"{summary.get('avg_retrieval_relevance', 0):.3f}")
    with col2:
        st.metric("Response Quality", f"{summary.get('avg_response_quality', 0):.3f}")
    with col3:
        st.metric("Avg Latency", f"{summary.get('avg_end_to_end_latency', 0):.2f}s")
    
    st.divider()
    
    # Retrieval quality details
    if 'retrieval' in data:
        st.subheader("Retrieval Quality Analysis")
        
        retrieval_scores = data['retrieval']['scores']
        df_retrieval = pd.DataFrame(retrieval_scores)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Relevance by Category**")
            fig = px.bar(df_retrieval, x='category', y='relevance_score',
                        title='Retrieval Relevance by Question Category',
                        labels={'category': 'Category', 'relevance_score': 'Relevance Score'},
                        color='relevance_score',
                        color_continuous_scale='Greens')
            fig.update_layout(showlegend=False, height=400)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Retrieval Time**")
            fig = px.bar(df_retrieval, x='category', y='retrieval_time',
                        title='Retrieval Time by Category',
                        labels={'category': 'Category', 'retrieval_time': 'Time (s)'},
                        color='retrieval_time',
                        color_continuous_scale='Blues')
            fig.update_layout(showlegend=False, height=400)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        with st.expander("View Detailed Results"):
            st.dataframe(df_retrieval, use_container_width=True, hide_index=True)
    
    # Response quality details
    if 'response_quality' in data:
        st.subheader("Response Quality Analysis")
        
        quality_scores = data['response_quality']['scores']
        df_quality = pd.DataFrame(quality_scores)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Quality Score Distribution**")
            fig = px.histogram(df_quality, x='quality_score',
                             title='Distribution of Quality Scores',
                             labels={'quality_score': 'Quality Score'},
                             nbins=10)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Response Time by Category**")
            fig = px.bar(df_quality, x='category', y='response_time',
                        title='Response Generation Time',
                        labels={'category': 'Category', 'response_time': 'Time (s)'},
                        color='response_time',
                        color_continuous_scale='Oranges')
            fig.update_layout(showlegend=False, height=400)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)


def show_llm_dashboard(data, filename):
    """Display LLM advice benchmark dashboard."""
    st.header("LLM Advice Quality Benchmark")
    st.caption(f"Source: {filename}")
    
    summary = data.get('summary', {})
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Response Time", f"{summary.get('avg_response_time', 0):.2f}s")
    with col2:
        st.metric("Advice Quality", f"{summary.get('avg_quality', 0):.3f}")
    with col3:
        st.metric("Consistency", f"{summary.get('avg_consistency', 0):.3f}")
    with col4:
        st.metric("Relevance", f"{summary.get('avg_relevance', 0):.3f}")
    
    st.divider()
    
    # Quality breakdown
    if 'quality' in data:
        st.subheader("Advice Quality Breakdown")
        
        quality_scores = data['quality']['quality_scores']
        df_quality = pd.DataFrame(quality_scores)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Overall Quality by Risk Level**")
            risk_quality = df_quality.groupby('risk_level')['overall_quality'].mean().reset_index()
            fig = px.bar(risk_quality, x='risk_level', y='overall_quality',
                        title='Average Quality Score by Risk Level',
                        labels={'risk_level': 'Risk Level', 'overall_quality': 'Quality Score'},
                        color='overall_quality',
                        color_continuous_scale='Viridis')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Quality Components**")
            components = df_quality[['has_specific_numbers', 'has_actionable_steps', 
                                    'mentions_engagement', 'mentions_grades', 
                                    'is_personalized', 'has_encouragement']].mean()
            
            fig = px.bar(x=components.values, y=components.index, orientation='h',
                        title='Percentage of Advice Meeting Criteria',
                        labels={'x': 'Percentage', 'y': 'Criteria'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        with st.expander("View Detailed Quality Scores"):
            st.dataframe(df_quality, use_container_width=True, hide_index=True)
    
    # Response time analysis
    if 'response_time' in data:
        st.subheader("Response Time Analysis")
        
        response_times = data['response_time']['response_times']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Response Time Distribution**")
            fig = px.histogram(x=response_times, nbins=15,
                             title='Distribution of Response Times',
                             labels={'x': 'Response Time (s)', 'y': 'Count'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Response Time Statistics**")
            stats_df = pd.DataFrame({
                'Metric': ['Mean', 'Std Dev', 'Min', 'Max'],
                'Value (s)': [
                    data['response_time']['avg_time'],
                    data['response_time']['std_time'],
                    min(response_times),
                    max(response_times)
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)


def main():
    st.set_page_config(
        page_title="PLAF Benchmark Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("PLAF Benchmark Results Dashboard")
    st.markdown("View and analyze benchmark results from Predictive Models, RAG System, and LLM Advice")
    
    # Sidebar for navigation
    st.sidebar.header("Navigation")
    
    benchmark_type = st.sidebar.radio(
        "Select Benchmark",
        ["Predictive Models", "RAG System", "LLM Advice", "Overview"]
    )
    
    st.sidebar.divider()
    st.sidebar.info(
        "**Note:** Run benchmarks first to see results:\n\n"
        "`python tests/benchmark_predictive.py`\n\n"
        "`python tests/benchmark_rag.py`\n\n"
        "`python tests/benchmark_llm.py`"
    )
    
    # Main content
    if benchmark_type == "Overview":
        st.header("Benchmark Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Predictive Models")
            result = load_predictive_results()
            if result:
                df, filename = result
                st.success(f"Latest: {filename}")
                st.metric("Best Model", df.iloc[0]['model'])
                st.metric("Best AUC", f"{df.iloc[0]['test_auc']:.4f}")
            else:
                st.warning("No results found")
        
        with col2:
            st.subheader("RAG System")
            result = load_rag_results()
            if result:
                data, filename = result
                st.success(f"Latest: {filename}")
                summary = data.get('summary', {})
                st.metric("Retrieval Relevance", f"{summary.get('avg_retrieval_relevance', 0):.3f}")
                st.metric("Response Quality", f"{summary.get('avg_response_quality', 0):.3f}")
            else:
                st.warning("No results found")
        
        with col3:
            st.subheader("LLM Advice")
            result = load_llm_results()
            if result:
                data, filename = result
                st.success(f"Latest: {filename}")
                summary = data.get('summary', {})
                st.metric("Advice Quality", f"{summary.get('avg_quality', 0):.3f}")
                st.metric("Consistency", f"{summary.get('avg_consistency', 0):.3f}")
            else:
                st.warning("No results found")
    
    elif benchmark_type == "Predictive Models":
        result = load_predictive_results()
        if result:
            df, filename = result
            show_predictive_dashboard(df, filename)
        else:
            st.warning("No predictive model benchmark results found. Run `python tests/benchmark_predictive.py` first.")
    
    elif benchmark_type == "RAG System":
        result = load_rag_results()
        if result:
            data, filename = result
            show_rag_dashboard(data, filename)
        else:
            st.warning("No RAG system benchmark results found. Run `python tests/benchmark_rag.py` first.")
    
    elif benchmark_type == "LLM Advice":
        result = load_llm_results()
        if result:
            data, filename = result
            show_llm_dashboard(data, filename)
        else:
            st.warning("No LLM advice benchmark results found. Run `python tests/benchmark_llm.py` first.")


if __name__ == "__main__":
    main()

