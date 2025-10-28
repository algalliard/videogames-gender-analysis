"""
Character Analysis Page
Explores character-level representation patterns (Section 3: H2a-H2f)
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from scipy import stats

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    load_data, filter_data_by_year, filter_data_by_gender,
    create_gender_bar_chart, create_box_plot, create_grouped_bar_chart,
    create_pie_chart, create_heatmap, create_percentage_stacked_bar,
    display_insight_box, format_percentage, COLORS
)

st.set_page_config(page_title="Character Analysis", page_icon="👥", layout="wide")

# Load data
games, chars, sex = load_data()

# Merge character data with game info (sexualization already in chars)
chars_full = chars.merge(
    games[['game_id', 'title', 'release_year']], 
    left_on='game',
    right_on='game_id',
    how='left'
)

# Page header
st.title("👥 Character-Level Representation Analysis")
st.markdown("""
Explore how different genders are distributed across character roles, narrative importance, 
and representation patterns. This analysis tests 6 key hypotheses about character-level representation.
""")

# Sidebar filters
st.sidebar.header("Filters")

# Get year range, handling NaN values
year_min = int(chars_full['release_year'].dropna().min()) if chars_full['release_year'].notna().any() else 2012
year_max = int(chars_full['release_year'].dropna().max()) if chars_full['release_year'].notna().any() else 2022

year_range = st.sidebar.slider(
    "Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)
)

gender_options = st.sidebar.multiselect(
    "Gender",
    options=['Male', 'Female', 'Non-binary', 'Custom'],
    default=['Male', 'Female']
)

# Filter data
# Note: We keep characters even if release_year is missing to avoid data loss
chars_filtered = chars_full.copy()

# Apply year filter only to characters that have a valid release year
if year_range:
    chars_filtered = chars_filtered[
        (chars_filtered['release_year'].isna()) |  # Keep NaN years
        ((chars_filtered['release_year'] >= year_range[0]) & 
         (chars_filtered['release_year'] <= year_range[1]))
    ]

if gender_options:
    chars_filtered = chars_filtered[chars_filtered['gender'].isin(gender_options)]

# Convert age to numeric for analysis (handle string values like "Teenager")
if 'age' in chars_filtered.columns:
    chars_filtered['age_numeric'] = pd.to_numeric(chars_filtered['age'], errors='coerce')

st.markdown("---")

# Check if we have data
if len(chars_filtered) == 0:
    st.warning("⚠️ No characters found with the selected filters. Please adjust your filter settings.")
    st.stop()

# Overview metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_chars = len(chars_filtered)
    st.metric("Total Characters", f"{total_chars:,}")

with col2:
    female_pct = (chars_filtered['gender'] == 'Female').sum() / len(chars_filtered) * 100
    st.metric("Female %", f"{female_pct:.1f}%")

with col3:
    protagonist_count = chars_filtered['is_protagonist'].sum()
    st.metric("Protagonists", f"{protagonist_count}")

with col4:
    sexualized_pct = chars_filtered['is_sexualized'].sum() / len(chars_filtered) * 100
    st.metric("Sexualized %", f"{sexualized_pct:.1f}%")

st.markdown("---")

# Create tabs for different analyses
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "H2a: Protagonist Roles",
    "H2b: Playability", 
    "H2c: Plot Relevance",
    "H2d: Age Patterns",
    "H2e: Romantic Interest",
    "H2f: Intersectional"
])

# TAB 1: H2a - Protagonist Roles
with tab1:
    st.header("H2a: Male Over-representation in Protagonist Roles")
    st.markdown("**Hypothesis**: Male characters are over-represented in protagonist roles")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gender distribution by protagonist status
        protag_gender = chars_filtered.groupby(['is_protagonist', 'gender']).size().unstack(fill_value=0)
        protag_gender_pct = protag_gender.div(protag_gender.sum(axis=1), axis=0) * 100
        
        # Create stacked bar chart
        import plotly.graph_objects as go
        
        fig = go.Figure()
        for gender in protag_gender_pct.columns:
            color = COLORS.get(gender.lower(), COLORS['primary'])
            fig.add_trace(go.Bar(
                name=gender,
                x=['Non-Protagonist', 'Protagonist'],
                y=protag_gender_pct.loc[[False, True], gender],
                marker_color=color
            ))
        
        fig.update_layout(
            title="Gender Distribution by Protagonist Status",
            barmode='stack',
            yaxis_title="Percentage",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Key Statistics")
        
        # Calculate protagonist rates by gender
        for gender in gender_options:
            gender_chars = chars_filtered[chars_filtered['gender'] == gender]
            protag_rate = gender_chars['is_protagonist'].mean() * 100
            st.metric(f"{gender} Protagonist Rate", f"{protag_rate:.1f}%")
        
        # Statistical test
        if len(gender_options) == 2 and len(chars_filtered) > 0:
            contingency = pd.crosstab(
                chars_filtered['gender'], 
                chars_filtered['is_protagonist']
            )
            
            # Only run test if we have enough data
            if contingency.size > 0 and contingency.min().min() >= 5:
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
                
                st.markdown("---")
                st.markdown("### 🎯 Statistical Test")
                st.write(f"Chi-square: {chi2:.2f}")
                st.write(f"p-value: {p_value:.4f}")
                
                if p_value < 0.05:
                    st.success("✅ Significant difference detected")
                else:
                    st.info("No significant difference")
            else:
                st.warning("⚠️ Insufficient data for statistical test")
    
    # Detailed breakdown
    st.markdown("### Detailed Character Counts")
    protag_table = pd.crosstab(
        chars_filtered['gender'],
        chars_filtered['is_protagonist'],
        margins=True
    )
    protag_table.columns = ['Non-Protagonist', 'Protagonist', 'Total']
    st.dataframe(protag_table, use_container_width=True)

# TAB 2: H2b - Playability
with tab2:
    st.header("H2b: Playable Character Gender Diversity")
    st.markdown("**Hypothesis**: Playable characters are more gender-diverse than non-playable characters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gender distribution among playable characters
        playable_chars = chars_filtered[chars_filtered['playable'] == True]
        playable_gender_dist = playable_chars['gender'].value_counts()
        
        fig1 = create_pie_chart(
            playable_gender_dist,
            "Playable Characters - Gender Distribution"
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        st.metric(
            "Female Playable Characters",
            f"{(playable_chars['gender'] == 'Female').sum()}",
            f"{(playable_chars['gender'] == 'Female').sum() / len(playable_chars) * 100:.1f}%"
        )
    
    with col2:
        # Gender distribution among non-playable characters
        non_playable_chars = chars_filtered[chars_filtered['playable'] == False]
        non_playable_gender_dist = non_playable_chars['gender'].value_counts()
        
        fig2 = create_pie_chart(
            non_playable_gender_dist,
            "Non-Playable Characters - Gender Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        st.metric(
            "Female Non-Playable Characters",
            f"{(non_playable_chars['gender'] == 'Female').sum()}",
            f"{(non_playable_chars['gender'] == 'Female').sum() / len(non_playable_chars) * 100:.1f}%"
        )
    
    # Comparison chart
    st.markdown("### Playable vs Non-Playable Comparison")
    
    playable_comparison = chars_filtered.groupby(['playable', 'gender']).size().unstack(fill_value=0)
    playable_comparison_pct = playable_comparison.div(playable_comparison.sum(axis=1), axis=0) * 100
    
    fig3 = create_grouped_bar_chart(
        playable_comparison_pct.reset_index().melt(id_vars='playable', var_name='Gender', value_name='Percentage'),
        'Gender',
        'Percentage',
        'playable',
        "Gender Distribution: Playable vs Non-Playable Characters"
    )
    st.plotly_chart(fig3, use_container_width=True)

# TAB 3: H2c - Plot Relevance
with tab3:
    st.header("H2c: Gender and Plot Relevance")
    st.markdown("**Hypothesis**: Male characters are more likely to be marked as 'relevant' to the plot")
    
    # Relevance categories
    if 'relevance' in chars_filtered.columns:
        relevance_gender = pd.crosstab(
            chars_filtered['relevance'],
            chars_filtered['gender'],
            normalize='index'
        ) * 100
        
        # Heatmap
        fig = create_heatmap(
            relevance_gender,
            "Plot Relevance by Gender (%)",
            x_label="Gender",
            y_label="Relevance Code"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary table
        st.markdown("### Relevance Code Distribution")
        relevance_counts = pd.crosstab(
            chars_filtered['relevance'],
            chars_filtered['gender'],
            margins=True
        )
        st.dataframe(relevance_counts, use_container_width=True)
        
        # Main character analysis
        st.markdown("### Main Characters (PA/MC/DA)")
        main_char_codes = ['PA', 'MC', 'DA']
        chars_filtered['is_main'] = chars_filtered['relevance'].isin(main_char_codes)
        
        main_char_rate = chars_filtered.groupby('gender')['is_main'].mean() * 100
        
        fig2 = create_gender_bar_chart(
            main_char_rate,
            "Main Character Rate by Gender"
        )
        st.plotly_chart(fig2, use_container_width=True)

# TAB 4: H2d - Age Patterns
with tab4:
    st.header("H2d: Age Distribution by Gender")
    st.markdown("**Hypothesis**: Female characters are portrayed as younger on average than male characters")
    
    if 'age_range' in chars_filtered.columns:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Box plot of age by gender - only if we have numeric age data
            if 'age_numeric' in chars_filtered.columns:
                age_data = chars_filtered[chars_filtered['age_numeric'].notna()]
                
                if len(age_data) > 0:
                    fig = create_box_plot(
                        age_data,
                        'gender',
                        'age_numeric',
                        "Age Distribution by Gender",
                        color_col='gender'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No numeric age data available for selected filters")
            else:
                st.info("Age data not available in numeric format")
        
        with col2:
            st.markdown("### 📊 Age Statistics")
            if 'age_numeric' in chars_filtered.columns:
                for gender in gender_options:
                    gender_ages = chars_filtered[chars_filtered['gender'] == gender]['age_numeric']
                    gender_ages = gender_ages.dropna()
                    
                    if len(gender_ages) > 0:
                        mean_age = gender_ages.mean()
                        median_age = gender_ages.median()
                        st.write(f"**{gender}**")
                        st.write(f"Mean: {mean_age:.1f} years")
                        st.write(f"Median: {median_age:.1f} years")
                        st.write(f"Count: {len(gender_ages)}")
                        st.write("---")
                    else:
                        st.write(f"**{gender}**: No numeric age data")
            else:
                st.info("Numeric age data not available")
        
        # Age range distribution
        st.markdown("### Age Range Distribution by Gender")
        age_range_dist = pd.crosstab(
            chars_filtered['age_range'],
            chars_filtered['gender'],
            normalize='columns'
        ) * 100
        
        fig2 = create_grouped_bar_chart(
            age_range_dist.reset_index().melt(id_vars='age_range', var_name='Gender', value_name='Percentage'),
            'age_range',
            'Percentage',
            'Gender',
            "Age Range Distribution by Gender"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Age range data not available in dataset")

# TAB 5: H2e - Romantic Interest
with tab5:
    st.header("H2e: Romantic Interest Patterns")
    st.markdown("**Hypothesis**: Female characters are more likely to be defined by romantic interest relationships")
    
    if 'romantic_interest' in chars_filtered.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Romantic interest rate by gender
            romantic_rate = chars_filtered.groupby('gender')['romantic_interest'].mean() * 100
            
            fig = create_gender_bar_chart(
                romantic_rate,
                "Romantic Interest Rate by Gender"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Statistics")
            for gender in gender_options:
                gender_chars = chars_filtered[chars_filtered['gender'] == gender]
                romantic_pct = gender_chars['romantic_interest'].mean() * 100
                romantic_count = gender_chars['romantic_interest'].sum()
                
                st.metric(
                    f"{gender} Romantic Interest",
                    f"{romantic_count}",
                    f"{romantic_pct:.1f}%"
                )
        
        # Cross-tabulation
        st.markdown("### Romantic Interest by Gender and Role")
        romantic_role = pd.crosstab(
            [chars_filtered['gender'], chars_filtered['is_protagonist']],
            chars_filtered['romantic_interest']
        )
        romantic_role.index.names = ['Gender', 'Is Protagonist']
        st.dataframe(romantic_role, use_container_width=True)
    else:
        st.warning("Romantic interest data not available in dataset")

# TAB 6: H2f - Intersectional Analysis
with tab6:
    st.header("H2f: Intersectional Character Analysis")
    st.markdown("**Hypothesis**: Multiple marginalized identities compound underrepresentation")
    
    st.markdown("### Character Privilege Scores")
    st.info("""
    This analysis examines how multiple factors (gender, role, age) intersect to create 
    patterns of privilege or marginalization in character representation.
    """)
    
    # Create privilege indicators
    chars_filtered['privilege_protagonist'] = chars_filtered['is_protagonist'].astype(int)
    chars_filtered['privilege_playable'] = chars_filtered['playable'].astype(int)
    chars_filtered['privilege_male'] = (chars_filtered['gender'] == 'Male').astype(int)
    
    privilege_cols = ['privilege_protagonist', 'privilege_playable', 'privilege_male']
    chars_filtered['privilege_score'] = chars_filtered[privilege_cols].sum(axis=1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Privilege score distribution
        privilege_dist = chars_filtered['privilege_score'].value_counts().sort_index()
        
        import plotly.express as px
        fig = px.bar(
            x=privilege_dist.index,
            y=privilege_dist.values,
            labels={'x': 'Privilege Score (0=Low, 3=High)', 'y': 'Number of Characters'},
            title="Character Privilege Score Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Privilege by gender
        privilege_by_gender = chars_filtered.groupby('gender')['privilege_score'].mean()
        
        fig2 = create_gender_bar_chart(
            privilege_by_gender,
            "Average Privilege Score by Gender"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Sexualization by intersectional identity
    st.markdown("### Sexualization by Intersectional Identity")
    
    if 'is_sexualized' in chars_filtered.columns:
        # Gender × Role × Sexualization
        intersectional_sex = chars_filtered.groupby(['gender', 'is_protagonist'])['is_sexualized'].mean() * 100
        intersectional_sex_df = intersectional_sex.reset_index()
        intersectional_sex_df.columns = ['Gender', 'Is Protagonist', 'Sexualization Rate (%)']
        
        fig3 = create_grouped_bar_chart(
            intersectional_sex_df,
            'Gender',
            'Sexualization Rate (%)',
            'Is Protagonist',
            "Sexualization Rate by Gender and Protagonist Status"
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Summary insights
        display_insight_box(
            "Key Findings",
            f"Female protagonists: {intersectional_sex.get(('Female', True), 0):.1f}% sexualized. "
            f"Female non-protagonists: {intersectional_sex.get(('Female', False), 0):.1f}% sexualized. "
            f"Male protagonists: {intersectional_sex.get(('Male', True), 0):.1f}% sexualized."
        )

st.markdown("---")

# Summary section
st.header("📝 Character Analysis Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ Confirmed Patterns")
    st.markdown("""
    - Male over-representation in protagonist roles
    - Higher sexualization rates for female characters
    - Age differences between male and female characters
    - Romantic interest disparity by gender
    """)

with col2:
    st.markdown("### 📊 Key Metrics")
    overall_female_pct = (chars_filtered['gender'] == 'Female').sum() / len(chars_filtered) * 100
    female_protag_pct = chars_filtered[chars_filtered['is_protagonist']]['gender'].value_counts(normalize=True).get('Female', 0) * 100
    
    st.write(f"- Overall female representation: {overall_female_pct:.1f}%")
    st.write(f"- Female protagonist representation: {female_protag_pct:.1f}%")
    st.write(f"- Total characters analyzed: {len(chars_filtered):,}")
    st.write(f"- Games in sample: {chars_filtered['game'].nunique()}")

# Download button
st.markdown("### 📥 Export Data")
csv = chars_filtered.to_csv(index=False)
st.download_button(
    label="Download Filtered Character Data",
    data=csv,
    file_name=f"character_analysis_{year_range[0]}-{year_range[1]}.csv",
    mime="text/csv"
)
