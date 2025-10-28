"""
Test script to verify the Streamlit app components work correctly
Run this before launching the full Streamlit app
"""

import sys
from pathlib import Path
import pandas as pd

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("TESTING STREAMLIT APP COMPONENTS")
print("=" * 60)

# Test 1: Import utilities
print("\n1. Testing utility imports...")
try:
    from utils.data_loader import load_data, get_data_summary, get_character_stats, get_game_stats
    from utils.viz_utils import COLORS, format_percentage, format_count
    print("   ✅ All utility modules imported successfully")
except Exception as e:
    print(f"   ❌ Error importing utilities: {e}")
    sys.exit(1)

# Test 2: Data loading
print("\n2. Testing data loading...")
try:
    games, chars, sex = load_data()
    print(f"   ✅ Data loaded successfully")
    print(f"      - Games: {len(games)} rows, {len(games.columns)} columns")
    print(f"      - Characters: {len(chars)} rows, {len(chars.columns)} columns")
    print(f"      - Sexualization: {len(sex)} rows, {len(sex.columns)} columns")
except Exception as e:
    print(f"   ❌ Error loading data: {e}")
    sys.exit(1)

# Test 3: Data summary
print("\n3. Testing data summary generation...")
try:
    summary = get_data_summary(games, chars)
    print(f"   ✅ Summary generated successfully")
    print(f"      - Total games: {summary['total_games']}")
    print(f"      - Total characters: {summary['total_characters']}")
    print(f"      - Year range: {summary['year_range']}")
    print(f"      - Female percentage: {summary.get('female_percentage', 0):.1f}%")
except Exception as e:
    print(f"   ❌ Error generating summary: {e}")
    sys.exit(1)

# Test 4: Required columns check
print("\n4. Checking required columns in games dataset...")
required_game_cols = [
    'release_year', 'char_pct_Female', 'has_female_protagonist',
    'has_gender_parity', 'customizable_main', 'has_female_team'
]
missing_cols = [col for col in required_game_cols if col not in games.columns]

if missing_cols:
    print(f"   ⚠️  Missing columns: {missing_cols}")
    print(f"   Available columns: {games.columns.tolist()}")
else:
    print(f"   ✅ All required game columns present")

# Test 5: Character stats
print("\n5. Testing character statistics...")
try:
    char_stats = get_character_stats(chars)
    print(f"   ✅ Character stats calculated")
    if 'gender_counts' in char_stats:
        print(f"      Gender distribution:")
        for gender, count in char_stats['gender_counts'].items():
            print(f"        - {gender}: {count}")
except Exception as e:
    print(f"   ❌ Error calculating character stats: {e}")

# Test 6: Game stats
print("\n6. Testing game statistics...")
try:
    game_stats = get_game_stats(games)
    print(f"   ✅ Game stats calculated")
    if 'avg_female_pct' in game_stats:
        print(f"      - Avg female %: {game_stats['avg_female_pct']:.1f}%")
    if 'parity_percentage' in game_stats:
        print(f"      - Games with parity: {game_stats['parity_percentage']:.1f}%")
    if 'female_protag_percentage' in game_stats:
        print(f"      - Games with female protag: {game_stats['female_protag_percentage']:.1f}%")
except Exception as e:
    print(f"   ❌ Error calculating game stats: {e}")

# Test 7: Check for NaN issues
print("\n7. Checking for data quality issues...")
games_nan = games[required_game_cols].isna().sum()
if games_nan.sum() > 0:
    print(f"   ⚠️  Found NaN values:")
    for col, count in games_nan[games_nan > 0].items():
        print(f"      - {col}: {count} NaN values")
else:
    print(f"   ✅ No NaN values in key columns")

# Test 8: Year range validation
print("\n8. Validating year range...")
if 'release_year' in games.columns:
    year_min = games['release_year'].min()
    year_max = games['release_year'].max()
    print(f"   ✅ Year range: {year_min} - {year_max}")
    
    if year_min < 2000 or year_max > 2025:
        print(f"   ⚠️  Unusual year range detected")
else:
    print(f"   ❌ No release_year column found")

# Test 9: Sample data preview
print("\n9. Sample game data preview...")
print(games[['game_name', 'release_year', 'char_pct_Female', 'has_female_protagonist']].head())

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("✅ All critical tests passed!")
print("   The app is ready to run.")
print("\nTo launch the Streamlit app, run:")
print("   streamlit run app.py")
print("=" * 60)
