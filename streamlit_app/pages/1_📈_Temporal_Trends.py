"""
Temporal Trends Analysis Page
Explores how gender representation evolved over time (2012-2022)
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    load_data, filter_data_by_year,
    create_temporal_line_chart, create_box_plot,
    create_grouped_bar_chart, display_insight_box,
    format_percentage, COLORS
)

st.set_page_config(page_title="Temporal Trends", page_icon="📈", layout="wide")

# Load data
games, chars, _ = load_data()

# Page header
st.title("📈 Temporal Trends Analysis")
st.markdown("""
Explore how gender representation in video games has evolved from 2012 to 2022.
This analysis examines trends in character representation, protagonist gender, 
and game design choices over time.
""")

# Sidebar filters
st.sidebar.header("Filters")

# Get year range, handling NaN values
year_min = int(games['release_year'].dropna().min()) if games['release_year'].notna().any() else 2012
year_max = int(games['release_year'].dropna().max()) if games['release_year'].notna().any() else 2022

year_range = st.sidebar.slider(
    "Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)
)

# Filter data
games_filtered = filter_data_by_year(games, 'release_year', year_range)

# Merge characters with game year
chars_with_year = chars.merge(
    games[['game_id', 'release_year']], 
    left_on='game',
    right_on='game_id',
    how='left'
)
chars_filtered = filter_data_by_year(chars_with_year, 'release_year', year_range)

st.markdown("---")

# Section 1: Overall Temporal Trends
st.header("1️⃣ Overall Temporal Trends")

col1, col2 = st.columns(2)

with col1:
    # Calculate yearly statistics
    yearly_stats = games_filtered.groupby('release_year').agg({
        'char_pct_Female': 'mean',
        'has_female_protagonist': 'mean',
        'has_gender_parity': 'mean',
        'customizable_main': 'mean'
    }).reset_index()
    
    yearly_stats.columns = ['Year', 'Female %', 'Female Protagonist %', 
                           'Gender Parity %', 'Customizable Protagonist %']
    
    # Convert to percentages (char_pct_Female is already in %, others are decimals)
    yearly_stats['Female Protagonist %'] = yearly_stats['Female Protagonist %'] * 100
    yearly_stats['Gender Parity %'] = yearly_stats['Gender Parity %'] * 100
    yearly_stats['Customizable Protagonist %'] = yearly_stats['Customizable Protagonist %'] * 100
    # Note: 'Female %' is already in percentage format from the CSV
    
    # Line chart for female representation
    fig1 = create_temporal_line_chart(
        yearly_stats, 'Year', 'Female %',
        "Average Female Character Representation Over Time"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Line chart for female protagonists
    fig2 = create_temporal_line_chart(
        yearly_stats, 'Year', 'Female Protagonist %',
        "Games with Female Protagonists Over Time"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Key insights
latest_year = yearly_stats['Year'].max()
earliest_year = yearly_stats['Year'].min()

latest_female_pct = yearly_stats[yearly_stats['Year'] == latest_year]['Female %'].values[0]
earliest_female_pct = yearly_stats[yearly_stats['Year'] == earliest_year]['Female %'].values[0]
change_pct = latest_female_pct - earliest_female_pct

display_insight_box(
    "Key Finding",
    f"Female character representation {'increased' if change_pct > 0 else 'decreased'} "
    f"by {abs(change_pct):.1f} percentage points from {earliest_year} ({earliest_female_pct:.1f}%) "
    f"to {latest_year} ({latest_female_pct:.1f}%)."
)

st.markdown("---")

# Section 2: Character-Level Trends
st.header("2️⃣ Character-Level Temporal Analysis")

# Gender distribution by year
gender_by_year = chars_filtered.groupby(['release_year', 'gender']).size().unstack(fill_value=0)
gender_by_year_pct = gender_by_year.div(gender_by_year.sum(axis=1), axis=0) * 100

# Create line chart
fig3 = create_temporal_line_chart(
    gender_by_year_pct.reset_index().melt(id_vars='release_year'),
    'release_year', 'value',
    "Character Gender Distribution Over Time (%)",
    color='gender',
    color_map={'Female': COLORS['female'], 'Male': COLORS['male'], 
               'Non-Binary': COLORS['non_binary']}
)
st.plotly_chart(fig3, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    # Protagonist trends
    protag_by_year = chars_filtered[chars_filtered['is_protagonist']].groupby(['release_year', 'gender']).size().unstack(fill_value=0)
    protag_by_year_pct = protag_by_year.div(protag_by_year.sum(axis=1), axis=0) * 100
    
    fig4 = create_temporal_line_chart(
        protag_by_year_pct.reset_index().melt(id_vars='release_year'),
        'release_year', 'value',
        "Protagonist Gender Distribution Over Time (%)",
        color='gender',
        color_map={'Female': COLORS['female'], 'Male': COLORS['male']}
    )
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    # Playable character trends
    playable_by_year = chars_filtered[chars_filtered['playable']].groupby(['release_year', 'gender']).size().unstack(fill_value=0)
    playable_by_year_pct = playable_by_year.div(playable_by_year.sum(axis=1), axis=0) * 100
    
    fig5 = create_temporal_line_chart(
        playable_by_year_pct.reset_index().melt(id_vars='release_year'),
        'release_year', 'value',
        "Playable Character Gender Distribution Over Time (%)",
        color='gender',
        color_map={'Female': COLORS['female'], 'Male': COLORS['male']}
    )
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# Section 3: Game Design Trends
st.header("3️⃣ Game Design Trends")

col1, col2 = st.columns(2)

with col1:
    # Gender parity trend
    fig6 = create_temporal_line_chart(
        yearly_stats, 'Year', 'Gender Parity %',
        "Games Achieving Gender Parity Over Time"
    )
    st.plotly_chart(fig6, use_container_width=True)

with col2:
    # Customizable protagonist trend
    fig7 = create_temporal_line_chart(
        yearly_stats, 'Year', 'Customizable Protagonist %',
        "Games with Customizable Protagonists Over Time"
    )
    st.plotly_chart(fig7, use_container_width=True)

# Calculate correlations
if len(yearly_stats) > 2:
    from scipy.stats import pearsonr
    
    corr_parity, p_parity = pearsonr(yearly_stats['Year'], yearly_stats['Gender Parity %'])
    corr_custom, p_custom = pearsonr(yearly_stats['Year'], yearly_stats['Customizable Protagonist %'])
    
    display_insight_box(
        "Trend Analysis",
        f"Gender parity shows a {'positive' if corr_parity > 0 else 'negative'} correlation "
        f"with time (r={corr_parity:.2f}, {'significant' if p_parity < 0.05 else 'not significant'}). "
        f"Customizable protagonists show a {'positive' if corr_custom > 0 else 'negative'} correlation "
        f"(r={corr_custom:.2f}, {'significant' if p_custom < 0.05 else 'not significant'})."
    )

st.markdown("---")

# Section 4: Statistical Summary
st.header("4️⃣ Statistical Summary")

# Display summary table
st.subheader("Yearly Statistics")
st.dataframe(
    yearly_stats.style.format({
        'Female %': '{:.1f}%',
        'Female Protagonist %': '{:.1f}%',
        'Gender Parity %': '{:.1f}%',
        'Customizable Protagonist %': '{:.1f}%'
    }),
    use_container_width=True
)

# Download button
csv = yearly_stats.to_csv(index=False)
st.download_button(
    label="📥 Download Temporal Data",
    data=csv,
    file_name="temporal_trends.csv",
    mime="text/csv"
)
