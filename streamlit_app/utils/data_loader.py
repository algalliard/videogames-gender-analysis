"""
Data loading and caching utilities for the Streamlit app
"""

import pandas as pd
from pathlib import Path
import streamlit as st

def get_data_path():
    """Get the path to the data directory"""
    # App is in streamlit_app/, data is in parent directory
    app_dir = Path(__file__).parent.parent  # streamlit_app/
    parent_dir = app_dir.parent  # videogames gender/
    return parent_dir

@st.cache_data
def load_data():
    """
    Load the cleaned and processed datasets
    
    Returns:
        tuple: (games, characters, sexualization) DataFrames
    """
    data_dir = get_data_path()
    
    try:
        # Load the CSV files with original names
        games = pd.read_csv(data_dir / "games.grivg.csv")
        chars = pd.read_csv(data_dir / "characters.grivg.csv")
        sex = pd.read_csv(data_dir / "sexualization.grivg.csv")
        
        # Strip any whitespace from column names and rename
        games.columns = games.columns.str.strip()
        chars.columns = chars.columns.str.strip()
        sex.columns = sex.columns.str.strip()
        
        # Rename columns to match expected format
        games_column_map = {
            'Game_Id': 'game_id',
            'Title': 'title',
            'Release': 'release_date',
            'Series': 'series',
            'Genre': 'genre',
            'Sub-genre': 'sub_genre',
            'Developer': 'developer',
            'Publisher': 'publisher',
            'Country': 'country',
            'Platform': 'platform',
            'PEGI': 'pegi',
            'Customizable_main': 'customizable_main',
            'Protagonist': 'protagonist',
            'Protagonist_Non_Male': 'protagonist_non_male',
            'Relevant_males': 'relevant_males',
            'Relevant_no_males': 'relevant_no_males',
            'Percentage_non_male': 'char_pct_Female',
            'Criteria': 'criteria',
            'Director': 'director',
            'Total_team': 'total_team',
            'female_team': 'female_team',
            'Team_percentage': 'team_percentage',
            'Metacritic ': 'metacritic',  # Note the space
            'Metacritic': 'metacritic',
            'Destructoid': 'destructoid',
            'IGN': 'ign',
            'GameSpot': 'gamespot',
            'Avg_Reviews': 'avg_reviews'
        }
        
        chars_column_map = {
            'Name': 'name',
            'Gender': 'gender',
            'Game': 'game',
            'Age': 'age',
            'Age_range': 'age_range',
            'Playable': 'is_playable',
            'Sexualization': 'is_sexualized',
            'Id': 'char_id',
            'Species': 'species',
            'Side': 'side',
            'Relevance': 'plot_relevance',
            'Romantic_Interest': 'is_romantic_interest'
        }
        
        games.rename(columns=games_column_map, inplace=True)
        chars.rename(columns=chars_column_map, inplace=True)
        
        # Extract year from release_date (format: "Nov-13" -> 2013)
        if 'release_date' in games.columns:
            def parse_release_year(date_str):
                if pd.isna(date_str):
                    return None
                try:
                    # Format is "Nov-13" where 13 is 2013
                    year_part = str(date_str).split('-')[-1]
                    year = int(year_part)
                    # Assume 00-99 maps to 2000-2099
                    if year < 100:
                        year = 2000 + year
                    return year
                except:
                    return None
            
            games['release_year'] = games['release_date'].apply(parse_release_year)
        
        # Convert percentage strings to floats (e.g., "18%" -> 18.0)
        if 'char_pct_Female' in games.columns:
            games['char_pct_Female'] = games['char_pct_Female'].str.rstrip('%').astype(float)
        
        if 'team_percentage' in games.columns:
            games['team_percentage'] = games['team_percentage'].str.rstrip('%').astype(float)
        
        # Create derived boolean columns
        # Has female protagonist - check if any protagonist is not male
        games['has_female_protagonist'] = games['protagonist_non_male'] > 0
        
        # Has male protagonist
        if 'relevant_males' in games.columns:
            games['has_male_protagonist'] = games['relevant_males'] > 0
        
        # Has gender parity (40-60% female characters)
        if 'char_pct_Female' in games.columns:
            games['has_gender_parity'] = (games['char_pct_Female'] >= 40) & (games['char_pct_Female'] <= 60)
        
        # Has female team members
        if 'female_team' in games.columns:
            games['has_female_team'] = games['female_team'] > 0
        
        # Convert customizable_main to boolean
        if 'customizable_main' in games.columns:
            games['customizable_main'] = games['customizable_main'].str.lower().isin(['yes', 'true', '1'])
        
        # Add game_id to characters for joining
        chars['game_id'] = chars['game']
        
        # Convert playable and sexualization to boolean
        if 'is_playable' in chars.columns:
            chars['is_playable'] = chars['is_playable'] == 1
            chars['playable'] = chars['is_playable']  # Alias
        
        if 'is_sexualized' in chars.columns:
            # Keep original sexualization level (0-3) and create boolean for any sexualization
            chars['sexualization_level'] = chars['is_sexualized']
            chars['is_sexualized'] = chars['is_sexualized'] > 0  # Any value > 0 means sexualized
        
        if 'is_romantic_interest' in chars.columns:
            chars['is_romantic_interest'] = chars['is_romantic_interest'].str.lower().isin(['yes', 'true'])
        
        # Identify protagonists from relevance column
        if 'plot_relevance' in chars.columns:
            chars['is_protagonist'] = chars['plot_relevance'] == 'PA'  # PA = Primary/Protagonist
            chars['is_main_character'] = chars['plot_relevance'].isin(['PA', 'MC'])  # MC = Main Character
        
        # Convert categorical columns - with safe checks
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
    except Exception as e:
        # More detailed error message
        import traceback
        error_details = traceback.format_exc()
        raise Exception(f"Error processing data: {str(e)}\n\nDetails:\n{error_details}")

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
        years = games['release_year'].dropna()
        if len(years) > 0:
            summary['year_range'] = (int(years.min()), int(years.max()))
        else:
            summary['year_range'] = (None, None)
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
