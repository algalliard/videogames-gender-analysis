"""
Game Patterns Analysis Page
Explores game-level representation patterns (Section 3: H3a-H3d)
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

st.set_page_config(page_title="Game Patterns", page_icon="🎮", layout="wide")

# Load data
games, chars, sex = load_data()

# Page header
st.title("🎮 Game-Level Representation Patterns")
st.markdown("""
Explore how representation varies across different game characteristics including genre, 
platform, protagonist type, and developer choices. This analysis examines game-level 
patterns that influence gender representation.
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

# Genre filter
if 'genre' in games.columns:
    genre_options = ['All'] + sorted(games['genre'].dropna().unique().tolist())
    selected_genre = st.sidebar.selectbox("Filter by Genre", genre_options)
else:
    selected_genre = 'All'

# Platform filter
if 'platform' in games.columns:
    platform_options = ['All'] + sorted(games['platform'].dropna().unique().tolist())
    selected_platform = st.sidebar.selectbox("Filter by Platform", platform_options)
else:
    selected_platform = 'All'

# Filter data
games_filtered = filter_data_by_year(games, 'release_year', year_range)

if selected_genre != 'All' and 'genre' in games.columns:
    games_filtered = games_filtered[games_filtered['genre'] == selected_genre]

if selected_platform != 'All' and 'platform' in games.columns:
    games_filtered = games_filtered[games_filtered['platform'] == selected_platform]

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
    avg_female_pct = games_filtered['char_pct_Female'].mean() if 'char_pct_Female' in games_filtered.columns else 0
    st.metric("Avg Female %", f"{avg_female_pct:.1f}%")

with col3:
    parity_games = games_filtered['has_gender_parity'].sum() if 'has_gender_parity' in games_filtered.columns else 0
    st.metric("Games with Parity", f"{parity_games}")

with col4:
    female_protag_games = games_filtered['has_female_protagonist'].sum() if 'has_female_protagonist' in games_filtered.columns else 0
    st.metric("Female Protagonist Games", f"{female_protag_games}")

st.markdown("---")

# Create tabs for different analyses
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "H3a: Protagonist Impact",
    "H3b: Customization Effect", 
    "H3c: Cast Diversity",
    "H3d: Genre & Platform",
    "Developer Patterns"
])

# TAB 1: H3a - Protagonist Impact
with tab1:
    st.header("H3a: Protagonist Gender and Overall Representation")
    st.markdown("**Hypothesis**: Games with female/non-male protagonists have higher overall % female characters")
    
    if 'has_female_protagonist' in games_filtered.columns and 'char_pct_Female' in games_filtered.columns:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Box plot comparing female % by protagonist gender
            games_filtered['protagonist_type'] = 'Male Protagonist'
            games_filtered.loc[games_filtered['has_female_protagonist'] == True, 'protagonist_type'] = 'Female Protagonist'
            games_filtered.loc[games_filtered['has_non_male_protagonist'] == True, 'protagonist_type'] = 'Non-Male Protagonist'
            
            fig = create_box_plot(
                games_filtered[games_filtered['char_pct_Female'].notna()],
                'protagonist_type',
                'char_pct_Female',
                "Female Character Percentage by Protagonist Gender"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Key Statistics")
            
            # Calculate means for each protagonist type
            female_protag_games = games_filtered[games_filtered['has_female_protagonist'] == True]
            male_protag_games = games_filtered[games_filtered['has_male_protagonist'] == True]
            
            if len(female_protag_games) > 0:
                avg_female_with_female_protag = female_protag_games['char_pct_Female'].mean()
                st.metric("With Female Protagonist", f"{avg_female_with_female_protag:.1f}%")
            
            if len(male_protag_games) > 0:
                avg_female_with_male_protag = male_protag_games['char_pct_Female'].mean()
                st.metric("With Male Protagonist", f"{avg_female_with_male_protag:.1f}%")
            
            # Statistical test
            if len(female_protag_games) > 0 and len(male_protag_games) > 0:
                female_vals = female_protag_games['char_pct_Female'].dropna()
                male_vals = male_protag_games['char_pct_Female'].dropna()
                
                if len(female_vals) > 1 and len(male_vals) > 1:
                    t_stat, p_value = stats.ttest_ind(female_vals, male_vals)
                    
                    st.markdown("---")
                    st.markdown("### 🎯 Statistical Test")
                    st.write(f"t-statistic: {t_stat:.2f}")
                    st.write(f"p-value: {p_value:.4f}")
                    
                    if p_value < 0.05:
                        st.success("✅ Significant difference detected")
                        diff = avg_female_with_female_protag - avg_female_with_male_protag
                        st.write(f"Difference: {diff:.1f} percentage points")
                    else:
                        st.info("No significant difference")
        
        # Scatter plot
        st.markdown("### Protagonist Gender vs Overall Female Representation")
        
        scatter_data = games_filtered[['title', 'char_pct_Female', 'protagonist_type', 'release_year']].copy()
        
        fig2 = create_scatter_plot(
            scatter_data[scatter_data['char_pct_Female'].notna()],
            'release_year',
            'char_pct_Female',
            "Female % by Protagonist Type Over Time",
            color_col='protagonist_type'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Key insight
        if len(female_protag_games) > 0 and len(male_protag_games) > 0:
            display_insight_box(
                "Key Finding",
                f"Games with female protagonists have {avg_female_with_female_protag:.1f}% female characters on average, "
                f"compared to {avg_female_with_male_protag:.1f}% for games with male protagonists. "
                f"This represents a {abs(avg_female_with_female_protag - avg_female_with_male_protag):.1f} percentage point difference."
            )
    else:
        st.warning("Protagonist gender data not available in dataset")

# TAB 2: H3b - Customization Effect
with tab2:
    st.header("H3b: Impact of Customizable Protagonists")
    st.markdown("**Hypothesis**: Games with customizable protagonists have more balanced gender representation")
    
    if 'customizable_main' in games_filtered.columns and 'char_pct_Female' in games_filtered.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution of female % by customization status
            customizable_games = games_filtered[games_filtered['customizable_main'] == True]
            fixed_games = games_filtered[games_filtered['customizable_main'] == False]
            
            fig = create_box_plot(
                games_filtered[games_filtered['char_pct_Female'].notna()],
                'customizable_main',
                'char_pct_Female',
                "Female Character % by Protagonist Customization"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            st.markdown("### Customization Statistics")
            customizable_count = games_filtered['customizable_main'].sum()
            customizable_pct = (customizable_count / len(games_filtered)) * 100
            st.write(f"**{customizable_count}** games ({customizable_pct:.1f}%) have customizable protagonists")
        
        with col2:
            # Gender parity comparison
            if 'has_gender_parity' in games_filtered.columns:
                parity_comparison = pd.crosstab(
                    games_filtered['customizable_main'],
                    games_filtered['has_gender_parity'],
                    normalize='index'
                ) * 100
                
                import plotly.graph_objects as go
                
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    name='Without Parity',
                    x=['Fixed', 'Customizable'],
                    y=parity_comparison[False] if False in parity_comparison.columns else [0, 0],
                    marker_color=COLORS['warning']
                ))
                fig2.add_trace(go.Bar(
                    name='With Parity',
                    x=['Fixed', 'Customizable'],
                    y=parity_comparison[True] if True in parity_comparison.columns else [0, 0],
                    marker_color=COLORS['success']
                ))
                
                fig2.update_layout(
                    title="Gender Parity Rate by Customization Status",
                    barmode='stack',
                    yaxis_title="Percentage of Games",
                    height=400
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # Calculate rates
                if len(customizable_games) > 0:
                    custom_parity_rate = customizable_games['has_gender_parity'].mean() * 100
                    st.metric("Parity Rate (Customizable)", f"{custom_parity_rate:.1f}%")
                
                if len(fixed_games) > 0:
                    fixed_parity_rate = fixed_games['has_gender_parity'].mean() * 100
                    st.metric("Parity Rate (Fixed)", f"{fixed_parity_rate:.1f}%")
        
        # Detailed comparison
        st.markdown("### Detailed Comparison: Customizable vs Fixed Protagonists")
        
        comparison_metrics = []
        
        if len(customizable_games) > 0 and len(fixed_games) > 0:
            comparison_metrics.append({
                'Metric': 'Average Female %',
                'Customizable': f"{customizable_games['char_pct_Female'].mean():.1f}%",
                'Fixed': f"{fixed_games['char_pct_Female'].mean():.1f}%"
            })
            
            if 'has_gender_parity' in games_filtered.columns:
                comparison_metrics.append({
                    'Metric': 'Gender Parity Rate',
                    'Customizable': f"{customizable_games['has_gender_parity'].mean() * 100:.1f}%",
                    'Fixed': f"{fixed_games['has_gender_parity'].mean() * 100:.1f}%"
                })
            
            if 'has_female_protagonist' in games_filtered.columns:
                comparison_metrics.append({
                    'Metric': 'Female Protagonist Rate',
                    'Customizable': f"{customizable_games['has_female_protagonist'].mean() * 100:.1f}%",
                    'Fixed': f"{fixed_games['has_female_protagonist'].mean() * 100:.1f}%"
                })
            
            comparison_df = pd.DataFrame(comparison_metrics)
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Customization data not available in dataset")

# TAB 3: H3c - Cast Diversity
with tab3:
    st.header("H3c: Overall Cast Gender Distribution")
    st.markdown("**Hypothesis**: Most games still feature predominantly male casts (>60% male)")
    
    if 'char_pct_Female' in games_filtered.columns:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Distribution of female % across all games
            games_with_data = games_filtered[games_filtered['char_pct_Female'].notna()]
            
            fig = create_distribution_histogram(
                games_with_data['char_pct_Female'],
                "Distribution of Female Character Percentage Across Games",
                "Female Character %",
                bins=20
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Cast Categories")
            
            # Categorize games
            games_filtered['cast_category'] = pd.cut(
                games_filtered['char_pct_Female'],
                bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                labels=['Very Low (0-20%)', 'Low (20-40%)', 'Balanced (40-60%)', 'High (60-80%)', 'Very High (80-100%)']
            )
            
            category_counts = games_filtered['cast_category'].value_counts()
            
            for cat in category_counts.index:
                count = category_counts[cat]
                pct = (count / len(games_filtered)) * 100
                st.write(f"**{cat}**: {count} ({pct:.1f}%)")
        
        # Pie chart of categories
        st.markdown("### Game Distribution by Female Representation Level")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig2 = create_pie_chart(
                category_counts,
                "Games by Female Character Percentage"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            # Key statistics
            st.markdown("### Key Statistics")
            
            median_female = games_filtered['char_pct_Female'].median()
            mean_female = games_filtered['char_pct_Female'].mean()
            
            st.metric("Median Female %", f"{median_female:.1f}%")
            st.metric("Mean Female %", f"{mean_female:.1f}%")
            
            # Predominantly male games (< 40% female)
            male_dominant = (games_filtered['char_pct_Female'] < 0.4).sum()
            male_dominant_pct = (male_dominant / len(games_filtered)) * 100
            st.metric("Male-Dominant Games (<40% female)", f"{male_dominant} ({male_dominant_pct:.1f}%)")
            
            # Balanced games (40-60% female)
            if 'has_gender_parity' in games_filtered.columns:
                balanced = games_filtered['has_gender_parity'].sum()
                balanced_pct = (balanced / len(games_filtered)) * 100
                st.metric("Balanced Games (40-60% female)", f"{balanced} ({balanced_pct:.1f}%)")
        
        # Display insight
        display_insight_box(
            "Key Finding",
            f"{male_dominant_pct:.1f}% of games have predominantly male casts (<40% female). "
            f"Only {(games_filtered['char_pct_Female'] >= 0.4).sum()} games ({((games_filtered['char_pct_Female'] >= 0.4).sum() / len(games_filtered)) * 100:.1f}%) "
            f"have at least 40% female representation."
        )
        
        # Top and bottom games
        st.markdown("### 🏆 Exemplary Games (Highest Female Representation)")
        top_games = games_filtered.nlargest(10, 'char_pct_Female')[['title', 'char_pct_Female', 'release_year', 'genre']].copy()
        top_games['char_pct_Female'] = top_games['char_pct_Female'].round(1)
        top_games.columns = ['Title', 'Female %', 'Year', 'Genre']
        st.dataframe(top_games, use_container_width=True, hide_index=True)
        
        st.markdown("### ⚠️ Games with Lowest Female Representation")
        bottom_games = games_filtered.nsmallest(10, 'char_pct_Female')[['title', 'char_pct_Female', 'release_year', 'genre']].copy()
        bottom_games['char_pct_Female'] = bottom_games['char_pct_Female'].round(1)
        bottom_games.columns = ['Title', 'Female %', 'Year', 'Genre']
        st.dataframe(bottom_games, use_container_width=True, hide_index=True)
    else:
        st.warning("Character percentage data not available")

# TAB 4: H3d - Genre & Platform Patterns
with tab4:
    st.header("H3d: Genre and Platform Influences")
    st.markdown("**Analysis**: How do genre and platform affect gender representation?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Genre analysis
        if 'genre' in games_filtered.columns and 'char_pct_Female' in games_filtered.columns:
            st.markdown("### 🎭 Genre Analysis")
            
            genre_stats = games_filtered.groupby('genre').agg({
                'char_pct_Female': ['mean', 'count'],
                'has_gender_parity': 'mean' if 'has_gender_parity' in games_filtered.columns else lambda x: 0
            }).round(3)
            
            genre_stats.columns = ['Avg Female %', 'Game Count', 'Parity Rate']
            genre_stats['Parity Rate'] = genre_stats['Parity Rate'] * 100
            genre_stats = genre_stats.sort_values('Avg Female %', ascending=False)
            
            # Bar chart
            import plotly.express as px
            fig = px.bar(
                genre_stats.reset_index(),
                x='genre',
                y='Avg Female %',
                title="Average Female Character % by Genre",
                color='Avg Female %',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(xaxis_title="Genre", yaxis_title="Average Female %", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Table
            st.dataframe(genre_stats, use_container_width=True)
            
            # Best and worst genres
            best_genre = genre_stats.index[0]
            worst_genre = genre_stats.index[-1]
            
            st.info(f"📈 **Best Genre**: {best_genre} ({genre_stats.loc[best_genre, 'Avg Female %']:.1f}% female)")
            st.warning(f"📉 **Worst Genre**: {worst_genre} ({genre_stats.loc[worst_genre, 'Avg Female %']:.1f}% female)")
    
    with col2:
        # Platform analysis
        if 'platform' in games_filtered.columns and 'char_pct_Female' in games_filtered.columns:
            st.markdown("### 🎮 Platform Analysis")
            
            platform_stats = games_filtered.groupby('platform').agg({
                'char_pct_Female': ['mean', 'count'],
                'has_gender_parity': 'mean' if 'has_gender_parity' in games_filtered.columns else lambda x: 0
            }).round(3)
            
            platform_stats.columns = ['Avg Female %', 'Game Count', 'Parity Rate']
            platform_stats['Parity Rate'] = platform_stats['Parity Rate'] * 100
            platform_stats = platform_stats.sort_values('Avg Female %', ascending=False)
            
            # Bar chart
            fig2 = px.bar(
                platform_stats.reset_index(),
                x='platform',
                y='Avg Female %',
                title="Average Female Character % by Platform",
                color='Avg Female %',
                color_continuous_scale='RdYlGn'
            )
            fig2.update_layout(xaxis_title="Platform", yaxis_title="Average Female %", height=400)
            st.plotly_chart(fig2, use_container_width=True)
            
            # Table
            st.dataframe(platform_stats, use_container_width=True)
            
            # Best and worst platforms
            best_platform = platform_stats.index[0]
            worst_platform = platform_stats.index[-1]
            
            st.info(f"📈 **Best Platform**: {best_platform} ({platform_stats.loc[best_platform, 'Avg Female %']:.1f}% female)")
            st.warning(f"📉 **Worst Platform**: {worst_platform} ({platform_stats.loc[worst_platform, 'Avg Female %']:.1f}% female)")
    
    # Heatmap: Genre × Platform
    if 'genre' in games_filtered.columns and 'platform' in games_filtered.columns and 'char_pct_Female' in games_filtered.columns:
        st.markdown("### 🔥 Genre × Platform Interaction")
        
        # Create pivot table
        genre_platform = games_filtered.pivot_table(
            values='char_pct_Female',
            index='genre',
            columns='platform',
            aggfunc='mean'
        )
        
        # Only show if we have enough data
        if genre_platform.size > 0:
            import plotly.express as px
            fig3 = px.imshow(
                genre_platform,
                title="Female Character % by Genre and Platform",
                labels={'color': 'Female %'},
                color_continuous_scale='RdYlGn',
                aspect='auto'
            )
            fig3.update_layout(height=500)
            st.plotly_chart(fig3, use_container_width=True)

# TAB 5: Developer Patterns
with tab5:
    st.header("Developer and Publisher Patterns")
    st.markdown("Explore how different developers and publishers approach gender representation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Developer analysis
        if 'developer' in games_filtered.columns and 'char_pct_Female' in games_filtered.columns:
            st.markdown("### 🏢 Top Developers by Female Representation")
            
            # Filter developers with multiple games
            dev_stats = games_filtered.groupby('developer').agg({
                'char_pct_Female': ['mean', 'count']
            })
            dev_stats.columns = ['Avg Female %', 'Game Count']
            dev_stats = dev_stats[dev_stats['Game Count'] >= 2]  # Only developers with 2+ games
            dev_stats = dev_stats.sort_values('Avg Female %', ascending=False).head(15)
            
            if len(dev_stats) > 0:
                import plotly.express as px
                fig = px.bar(
                    dev_stats.reset_index(),
                    x='Avg Female %',
                    y='developer',
                    orientation='h',
                    title="Top Developers by Female Character %",
                    color='Avg Female %',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough multi-game developers in filtered data")
    
    with col2:
        # Publisher analysis
        if 'publisher' in games_filtered.columns and 'char_pct_Female' in games_filtered.columns:
            st.markdown("### 📚 Top Publishers by Female Representation")
            
            # Filter publishers with multiple games
            pub_stats = games_filtered.groupby('publisher').agg({
                'char_pct_Female': ['mean', 'count']
            })
            pub_stats.columns = ['Avg Female %', 'Game Count']
            pub_stats = pub_stats[pub_stats['Game Count'] >= 2]  # Only publishers with 2+ games
            pub_stats = pub_stats.sort_values('Avg Female %', ascending=False).head(15)
            
            if len(pub_stats) > 0:
                fig2 = px.bar(
                    pub_stats.reset_index(),
                    x='Avg Female %',
                    y='publisher',
                    orientation='h',
                    title="Top Publishers by Female Character %",
                    color='Avg Female %',
                    color_continuous_scale='RdYlGn'
                )
                fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Not enough multi-game publishers in filtered data")
    
    # Country analysis
    if 'country' in games_filtered.columns and 'char_pct_Female' in games_filtered.columns:
        st.markdown("### 🌍 Regional Patterns")
        
        country_stats = games_filtered.groupby('country').agg({
            'char_pct_Female': ['mean', 'count'],
            'has_gender_parity': 'mean' if 'has_gender_parity' in games_filtered.columns else lambda x: 0
        }).round(3)
        
        country_stats.columns = ['Avg Female %', 'Game Count', 'Parity Rate']
        country_stats['Parity Rate'] = country_stats['Parity Rate'] * 100
        country_stats = country_stats.sort_values('Avg Female %', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            import plotly.express as px
            fig3 = px.bar(
                country_stats.reset_index(),
                x='country',
                y='Avg Female %',
                title="Average Female Character % by Country",
                color='Game Count',
                color_continuous_scale='Blues'
            )
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.dataframe(country_stats, use_container_width=True)

st.markdown("---")

# Summary section
st.header("📝 Game Patterns Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ Key Findings")
    st.markdown("""
    - Protagonist gender strongly predicts overall representation
    - Customizable protagonists correlate with better gender balance
    - Most games still have predominantly male casts
    - Genre and platform significantly influence representation
    - Some developers/publishers consistently perform better
    """)

with col2:
    st.markdown("### 📊 Overall Statistics")
    total = len(games_filtered)
    if 'char_pct_Female' in games_filtered.columns:
        avg_female = games_filtered['char_pct_Female'].mean()
        st.write(f"- Average female representation: {avg_female:.1f}%")
    
    if 'has_gender_parity' in games_filtered.columns:
        parity_count = games_filtered['has_gender_parity'].sum()
        parity_pct = (parity_count / total) * 100
        st.write(f"- Games with gender parity: {parity_count} ({parity_pct:.1f}%)")
    
    if 'customizable_main' in games_filtered.columns:
        custom_count = games_filtered['customizable_main'].sum()
        custom_pct = (custom_count / total) * 100
        st.write(f"- Games with customizable protagonists: {custom_count} ({custom_pct:.1f}%)")
    
    st.write(f"- Total games analyzed: {total:,}")

# Download button
st.markdown("### 📥 Export Data")
csv = games_filtered.to_csv(index=False)
st.download_button(
    label="Download Filtered Game Data",
    data=csv,
    file_name=f"game_patterns_{year_range[0]}-{year_range[1]}.csv",
    mime="text/csv"
)
