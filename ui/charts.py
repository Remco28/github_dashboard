import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd


def render_language_pie(lang_map: Dict[str, int]) -> None:
    """Render a pie chart showing repository distribution by language."""
    if not lang_map:
        st.info("📊 No language data available for current filters.")
        return
    
    # Create DataFrame for plotly
    df = pd.DataFrame(list(lang_map.items()), columns=['Language', 'Count'])
    
    # Create pie chart
    fig = px.pie(
        df, 
        values='Count', 
        names='Language',
        title="Repository Distribution by Language",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
    )
    
    st.plotly_chart(fig, width='stretch')


def render_commits_bar(data: List[Tuple[str, int]]) -> None:
    """Render a bar chart showing commits per repository."""
    if not data or all(count == 0 for _, count in data):
        st.info("📊 No commit data available for the selected time window and repositories.")
        return
    
    # Filter out repositories with 0 commits for cleaner visualization
    filtered_data = [(repo, count) for repo, count in data if count > 0]
    
    if not filtered_data:
        st.info("📊 No commits found in the selected time window.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(filtered_data, columns=['Repository', 'Commits'])
    
    # Create bar chart
    fig = px.bar(
        df,
        x='Commits',
        y='Repository',
        orientation='h',
        title="Commits per Repository",
        color='Commits',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=max(300, len(filtered_data) * 40),
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    
    fig.update_traces(texttemplate='%{x}', textposition='outside')
    
    st.plotly_chart(fig, width='stretch')


def render_trend_line(points: List[Tuple[str, int]]) -> None:
    """Render a line chart showing commits over time."""
    if not points:
        st.info("📊 No commit trend data available for the selected time window.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(points, columns=['Date', 'Commits'])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Create line chart
    fig = px.line(
        df,
        x='Date',
        y='Commits',
        title="Commits Over Time",
        markers=True,
        line_shape='spline'
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Number of Commits",
        hovermode='x unified'
    )
    
    fig.update_traces(
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8, color='#1f77b4')
    )
    
    st.plotly_chart(fig, width='stretch')


def render_heatmap(day_counts: Dict[str, int]) -> None:
    """Render a calendar-like heatmap showing daily commit activity."""
    if not day_counts:
        st.info("📊 No daily commit data available for heatmap.")
        return
    
    # Convert to DataFrame and prepare for heatmap
    dates = []
    counts = []
    
    for date_str, count in day_counts.items():
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            dates.append(date)
            counts.append(count)
        except ValueError:
            continue
    
    if not dates:
        st.info("📊 No valid dates found for heatmap.")
        return
    
    # Create DataFrame
    df = pd.DataFrame({'Date': dates, 'Commits': counts})
    df = df.sort_values('Date')
    
    # Add day of week and week of year for heatmap structure
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['Week'] = df['Date'].dt.isocalendar().week
    df['Year'] = df['Date'].dt.year
    
    # Create a pivot table for the heatmap
    if len(df) > 1:
        # For longer periods, show weekly pattern
        pivot_df = df.groupby(['DayOfWeek'])['Commits'].mean().reset_index()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_df['DayOfWeek'] = pd.Categorical(pivot_df['DayOfWeek'], categories=day_order, ordered=True)
        pivot_df = pivot_df.sort_values('DayOfWeek')
        
        fig = px.bar(
            pivot_df,
            x='DayOfWeek',
            y='Commits',
            title="Average Daily Commit Activity",
            color='Commits',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Day of Week",
            yaxis_title="Average Commits"
        )
    else:
        # For shorter periods, show daily activity
        fig = px.scatter(
            df,
            x='Date',
            y=[1] * len(df),  # Fixed y position
            size='Commits',
            title="Daily Commit Activity",
            color='Commits',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            height=300,
            yaxis=dict(visible=False),
            xaxis_title="Date",
            showlegend=False
        )
    
    st.plotly_chart(fig, width='stretch')
