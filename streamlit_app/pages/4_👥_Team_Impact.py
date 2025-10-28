"""
Team Impact Analysis Page
Explores how development team composition affects representation (Section 4: H4a-H4d)
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
    load_data, filter_data_by_year,
    create_gender_bar_chart, create_box_plot, create_grouped_bar_chart,
    create_pie_chart, create_scatter_plot, create_distribution_histogram,
    display_insight_box, format_percentage, COLORS
)

st.set_page_config(page_title="Team Impact", page_icon="👥", layout="wide")

# Load data
games, chars, sex = load_data()

# Page header
st.title("👥 Development Team Impact on Representation")
st.markdown("""
Explore how the composition of development teams influences gender representation in games.
This analysis examines whether having women on development teams correlates with better
representation outcomes and lower sexualization rates.
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

st.markdown("---")

# Check if we have data
if len(games_filtered) == 0:
    st.warning("⚠️ No games found with the selected filters. Please adjust your filter settings.")
    st.stop()

# Overview metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_games = len(games_filtered)
    st.metric("Total Games", f"{total_games:,}")

with col2:
    if 'has_female_team' in games_filtered.columns:
        games_with_women = games_filtered['has_female_team'].sum()
        st.metric("Games with Women on Team", f"{games_with_women} ({games_with_women/total_games*100:.1f}%)")
    else:
        st.metric("Games with Women on Team", "N/A")

with col3:
    if 'team_percentage' in games_filtered.columns:
        avg_team_pct = games_filtered['team_percentage'].mean()
        st.metric("Avg Team % Female", f"{avg_team_pct:.1f}%")
    else:
        st.metric("Avg Team % Female", "N/A")

with col4:
    if 'female_team' in games_filtered.columns:
        avg_women_count = games_filtered['female_team'].mean()
        st.metric("Avg Women per Team", f"{avg_women_count:.1f}")
    else:
        st.metric("Avg Women per Team", "N/A")

st.markdown("---")

# Create tabs for different analyses
tab1, tab2, tab3, tab4 = st.tabs([
    "H4a: Team & Representation",
    "H4b: Team & Sexualization",
    "H4c: Team & Protagonists",
    "Team Composition"
])

# TAB 1: H4a - Team & Representation
with tab1:
    st.header("H4a: Team Diversity and Character Representation")
    st.markdown("**Hypothesis**: Games with women on the team have higher % female characters")
    
    if 'has_female_team' in games_filtered.columns and 'char_pct_Female' in games_filtered.columns:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Box plot comparing female % by team composition
            games_filtered['team_composition'] = games_filtered['has_female_team'].map({
                True: 'With Women on Team',
                False: 'All-Male Team'
            })
            
            fig = create_box_plot(
                games_filtered[games_filtered['char_pct_Female'].notna()],
                'team_composition',
                'char_pct_Female',
                "Female Character % by Team Composition"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Key Statistics")
            
            # Calculate means for each team type
            with_women = games_filtered[games_filtered['has_female_team'] == True]
            without_women = games_filtered[games_filtered['has_female_team'] == False]
            
            if len(with_women) > 0:
                avg_female_with_women = with_women['char_pct_Female'].mean()
                st.metric("With Women on Team", f"{avg_female_with_women:.1f}%")
            
            if len(without_women) > 0:
                avg_female_without_women = without_women['char_pct_Female'].mean()
                st.metric("All-Male Team", f"{avg_female_without_women:.1f}%")
            
            # Statistical test
            if len(with_women) > 0 and len(without_women) > 0:
                with_vals = with_women['char_pct_Female'].dropna()
                without_vals = without_women['char_pct_Female'].dropna()
                
                if len(with_vals) > 1 and len(without_vals) > 1:
                    t_stat, p_value = stats.ttest_ind(with_vals, without_vals)
                    
                    st.markdown("---")
                    st.markdown("### 🎯 Statistical Test")
                    st.write(f"t-statistic: {t_stat:.2f}")
                    st.write(f"p-value: {p_value:.4f}")
                    
                    if p_value < 0.05:
                        st.success("✅ Significant difference detected")
                        diff = avg_female_with_women - avg_female_without_women
                        st.write(f"Difference: {diff:.1f} percentage points")
                    else:
                        st.info("No significant difference")
        
        # Scatter plot: Team percentage vs Female character percentage
        if 'team_percentage' in games_filtered.columns:
            st.markdown("### Team % Female vs Character % Female")
            
            scatter_data = games_filtered[['title', 'team_percentage', 'char_pct_Female', 'release_year']].copy()
            scatter_data = scatter_data.dropna(subset=['team_percentage', 'char_pct_Female'])
            
            if len(scatter_data) > 0:
                fig2 = create_scatter_plot(
                    scatter_data,
                    'team_percentage',
                    'char_pct_Female',
                    "Correlation: Team % Female vs Character % Female",
                    color_col='release_year'
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # Calculate correlation
                corr, p_val = stats.pearsonr(scatter_data['team_percentage'], scatter_data['char_pct_Female'])
                
                display_insight_box(
                    "Correlation Analysis",
                    f"Pearson correlation coefficient: {corr:.3f} (p-value: {p_val:.4f}). "
                    f"{'Significant positive correlation' if p_val < 0.05 and corr > 0 else 'No significant correlation'} "
                    f"between team diversity and character representation."
                )
    else:
        st.warning("Team composition or character percentage data not available in dataset")

# TAB 2: H4b - Team & Sexualization
with tab2:
    st.header("H4b: Team Diversity and Sexualization Rates")
    st.markdown("**Hypothesis**: Higher % women on team correlates with lower sexualization rates")
    
    # Merge character sexualization with game team data
    if 'is_sexualized' in chars.columns:
        # Aggregate sexualization by game
        sex_by_game = chars.groupby('game').agg({
            'is_sexualized': 'mean',
            'gender': lambda x: (x == 'Female').sum() / len(x) * 100 if len(x) > 0 else 0
        }).reset_index()
        sex_by_game.columns = ['game_id', 'sexualization_rate', 'female_char_pct']
        
        # Merge with games data
        games_with_sex = games_filtered.merge(sex_by_game, on='game_id', how='left')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Compare sexualization rates by team composition
            if 'has_female_team' in games_with_sex.columns:
                st.markdown("### Sexualization Rate by Team Composition")
                
                with_women = games_with_sex[games_with_sex['has_female_team'] == True]
                without_women = games_with_sex[games_with_sex['has_female_team'] == False]
                
                sex_comparison = pd.DataFrame({
                    'Team Type': ['With Women', 'All-Male'],
                    'Sexualization Rate': [
                        with_women['sexualization_rate'].mean() * 100 if len(with_women) > 0 else 0,
                        without_women['sexualization_rate'].mean() * 100 if len(without_women) > 0 else 0
                    ]
                })
                
                import plotly.express as px
                fig = px.bar(
                    sex_comparison,
                    x='Team Type',
                    y='Sexualization Rate',
                    title="Average Sexualization Rate by Team Composition",
                    color='Team Type',
                    color_discrete_map={'With Women': COLORS['success'], 'All-Male': COLORS['warning']}
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show statistics
                st.write(f"**With Women on Team**: {sex_comparison.iloc[0]['Sexualization Rate']:.1f}%")
                st.write(f"**All-Male Team**: {sex_comparison.iloc[1]['Sexualization Rate']:.1f}%")
        
        with col2:
            # Scatter plot: Team % vs Sexualization Rate
            if 'team_percentage' in games_with_sex.columns:
                st.markdown("### Team % vs Sexualization Rate")
                
                scatter_data = games_with_sex[['team_percentage', 'sexualization_rate']].dropna()
                scatter_data['sexualization_rate'] = scatter_data['sexualization_rate'] * 100
                
                if len(scatter_data) > 0:
                    fig2 = create_scatter_plot(
                        scatter_data,
                        'team_percentage',
                        'sexualization_rate',
                        "Team % Female vs Sexualization Rate"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    # Calculate correlation
                    if len(scatter_data) > 2:
                        corr, p_val = stats.pearsonr(
                            scatter_data['team_percentage'], 
                            scatter_data['sexualization_rate']
                        )
                        st.write(f"**Correlation**: {corr:.3f} (p={p_val:.4f})")
        
        # Female character sexualization by team
        st.markdown("### Female Character Sexualization by Team Composition")
        
        # Get female characters only
        female_chars = chars[chars['gender'] == 'Female'].copy()
        female_chars_with_team = female_chars.merge(
            games_filtered[['game_id', 'has_female_team']], 
            left_on='game',
            right_on='game_id',
            how='left'
        )
        
        if len(female_chars_with_team) > 0 and 'is_sexualized' in female_chars_with_team.columns:
            sex_by_team = female_chars_with_team.groupby('has_female_team')['is_sexualized'].mean() * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig3 = px.bar(
                    x=['All-Male Team', 'With Women on Team'],
                    y=[sex_by_team.get(False, 0), sex_by_team.get(True, 0)],
                    labels={'x': 'Team Type', 'y': 'Sexualization Rate (%)'},
                    title="Female Character Sexualization Rate by Team Type",
                    color=['All-Male Team', 'With Women on Team'],
                    color_discrete_map={'With Women on Team': COLORS['success'], 'All-Male Team': COLORS['warning']}
                )
                fig3.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig3, use_container_width=True)
            
            with col2:
                st.markdown("### 📊 Summary")
                st.write(f"**Female characters in games with women on team**: {sex_by_team.get(True, 0):.1f}% sexualized")
                st.write(f"**Female characters in all-male team games**: {sex_by_team.get(False, 0):.1f}% sexualized")
                
                diff = sex_by_team.get(False, 0) - sex_by_team.get(True, 0)
                if diff > 0:
                    st.success(f"✅ {diff:.1f} percentage point reduction in sexualization with women on team")
                else:
                    st.info(f"Teams with women show {abs(diff):.1f} percentage point {'increase' if diff < 0 else 'difference'}")
    else:
        st.warning("Sexualization data not available in dataset")

# TAB 3: H4c - Team & Protagonists
with tab3:
    st.header("H4c: Team Diversity and Protagonist Gender")
    st.markdown("**Hypothesis**: Games with women on team are more likely to have female protagonists")
    
    if 'has_female_team' in games_filtered.columns and 'has_female_protagonist' in games_filtered.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Contingency table
            contingency = pd.crosstab(
                games_filtered['has_female_team'],
                games_filtered['has_female_protagonist'],
                margins=True
            )
            contingency.index = ['All-Male Team', 'With Women on Team', 'Total']
            contingency.columns = ['Male Protagonist', 'Female Protagonist', 'Total']
            
            st.markdown("### Protagonist Gender by Team Composition")
            st.dataframe(contingency, use_container_width=True)
        
        with col2:
            # Percentage breakdown
            contingency_pct = pd.crosstab(
                games_filtered['has_female_team'],
                games_filtered['has_female_protagonist'],
                normalize='index'
            ) * 100
            
            st.markdown("### Percentage Breakdown")
            
            import plotly.graph_objects as go
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Male Protagonist',
                x=['All-Male Team', 'With Women on Team'],
                y=[contingency_pct.loc[False, False] if False in contingency_pct.index else 0,
                   contingency_pct.loc[True, False] if True in contingency_pct.index else 0],
                marker_color=COLORS['male']
            ))
            fig.add_trace(go.Bar(
                name='Female Protagonist',
                x=['All-Male Team', 'With Women on Team'],
                y=[contingency_pct.loc[False, True] if False in contingency_pct.index else 0,
                   contingency_pct.loc[True, True] if True in contingency_pct.index else 0],
                marker_color=COLORS['female']
            ))
            
            fig.update_layout(
                title="Protagonist Gender Distribution by Team Composition",
                barmode='stack',
                yaxis_title="Percentage",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistical test
        st.markdown("### Statistical Analysis")
        
        contingency_test = pd.crosstab(
            games_filtered['has_female_team'],
            games_filtered['has_female_protagonist']
        )
        
        if contingency_test.size > 0 and contingency_test.min().min() >= 5:
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_test)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Chi-square", f"{chi2:.2f}")
            
            with col2:
                st.metric("p-value", f"{p_value:.4f}")
            
            with col3:
                if p_value < 0.05:
                    st.success("✅ Significant")
                else:
                    st.info("Not Significant")
            
            # Calculate effect size
            female_protag_with_women = (
                games_filtered[games_filtered['has_female_team'] == True]['has_female_protagonist'].mean() * 100
            )
            female_protag_without_women = (
                games_filtered[games_filtered['has_female_team'] == False]['has_female_protagonist'].mean() * 100
            )
            
            display_insight_box(
                "Key Finding",
                f"Games with women on team have {female_protag_with_women:.1f}% female protagonists, "
                f"compared to {female_protag_without_women:.1f}% for all-male teams. "
                f"Difference: {female_protag_with_women - female_protag_without_women:.1f} percentage points."
            )
        else:
            st.warning("Insufficient data for statistical test")
    else:
        st.warning("Team or protagonist data not available in dataset")

# TAB 4: Team Composition Details
with tab4:
    st.header("Development Team Composition Analysis")
    st.markdown("Detailed breakdown of development team demographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Team size distribution
        if 'total_team' in games_filtered.columns:
            st.markdown("### 👥 Team Size Distribution")
            
            team_size_data = games_filtered['total_team'].dropna()
            
            if len(team_size_data) > 0:
                fig = create_distribution_histogram(
                    team_size_data,
                    "Distribution of Development Team Sizes",
                    "Team Size",
                    bins=15
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.write(f"**Mean team size**: {team_size_data.mean():.1f} people")
                st.write(f"**Median team size**: {team_size_data.median():.1f} people")
                st.write(f"**Range**: {team_size_data.min():.0f} - {team_size_data.max():.0f} people")
    
    with col2:
        # Women per team distribution
        if 'female_team' in games_filtered.columns:
            st.markdown("### 👩 Women per Team Distribution")
            
            women_count_data = games_filtered['female_team'].dropna()
            
            if len(women_count_data) > 0:
                fig2 = create_distribution_histogram(
                    women_count_data,
                    "Distribution of Women per Development Team",
                    "Number of Women",
                    bins=10
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                st.write(f"**Mean**: {women_count_data.mean():.1f} women per team")
                st.write(f"**Median**: {women_count_data.median():.1f} women per team")
                st.write(f"**Games with 0 women**: {(women_count_data == 0).sum()} ({(women_count_data == 0).sum()/len(women_count_data)*100:.1f}%)")
    
    # Team percentage analysis
    if 'team_percentage' in games_filtered.columns:
        st.markdown("### 📊 Team % Female Distribution")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            team_pct_data = games_filtered['team_percentage'].dropna()
            
            if len(team_pct_data) > 0:
                fig3 = create_distribution_histogram(
                    team_pct_data,
                    "Distribution of % Women on Development Teams",
                    "% Women on Team",
                    bins=20
                )
                st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.markdown("### Statistics")
            
            if len(team_pct_data) > 0:
                st.write(f"**Mean**: {team_pct_data.mean():.1f}%")
                st.write(f"**Median**: {team_pct_data.median():.1f}%")
                st.write(f"**Max**: {team_pct_data.max():.1f}%")
                
                # Categorize teams
                zero_pct = (team_pct_data == 0).sum()
                low_pct = ((team_pct_data > 0) & (team_pct_data < 20)).sum()
                medium_pct = ((team_pct_data >= 20) & (team_pct_data < 40)).sum()
                high_pct = (team_pct_data >= 40).sum()
                
                st.markdown("---")
                st.markdown("### Team Categories")
                st.write(f"**0% women**: {zero_pct} games")
                st.write(f"**1-19% women**: {low_pct} games")
                st.write(f"**20-39% women**: {medium_pct} games")
                st.write(f"**40%+ women**: {high_pct} games")
    
    # Director gender analysis
    if 'director' in games_filtered.columns:
        st.markdown("### 🎬 Director Gender Distribution")
        
        director_counts = games_filtered['director'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig4 = create_pie_chart(
                director_counts,
                "Game Directors by Gender"
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            st.markdown("### Distribution")
            for director_type, count in director_counts.items():
                pct = count / len(games_filtered) * 100
                st.write(f"**{director_type}**: {count} games ({pct:.1f}%)")

st.markdown("---")

# Summary section
st.header("📝 Team Impact Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ Key Findings")
    st.markdown("""
    - Teams with women show different representation patterns
    - Team diversity correlates with character representation
    - Sexualization rates vary by team composition
    - Protagonist gender influenced by team demographics
    - Most teams have low percentages of women
    """)

with col2:
    st.markdown("### 📊 Overall Statistics")
    total = len(games_filtered)
    
    if 'has_female_team' in games_filtered.columns:
        with_women = games_filtered['has_female_team'].sum()
        st.write(f"- Games with women on team: {with_women} ({with_women/total*100:.1f}%)")
    
    if 'team_percentage' in games_filtered.columns:
        avg_pct = games_filtered['team_percentage'].mean()
        st.write(f"- Average team % female: {avg_pct:.1f}%")
    
    if 'female_team' in games_filtered.columns:
        avg_women = games_filtered['female_team'].mean()
        st.write(f"- Average women per team: {avg_women:.1f}")
    
    st.write(f"- Total games analyzed: {total:,}")

# Download button
st.markdown("### 📥 Export Data")
csv = games_filtered.to_csv(index=False)
st.download_button(
    label="Download Team Impact Data",
    data=csv,
    file_name=f"team_impact_{year_range[0]}-{year_range[1]}.csv",
    mime="text/csv"
)
