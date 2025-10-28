"""
Visualization utilities for the Streamlit app
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Custom color scheme
COLORS = {
    'female': '#E91E63',
    'male': '#2196F3',
    'non_binary': '#9C27B0',
    'unknown': '#757575',
    'primary': '#1976D2',
    'secondary': '#DC004E',
    'success': '#388E3C',
    'warning': '#F57C00',
    'info': '#0288D1'
}

def create_gender_bar_chart(data, title="Gender Distribution"):
    """Create a bar chart for gender distribution"""
    fig = px.bar(
        x=data.index,
        y=data.values,
        labels={'x': 'Gender', 'y': 'Count'},
        title=title,
        color=data.index,
        color_discrete_map={
            'Female': COLORS['female'],
            'Male': COLORS['male'],
            'Non-Binary': COLORS['non_binary'],
            'Unknown': COLORS['unknown']
        }
    )
    fig.update_layout(showlegend=False, height=400)
    return fig

def create_temporal_line_chart(df, x_col, y_col, title, color=None, color_map=None):
    """Create a line chart for temporal trends"""
    if color:
        fig = px.line(
            df, x=x_col, y=y_col,
            color=color,
            title=title,
            color_discrete_map=color_map or {}
        )
    else:
        fig = px.line(df, x=x_col, y=y_col, title=title)
    
    fig.update_layout(height=500)
    fig.update_xaxes(title=x_col.replace('_', ' ').title())
    fig.update_yaxes(title=y_col.replace('_', ' ').title())
    return fig

def create_distribution_histogram(data, title, x_label, bins=20):
    """Create a histogram for distribution analysis"""
    fig = px.histogram(
        x=data,
        nbins=bins,
        title=title,
        labels={'x': x_label}
    )
    fig.update_layout(height=400, showlegend=False)
    return fig

def create_box_plot(df, x_col, y_col, title, color_col=None):
    """Create a box plot for comparison"""
    if color_col:
        fig = px.box(
            df, x=x_col, y=y_col,
            color=color_col,
            title=title
        )
    else:
        fig = px.box(df, x=x_col, y=y_col, title=title)
    
    fig.update_layout(height=500)
    return fig

def create_scatter_plot(df, x_col, y_col, title, color_col=None, size_col=None):
    """Create a scatter plot"""
    fig = px.scatter(
        df, x=x_col, y=y_col,
        color=color_col,
        size=size_col,
        title=title,
        opacity=0.7
    )
    fig.update_layout(height=500)
    return fig

def create_pie_chart(data, title, names=None, values=None):
    """Create a pie chart"""
    if isinstance(data, pd.Series):
        fig = px.pie(
            values=data.values,
            names=data.index,
            title=title
        )
    else:
        fig = px.pie(
            data, names=names, values=values,
            title=title
        )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    return fig

def create_heatmap(data, title, x_label=None, y_label=None):
    """Create a heatmap"""
    fig = px.imshow(
        data,
        title=title,
        labels={'x': x_label or '', 'y': y_label or ''},
        aspect='auto',
        color_continuous_scale='RdBu_r'
    )
    fig.update_layout(height=500)
    return fig

def create_grouped_bar_chart(df, x_col, y_col, color_col, title):
    """Create a grouped bar chart"""
    fig = px.bar(
        df, x=x_col, y=y_col,
        color=color_col,
        barmode='group',
        title=title
    )
    fig.update_layout(height=500)
    return fig

def create_stacked_bar_chart(df, x_col, y_cols, title):
    """Create a stacked bar chart"""
    fig = go.Figure()
    
    for col in y_cols:
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[col],
            name=col
        ))
    
    fig.update_layout(
        barmode='stack',
        title=title,
        height=500
    )
    return fig

def create_percentage_stacked_bar(df, x_col, value_cols, title):
    """Create a 100% stacked bar chart"""
    # Normalize to percentages
    df_pct = df.copy()
    df_pct[value_cols] = df_pct[value_cols].div(df_pct[value_cols].sum(axis=1), axis=0) * 100
    
    fig = go.Figure()
    
    for col in value_cols:
        fig.add_trace(go.Bar(
            x=df_pct[x_col],
            y=df_pct[col],
            name=col
        ))
    
    fig.update_layout(
        barmode='stack',
        title=title,
        height=500,
        yaxis_title='Percentage'
    )
    return fig

def format_percentage(value):
    """Format a number as a percentage"""
    return f"{value:.1f}%"

def format_count(value):
    """Format a count with commas"""
    return f"{int(value):,}"

def display_metric_card(label, value, delta=None, help_text=None):
    """Display a styled metric card"""
    st.metric(label=label, value=value, delta=delta, help=help_text)

def display_insight_box(title, content, icon="💡"):
    """Display an insight box with styling"""
    st.markdown(f"""
    <div class="insight-box">
        <h4>{icon} {title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def create_correlation_matrix(df, columns, title="Correlation Matrix"):
    """Create a correlation heatmap"""
    corr_matrix = df[columns].corr()
    
    fig = px.imshow(
        corr_matrix,
        title=title,
        labels={'color': 'Correlation'},
        color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1,
        aspect='auto'
    )
    
    fig.update_layout(height=600)
    return fig
