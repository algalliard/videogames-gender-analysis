"""
Data loading and caching utilities for the Streamlit app
"""

import pandas as pd
from pathlib import Path
import streamlit as st

def get_data_path():
    """Get the path to the processed data directory"""
    # App is in videogames gender/streamlit_app/, data is in ../../processed/
    app_dir = Path(__file__).parent.parent  # videogames gender/streamlit_app/
    parent_dir = app_dir.parent  # videogames gender/
    data_dir = parent_dir.parent / "processed"  # kaggle/processed/
    return data_dir

@st.cache_data
def load_data():
    """
    Load the cleaned and processed datasets
    
    Returns:
        tuple: (games, characters, sexualization) DataFrames
    """
    data_dir = get_data_path()
    
    try:
        games = pd.read_csv(data_dir / "games_clean.csv")
        chars = pd.read_csv(data_dir / "characters_clean.csv")
        sex = pd.read_csv(data_dir / "sexualization_clean.csv")
        
        # Convert boolean columns back to boolean
        bool_cols_games = ['customizable_main', 'has_female_team', 'has_non_male_protagonist', 
                          'high_female_representation', 'is_multiplatform', 'has_gender_parity',
                          'has_female_protagonist', 'has_male_protagonist']
        
        bool_cols_chars = ['playable', 'romantic_interest', 'is_sexualized', 'high_sexualization',
                          'is_protagonist', 'is_main_character', 'is_antagonist']
        
        for col in bool_cols_games:
            if col in games.columns:
                games[col] = games[col].astype(bool)
        
        for col in bool_cols_chars:
            if col in chars.columns:
                chars[col] = chars[col].astype(bool)
        
        # Convert categorical columns
        if 'gender' in chars.columns:
            chars['gender'] = chars['gender'].astype('category')
        
        if 'genre' in games.columns:
            games['genre'] = games['genre'].astype('category')
        
        return games, chars, sex
        
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Data files not found in {data_dir}. "
            "Please run the preprocessing notebook first to generate cleaned data."
        )

def get_data_summary(games, chars):
    """
    Generate summary statistics about the datasets
    
    Args:
        games: Games DataFrame
        chars: Characters DataFrame
    
    Returns:
        dict: Summary statistics
    """
    summary = {
        'total_games': len(games),
        'total_characters': len(chars),
        'avg_chars_per_game': len(chars) / len(games) if len(games) > 0 else 0,
    }
    
    # Time range
    if 'release_year' in games.columns:
        summary['year_range'] = (games['release_year'].min(), games['release_year'].max())
    else:
        summary['year_range'] = (None, None)
    
    # Gender distribution
    if 'gender' in chars.columns:
        gender_counts = chars['gender'].value_counts()
        summary['gender_distribution'] = gender_counts.to_dict()
        summary['female_percentage'] = (gender_counts.get('Female', 0) / len(chars) * 100)
    
    # Game statistics
    if 'platform' in games.columns:
        summary['unique_platforms'] = games['platform'].nunique()
    
    if 'genre' in games.columns:
        summary['unique_genres'] = games['genre'].nunique()
    
    if 'developer' in games.columns:
        summary['unique_developers'] = games['developer'].nunique()
    
    return summary

def filter_data_by_year(df, year_col, year_range):
    """
    Filter dataframe by year range
    
    Args:
        df: DataFrame to filter
        year_col: Name of the year column
        year_range: Tuple of (min_year, max_year)
    
    Returns:
        DataFrame: Filtered dataframe
    """
    if year_col not in df.columns:
        return df
    
    return df[
        (df[year_col] >= year_range[0]) &
        (df[year_col] <= year_range[1])
    ]

def filter_data_by_gender(chars, selected_genders):
    """
    Filter characters by selected genders
    
    Args:
        chars: Characters DataFrame
        selected_genders: List of gender values to include
    
    Returns:
        DataFrame: Filtered dataframe
    """
    if not selected_genders:
        return chars
    
    return chars[chars['gender'].isin(selected_genders)]

def get_character_stats(chars):
    """
    Calculate character-level statistics
    
    Args:
        chars: Characters DataFrame
    
    Returns:
        dict: Character statistics
    """
    stats = {}
    
    # Gender distribution
    if 'gender' in chars.columns:
        stats['gender_counts'] = chars['gender'].value_counts()
        stats['gender_percentages'] = chars['gender'].value_counts(normalize=True) * 100
    
    # Playable characters
    if 'playable' in chars.columns:
        stats['playable_count'] = chars['playable'].sum()
        stats['playable_percentage'] = chars['playable'].mean() * 100
    
    # Protagonist characters
    if 'is_protagonist' in chars.columns:
        stats['protagonist_count'] = chars['is_protagonist'].sum()
        stats['protagonist_by_gender'] = chars[chars['is_protagonist']]['gender'].value_counts()
    
    # Sexualization
    if 'is_sexualized' in chars.columns:
        stats['sexualized_count'] = chars['is_sexualized'].sum()
        stats['sexualized_percentage'] = chars['is_sexualized'].mean() * 100
        stats['sexualized_by_gender'] = chars.groupby('gender')['is_sexualized'].mean() * 100
    
    return stats

def get_game_stats(games):
    """
    Calculate game-level statistics
    
    Args:
        games: Games DataFrame
    
    Returns:
        dict: Game statistics
    """
    stats = {}
    
    # Female representation
    if 'char_pct_Female' in games.columns:
        stats['avg_female_pct'] = games['char_pct_Female'].mean()
        stats['median_female_pct'] = games['char_pct_Female'].median()
    
    # Gender parity
    if 'has_gender_parity' in games.columns:
        stats['parity_count'] = games['has_gender_parity'].sum()
        stats['parity_percentage'] = games['has_gender_parity'].mean() * 100
    
    # Female protagonists
    if 'has_female_protagonist' in games.columns:
        stats['female_protag_count'] = games['has_female_protagonist'].sum()
        stats['female_protag_percentage'] = games['has_female_protagonist'].mean() * 100
    
    # Development team
    if 'has_female_team' in games.columns:
        stats['female_team_count'] = games['has_female_team'].sum()
        stats['female_team_percentage'] = games['has_female_team'].mean() * 100
    
    # Customizable protagonists
    if 'customizable_main' in games.columns:
        stats['customizable_count'] = games['customizable_main'].sum()
        stats['customizable_percentage'] = games['customizable_main'].mean() * 100
    
    return stats
