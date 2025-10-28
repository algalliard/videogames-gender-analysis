"""
Gender Representation in Video Games (2012-2022)
A comprehensive analysis dashboard exploring gender representation patterns
in video game characters, protagonists, and development teams.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent / "utils"))

from data_loader import load_data, get_data_summary

# Page configuration
st.set_page_config(
    page_title="Gender in Video Games Analysis",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2ca02c;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎮 Gender Representation in Video Games</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analysis of Character Gender Distribution (2012-2022)</div>', unsafe_allow_html=True)

# Load data
@st.cache_data
def get_data():
    """Load and cache the cleaned datasets"""
    return load_data()

try:
    games, chars, sex = get_data()
    
    # Sidebar - Dataset overview
    with st.sidebar:
        st.header("📊 Dataset Overview")
        summary = get_data_summary(games, chars)
        
        st.metric("Total Games", summary['total_games'])
        st.metric("Total Characters", summary['total_characters'])
        st.metric("Time Span", f"{summary['year_range'][0]:.0f} - {summary['year_range'][1]:.0f}")
        
        st.divider()
        
        st.header("🔍 Filters")
        
        # Year range filter
        year_range = st.slider(
            "Select Year Range",
            int(summary['year_range'][0]),
            int(summary['year_range'][1]),
            (int(summary['year_range'][0]), int(summary['year_range'][1]))
        )
        
        # Gender filter
        available_genders = chars['gender'].dropna().unique().tolist()
        selected_genders = st.multiselect(
            "Filter by Gender",
            available_genders,
            default=available_genders
        )
        
        # Platform filter
        if 'platform' in games.columns:
            platforms = ['All'] + sorted(games['platform'].dropna().unique().tolist())
            selected_platform = st.selectbox("Filter by Platform", platforms)
        else:
            selected_platform = 'All'
        
        st.divider()
        st.markdown("### 📖 About")
        st.info("""
        This dashboard analyzes gender representation in video games released between 2012-2022.
        
        **Data includes:**
        - Character demographics
        - Protagonist gender
        - Team composition
        - Review scores
        - Sexualization metrics
        """)
    
    # Main content
    st.markdown("---")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        female_pct = (chars['gender'] == 'Female').sum() / len(chars) * 100
        st.metric(
            "Female Characters",
            f"{female_pct:.1f}%",
            help="Percentage of female characters across all games"
        )
    
    with col2:
        if 'has_female_protagonist' in games.columns:
            female_protag_pct = games['has_female_protagonist'].sum() / len(games) * 100
            st.metric(
                "Games with Female Protagonist",
                f"{female_protag_pct:.1f}%",
                help="Percentage of games featuring a female protagonist"
            )
        else:
            st.metric("Games with Female Protagonist", "N/A")
    
    with col3:
        if 'has_gender_parity' in games.columns:
            parity_pct = games['has_gender_parity'].sum() / len(games) * 100
            st.metric(
                "Games with Gender Parity",
                f"{parity_pct:.1f}%",
                help="Games with 40-60% female characters"
            )
        else:
            st.metric("Games with Gender Parity", "N/A")
    
    with col4:
        if 'has_female_team' in games.columns:
            female_team_pct = games['has_female_team'].sum() / len(games) * 100
            st.metric(
                "Games with Women on Team",
                f"{female_team_pct:.1f}%",
                help="Percentage of games with at least one woman on the development team"
            )
        else:
            st.metric("Games with Women on Team", "N/A")
    
    st.markdown("---")
    
    # Introduction
    st.header("📋 Welcome to the Analysis Dashboard")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        This interactive dashboard explores gender representation patterns in video games from 2012 to 2022.
        Our analysis examines multiple dimensions:
        
        **🎯 Key Questions We Answer:**
        - How has gender representation evolved over time?
        - What is the relationship between protagonist gender and overall representation?
        - Do development team demographics influence character representation?
        - How does sexualization vary by character gender and role?
        - Which genres and platforms show more balanced representation?
        
        **📊 Navigation:**
        Use the sidebar to explore different aspects of the analysis:
        - **Overview**: Summary statistics and key insights
        - **Temporal Trends**: How representation changed from 2012-2022
        - **Character Analysis**: Deep dive into character demographics
        - **Game Patterns**: Game-level representation analysis
        - **Team Impact**: Development team composition effects
        - **Intersectional Analysis**: Complex patterns across multiple dimensions
        """)
    
    with col2:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("### 💡 Key Findings")
        st.markdown(f"""
        - **{female_pct:.1f}%** of all characters are female
        - Female characters are **underrepresented** compared to population
        - **Protagonist gender** strongly predicts overall representation
        - Games with **women on dev teams** show improved representation
        - **Customizable** protagonists correlate with better gender balance
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Stats
    st.header("📈 Quick Statistics")
    
    tab1, tab2, tab3 = st.tabs(["Character Distribution", "Game Statistics", "Temporal Overview"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Gender Distribution")
            gender_counts = chars['gender'].value_counts()
            st.bar_chart(gender_counts)
        
        with col2:
            st.subheader("Playable Characters by Gender")
            if 'playable' in chars.columns:
                playable_gender = chars[chars['playable'] == True]['gender'].value_counts()
                st.bar_chart(playable_gender)
            else:
                st.info("Playable character data not available")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Games by Genre")
            if 'genre' in games.columns:
                genre_counts = games['genre'].value_counts().head(10)
                st.bar_chart(genre_counts)
            else:
                st.info("Genre data not available")
        
        with col2:
            st.subheader("Games by Platform")
            if 'platform' in games.columns:
                platform_counts = games['platform'].value_counts().head(10)
                st.bar_chart(platform_counts)
            else:
                st.info("Platform data not available")
    
    with tab3:
        st.subheader("Games Released Per Year")
        if 'release_year' in games.columns:
            yearly_counts = games['release_year'].value_counts().sort_index()
            st.line_chart(yearly_counts)
        else:
            st.info("Release year data not available")
    
    st.markdown("---")
    
    # Call to Action
    st.success("👈 **Use the sidebar navigation** to explore detailed analyses across different dimensions!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p><strong>Gender Representation in Video Games Analysis Dashboard</strong></p>
        <p>Data spans 2012-2022 | Analyzing {} games and {} characters</p>
    </div>
    """.format(len(games), len(chars)), unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure the preprocessing notebook has been run and data files exist in the 'processed' folder.")
    st.code(str(e))
