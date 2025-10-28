"""
Intersectional Analysis Page
Multi-dimensional analysis of gender representation patterns (Section 7: H7a-H7d)
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    load_data, filter_data_by_year,
    create_gender_bar_chart, create_box_plot, create_grouped_bar_chart,
    create_pie_chart, create_scatter_plot, create_distribution_histogram,
    display_insight_box, format_percentage, COLORS
)

st.set_page_config(page_title="Intersectional Analysis", page_icon="🔍", layout="wide")

# Load data
games, chars, sex = load_data()

# Page header
st.title("🔍 Intersectional Analysis")
st.markdown("""
Explore complex, multi-dimensional patterns in gender representation. This analysis examines
how gender intersects with other character attributes like age, role, and sexualization to
reveal nuanced representation patterns.
""")

# Sidebar filters
st.sidebar.header("Filters")

# Get year range
year_min = int(games['release_year'].dropna().min()) if games['release_year'].notna().any() else 2012
year_max = int(games['release_year'].dropna().max()) if games['release_year'].notna().any() else 2022

year_range = st.sidebar.slider(
    "Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)
)

# Merge characters with game data for year filtering
chars_with_year = chars.merge(
    games[['game_id', 'release_year']], 
    left_on='game',
    right_on='game_id',
    how='left'
)

# Filter characters by year
chars_filtered = chars_with_year[
    (chars_with_year['release_year'] >= year_range[0]) & 
    (chars_with_year['release_year'] <= year_range[1])
].copy()

# Filter games
games_filtered = filter_data_by_year(games, 'release_year', year_range)

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
    if 'gender' in chars_filtered.columns:
        female_chars = (chars_filtered['gender'] == 'Female').sum()
        st.metric("Female Characters", f"{female_chars} ({female_chars/total_chars*100:.1f}%)")

with col3:
    if 'is_sexualized' in chars_filtered.columns:
        sexualized = chars_filtered['is_sexualized'].sum()
        st.metric("Sexualized Characters", f"{sexualized} ({sexualized/total_chars*100:.1f}%)")

with col4:
    if 'is_protagonist' in chars_filtered.columns:
        protagonists = chars_filtered['is_protagonist'].sum()
        st.metric("Protagonists", f"{protagonists} ({protagonists/total_chars*100:.1f}%)")

st.markdown("---")

# Create tabs for different analyses
tab1, tab2, tab3, tab4 = st.tabs([
    "H7a: Gender × Age × Sexualization",
    "H7b: Gender × Role × Relevance",
    "H7c: Multi-Dimensional Patterns",
    "Correlation Matrix"
])

# TAB 1: H7a - Gender × Age × Sexualization
with tab1:
    st.header("H7a: Gender, Age, and Sexualization Intersections")
    st.markdown("**Hypothesis**: Young female characters are disproportionately sexualized")
    
    if all(col in chars_filtered.columns for col in ['gender', 'age', 'is_sexualized']):
        # Create age categories
        def categorize_age(age):
            if pd.isna(age):
                return 'Unknown'
            try:
                age_num = float(age)
                if age_num < 18:
                    return 'Child/Teen (<18)'
                elif age_num < 30:
                    return 'Young Adult (18-29)'
                elif age_num < 50:
                    return 'Adult (30-49)'
                else:
                    return 'Mature (50+)'
            except (ValueError, TypeError):
                return 'Unknown'
        
        chars_filtered['age_category'] = chars_filtered['age'].apply(categorize_age)
        
        # Three-way analysis: Gender × Age × Sexualization
        st.markdown("### Sexualization Rates by Gender and Age")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Calculate sexualization rates
            sex_by_gender_age = chars_filtered.groupby(['gender', 'age_category'])['is_sexualized'].agg(['mean', 'count']).reset_index()
            sex_by_gender_age['sexualization_rate'] = sex_by_gender_age['mean'] * 100
            
            # Pivot for grouped bar chart
            sex_pivot = sex_by_gender_age.pivot(index='age_category', columns='gender', values='sexualization_rate').fillna(0)
            
            fig = go.Figure()
            
            if 'Female' in sex_pivot.columns:
                fig.add_trace(go.Bar(
                    name='Female',
                    x=sex_pivot.index,
                    y=sex_pivot['Female'],
                    marker_color=COLORS['female']
                ))
            
            if 'Male' in sex_pivot.columns:
                fig.add_trace(go.Bar(
                    name='Male',
                    x=sex_pivot.index,
                    y=sex_pivot['Male'],
                    marker_color=COLORS['male']
                ))
            
            fig.update_layout(
                title="Sexualization Rate by Gender and Age Category",
                xaxis_title="Age Category",
                yaxis_title="Sexualization Rate (%)",
                barmode='group',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Key Statistics")
            
            # Focus on young female characters
            young_female = chars_filtered[
                (chars_filtered['gender'] == 'Female') & 
                (chars_filtered['age_category'] == 'Young Adult (18-29)')
            ]
            
            young_male = chars_filtered[
                (chars_filtered['gender'] == 'Male') & 
                (chars_filtered['age_category'] == 'Young Adult (18-29)')
            ]
            
            if len(young_female) > 0:
                young_f_sex_rate = young_female['is_sexualized'].mean() * 100
                st.metric("Young Female Sexualization", f"{young_f_sex_rate:.1f}%")
            
            if len(young_male) > 0:
                young_m_sex_rate = young_male['is_sexualized'].mean() * 100
                st.metric("Young Male Sexualization", f"{young_m_sex_rate:.1f}%")
            
            if len(young_female) > 0 and len(young_male) > 0:
                st.markdown("---")
                diff = young_f_sex_rate - young_m_sex_rate
                st.write(f"**Gender Gap**: {diff:.1f} percentage points")
        
        # Detailed breakdown table
        st.markdown("### Detailed Breakdown: Sexualization by Gender and Age")
        
        breakdown = chars_filtered.groupby(['gender', 'age_category']).agg({
            'is_sexualized': ['sum', 'count', 'mean']
        }).reset_index()
        
        breakdown.columns = ['Gender', 'Age Category', 'Sexualized Count', 'Total', 'Rate']
        breakdown['Rate (%)'] = breakdown['Rate'] * 100
        breakdown = breakdown[['Gender', 'Age Category', 'Sexualized Count', 'Total', 'Rate (%)']]
        breakdown = breakdown.sort_values(['Gender', 'Rate (%)'], ascending=[True, False])
        
        st.dataframe(
            breakdown.style.format({'Rate (%)': '{:.1f}'}),
            use_container_width=True,
            hide_index=True
        )
        
        # Statistical insight
        if len(young_female) > 0 and len(young_male) > 0:
            # Chi-square test for young adults
            contingency = pd.crosstab(
                chars_filtered[chars_filtered['age_category'] == 'Young Adult (18-29)']['gender'],
                chars_filtered[chars_filtered['age_category'] == 'Young Adult (18-29)']['is_sexualized']
            )
            
            if contingency.size > 0:
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
                
                display_insight_box(
                    "Statistical Test: Young Adult Sexualization",
                    f"Chi-square = {chi2:.2f}, p-value = {p_value:.4f}. "
                    f"{'Significant gender difference' if p_value < 0.05 else 'No significant difference'} "
                    f"in sexualization rates among young adult characters."
                )
    else:
        st.warning("Required data (gender, age, sexualization) not available")

# TAB 2: H7b - Gender × Role × Relevance
with tab2:
    st.header("H7b: Gender, Role, and Plot Relevance Intersections")
    st.markdown("**Hypothesis**: Female characters occupy different role-relevance combinations than males")
    
    if all(col in chars_filtered.columns for col in ['gender', 'is_protagonist', 'plot_relevance']):
        col1, col2 = st.columns(2)
        
        with col1:
            # Role categories
            def categorize_role(row):
                if row.get('is_protagonist', False):
                    return 'Protagonist'
                elif row.get('is_playable', False):
                    return 'Playable'
                else:
                    return 'NPC'
            
            chars_filtered['role_type'] = chars_filtered.apply(categorize_role, axis=1)
            
            # Gender × Role distribution
            st.markdown("### Role Distribution by Gender")
            
            role_by_gender = pd.crosstab(
                chars_filtered['gender'],
                chars_filtered['role_type'],
                normalize='index'
            ) * 100
            
            fig = go.Figure()
            
            for role in role_by_gender.columns:
                fig.add_trace(go.Bar(
                    name=role,
                    x=role_by_gender.index,
                    y=role_by_gender[role]
                ))
            
            fig.update_layout(
                title="Character Roles by Gender (%)",
                barmode='stack',
                yaxis_title="Percentage",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gender × Plot Relevance
            st.markdown("### Plot Relevance by Gender")
            
            relevance_by_gender = pd.crosstab(
                chars_filtered['gender'],
                chars_filtered['plot_relevance'],
                normalize='index'
            ) * 100
            
            fig2 = go.Figure()
            
            for relevance in relevance_by_gender.columns:
                fig2.add_trace(go.Bar(
                    name=relevance,
                    x=relevance_by_gender.index,
                    y=relevance_by_gender[relevance]
                ))
            
            fig2.update_layout(
                title="Plot Relevance by Gender (%)",
                barmode='stack',
                yaxis_title="Percentage",
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Three-way analysis: Gender × Role × Relevance
        st.markdown("### Gender × Role × Plot Relevance Matrix")
        
        # Create comprehensive breakdown
        role_relevance = chars_filtered.groupby(['gender', 'role_type', 'plot_relevance']).size().reset_index(name='count')
        role_relevance_pivot = role_relevance.pivot_table(
            index=['gender', 'role_type'],
            columns='plot_relevance',
            values='count',
            fill_value=0
        )
        
        st.dataframe(role_relevance_pivot, use_container_width=True)
        
        # Heatmap visualization
        st.markdown("### Heatmap: Female Character Distribution Across Role-Relevance Combinations")
        
        female_chars_role = chars_filtered[chars_filtered['gender'] == 'Female']
        female_matrix = pd.crosstab(
            female_chars_role['role_type'],
            female_chars_role['plot_relevance'],
            normalize='all'
        ) * 100
        
        fig3 = px.imshow(
            female_matrix.values,
            labels=dict(x="Plot Relevance", y="Role Type", color="% of Female Chars"),
            x=female_matrix.columns,
            y=female_matrix.index,
            color_continuous_scale='Purples',
            aspect="auto"
        )
        fig3.update_layout(title="Female Character Concentration (%)", height=400)
        st.plotly_chart(fig3, use_container_width=True)
        
        # Key insight
        most_common = role_relevance[role_relevance['gender'] == 'Female'].nlargest(3, 'count')
        
        display_insight_box(
            "Most Common Female Character Types",
            f"Top 3 combinations: " + ", ".join([
                f"{row['role_type']} + {row['plot_relevance']} ({row['count']} chars)" 
                for _, row in most_common.iterrows()
            ])
        )
    else:
        st.warning("Required data (gender, role, plot relevance) not available")

# TAB 3: H7c - Multi-Dimensional Patterns
with tab3:
    st.header("H7c: Multi-Dimensional Pattern Analysis")
    st.markdown("Explore complex patterns across multiple character attributes simultaneously")
    
    # Create composite character profiles
    st.markdown("### Character Profile Clustering")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Female character profiles
        st.markdown("#### Female Character Archetypes")
        
        if all(col in chars_filtered.columns for col in ['gender', 'is_protagonist', 'is_sexualized', 'plot_relevance']):
            female_chars = chars_filtered[chars_filtered['gender'] == 'Female'].copy()
            
            # Create profile categories
            def create_profile(row):
                profile_parts = []
                
                if row.get('is_protagonist', False):
                    profile_parts.append('Protagonist')
                elif row.get('is_playable', False):
                    profile_parts.append('Playable')
                else:
                    profile_parts.append('NPC')
                
                profile_parts.append(str(row.get('plot_relevance', 'Unknown')))
                
                if row.get('is_sexualized', False):
                    profile_parts.append('Sexualized')
                else:
                    profile_parts.append('Non-sexualized')
                
                return ' | '.join(profile_parts)
            
            female_chars['profile'] = female_chars.apply(create_profile, axis=1)
            
            profile_counts = female_chars['profile'].value_counts().head(10)
            
            fig = px.bar(
                x=profile_counts.index,
                y=profile_counts.values,
                labels={'x': 'Character Profile', 'y': 'Count'},
                title="Top 10 Female Character Profiles"
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Male character profiles
        st.markdown("#### Male Character Archetypes")
        
        if all(col in chars_filtered.columns for col in ['gender', 'is_protagonist', 'is_sexualized', 'plot_relevance']):
            male_chars = chars_filtered[chars_filtered['gender'] == 'Male'].copy()
            male_chars['profile'] = male_chars.apply(create_profile, axis=1)
            
            male_profile_counts = male_chars['profile'].value_counts().head(10)
            
            fig2 = px.bar(
                x=male_profile_counts.index,
                y=male_profile_counts.values,
                labels={'x': 'Character Profile', 'y': 'Count'},
                title="Top 10 Male Character Profiles",
                color_discrete_sequence=[COLORS['male']]
            )
            fig2.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig2, use_container_width=True)
    
    # Protagonist × Sexualization × Age
    if all(col in chars_filtered.columns for col in ['is_protagonist', 'is_sexualized', 'age_category']):
        st.markdown("### Protagonist Status × Sexualization × Age")
        
        protagonist_sex_age = chars_filtered.groupby(['is_protagonist', 'is_sexualized', 'age_category']).size().reset_index(name='count')
        
        # Filter for protagonists
        protag_data = protagonist_sex_age[protagonist_sex_age['is_protagonist'] == True]
        
        fig3 = px.sunburst(
            protag_data,
            path=['is_sexualized', 'age_category'],
            values='count',
            title="Protagonist Characteristics: Sexualization × Age Distribution"
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # Gender parity analysis by genre
    st.markdown("### Game-Level Patterns: Gender Parity by Genre")
    
    if 'has_gender_parity' in games_filtered.columns and 'genre' in games_filtered.columns:
        parity_by_genre = games_filtered.groupby('genre').agg({
            'has_gender_parity': ['sum', 'count']
        }).reset_index()
        
        parity_by_genre.columns = ['Genre', 'Parity Count', 'Total']
        parity_by_genre['Parity Rate (%)'] = parity_by_genre['Parity Count'] / parity_by_genre['Total'] * 100
        parity_by_genre = parity_by_genre.sort_values('Parity Rate (%)', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig4 = px.bar(
                parity_by_genre,
                x='Genre',
                y='Parity Rate (%)',
                title="Gender Parity Rate by Genre",
                color='Parity Rate (%)',
                color_continuous_scale='Greens'
            )
            fig4.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            st.markdown("### Top Genres for Parity")
            for _, row in parity_by_genre.head(5).iterrows():
                st.write(f"**{row['Genre']}**: {row['Parity Rate (%)']:.1f}%")

# TAB 4: Correlation Matrix
with tab4:
    st.header("Correlation Matrix: All Numeric Variables")
    st.markdown("Explore relationships between all numeric character and game attributes")
    
    # Select numeric columns for correlation
    numeric_cols = []
    
    # Character-level numeric variables
    if 'age' in chars_filtered.columns:
        # Convert age to numeric, coercing errors to NaN
        chars_filtered['age_numeric'] = pd.to_numeric(chars_filtered['age'], errors='coerce')
        numeric_cols.append('age_numeric')
    
    # Binary character variables
    binary_char_cols = ['is_protagonist', 'is_playable', 'is_sexualized', 'is_romantic_interest']
    for col in binary_char_cols:
        if col in chars_filtered.columns:
            chars_filtered[col] = chars_filtered[col].astype(int)
            numeric_cols.append(col)
    
    # Calculate character-level correlations
    if len(numeric_cols) > 1:
        st.markdown("### Character-Level Correlations")
        
        corr_data = chars_filtered[numeric_cols].dropna()
        
        # Rename age_numeric back to age for display
        if 'age_numeric' in corr_data.columns:
            corr_data = corr_data.rename(columns={'age_numeric': 'age'})
        
        if len(corr_data) > 0:
            corr_matrix = corr_data.corr()
            
            # Heatmap
            fig = px.imshow(
                corr_matrix,
                labels=dict(color="Correlation"),
                x=corr_matrix.columns,
                y=corr_matrix.index,
                color_continuous_scale='RdBu_r',
                zmin=-1,
                zmax=1,
                aspect="auto"
            )
            fig.update_layout(
                title="Character Attribute Correlation Matrix",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show strongest correlations
            st.markdown("### 🔗 Strongest Correlations")
            
            # Get upper triangle of correlation matrix
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
            corr_pairs = corr_matrix.where(mask).stack().reset_index()
            corr_pairs.columns = ['Variable 1', 'Variable 2', 'Correlation']
            corr_pairs = corr_pairs.sort_values('Correlation', key=abs, ascending=False).head(10)
            
            st.dataframe(
                corr_pairs.style.format({'Correlation': '{:.3f}'}),
                use_container_width=True,
                hide_index=True
            )
    
    # Game-level correlations
    st.markdown("### Game-Level Correlations")
    
    game_numeric_cols = []
    
    # Game numeric variables
    for col in ['char_pct_Female', 'team_percentage', 'female_team', 'total_team']:
        if col in games_filtered.columns:
            game_numeric_cols.append(col)
    
    # Game binary variables
    game_binary_cols = ['has_female_protagonist', 'has_gender_parity', 'has_female_team']
    for col in game_binary_cols:
        if col in games_filtered.columns:
            games_filtered[col] = games_filtered[col].astype(int)
            game_numeric_cols.append(col)
    
    if len(game_numeric_cols) > 1:
        game_corr_data = games_filtered[game_numeric_cols].dropna()
        
        if len(game_corr_data) > 0:
            game_corr_matrix = game_corr_data.corr()
            
            fig2 = px.imshow(
                game_corr_matrix,
                labels=dict(color="Correlation"),
                x=game_corr_matrix.columns,
                y=game_corr_matrix.index,
                color_continuous_scale='RdBu_r',
                zmin=-1,
                zmax=1,
                aspect="auto"
            )
            fig2.update_layout(
                title="Game Attribute Correlation Matrix",
                height=500
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Strongest game correlations
            st.markdown("### 🔗 Strongest Game-Level Correlations")
            
            mask = np.triu(np.ones_like(game_corr_matrix, dtype=bool), k=1)
            game_corr_pairs = game_corr_matrix.where(mask).stack().reset_index()
            game_corr_pairs.columns = ['Variable 1', 'Variable 2', 'Correlation']
            game_corr_pairs = game_corr_pairs.sort_values('Correlation', key=abs, ascending=False).head(10)
            
            st.dataframe(
                game_corr_pairs.style.format({'Correlation': '{:.3f}'}),
                use_container_width=True,
                hide_index=True
            )

st.markdown("---")

# Summary section
st.header("📝 Intersectional Analysis Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ Key Insights")
    st.markdown("""
    - Young female characters show distinct sexualization patterns
    - Role and relevance distributions vary significantly by gender
    - Complex character profiles reveal archetypal patterns
    - Multiple attributes intersect to create nuanced representations
    - Correlations reveal systemic patterns in representation
    """)

with col2:
    st.markdown("### 📊 Analysis Coverage")
    st.write(f"- Characters analyzed: {len(chars_filtered):,}")
    st.write(f"- Games analyzed: {len(games_filtered):,}")
    st.write(f"- Time period: {year_range[0]}-{year_range[1]}")
    st.write(f"- Dimensions explored: Gender, Age, Role, Relevance, Sexualization")

# Download button
st.markdown("### 📥 Export Data")

col1, col2 = st.columns(2)

with col1:
    csv_chars = chars_filtered.to_csv(index=False)
    st.download_button(
        label="Download Character Data",
        data=csv_chars,
        file_name=f"intersectional_chars_{year_range[0]}-{year_range[1]}.csv",
        mime="text/csv"
    )

with col2:
    csv_games = games_filtered.to_csv(index=False)
    st.download_button(
        label="Download Game Data",
        data=csv_games,
        file_name=f"intersectional_games_{year_range[0]}-{year_range[1]}.csv",
        mime="text/csv"
    )
