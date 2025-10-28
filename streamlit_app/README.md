# Gender Representation in Video Games - Interactive Dashboard

An interactive Streamlit dashboard exploring gender representation in video games from 2012-2022. This application visualizes insights from an exploratory data analysis of 64 games and 300+ characters.

## 📊 Features

- **Homepage**: Overview of key metrics and dataset summary
- **Temporal Trends**: Explore how gender representation evolved over time
- **Character Analysis**: Deep dive into character-level patterns
- **Game Patterns**: Analyze game design choices and their impact
- **Team Impact**: Examine how development team composition affects representation
- **Intersectional Analysis**: Multi-dimensional exploration of representation patterns

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. Navigate to the streamlit_app directory:
```bash
cd "c:\Users\lvrga\kaggle\videogames gender\streamlit_app"
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Running the App

Run the Streamlit app with:
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📁 Project Structure

```
streamlit_app/
├── app.py                      # Main dashboard homepage
├── pages/                      # Multi-page app sections
│   ├── 1_📈_Temporal_Trends.py
│   ├── 2_🎭_Character_Analysis.py
│   ├── 3_🎮_Game_Patterns.py
│   ├── 4_👥_Team_Impact.py
│   └── 5_🔍_Intersectional_Analysis.py
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── data_loader.py         # Data loading and caching
│   └── viz_utils.py           # Visualization helpers
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 📈 Data Requirements

The app expects processed data files in the `../processed/` directory:
- `games_clean.csv`: Cleaned game-level data with aggregated features
- `characters_clean.csv`: Cleaned character-level data
- `sexualization_clean.csv`: Sexualization scores

**Note**: Run the preprocessing notebook (`EDA on gender in videogames.ipynb`) first to generate these files.

## 🎨 Key Metrics

The dashboard tracks several key metrics:
- **Female Character %**: Percentage of female characters in games
- **Female Protagonist %**: Games featuring female protagonists
- **Gender Parity %**: Games achieving balanced representation
- **Female Team %**: Games with women in development teams

## 🔍 Analysis Sections

### 1. Temporal Trends
- Evolution of representation over time (2012-2022)
- Protagonist gender trends
- Game design evolution
- Statistical correlations

### 2. Character Analysis
- Gender distribution patterns
- Role assignments by gender
- Age and archetype analysis
- Sexualization patterns

### 3. Game Patterns
- Genre influences on representation
- Platform differences
- Customizable vs. fixed protagonists
- Developer patterns

### 4. Team Impact
- Development team composition effects
- Female-led vs. male-led teams
- Team diversity impact
- Publisher influences

### 5. Intersectional Analysis
- Multi-dimensional representation patterns
- Combined effects of multiple factors
- Correlation analysis
- Complex relationship exploration

## 🛠️ Technologies Used

- **Streamlit**: Web app framework
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computing
- **SciPy**: Statistical analysis

## 📝 Notes

- The app uses caching (`@st.cache_data`) for efficient data loading
- Interactive filters allow dynamic data exploration
- All visualizations are exportable
- Download buttons provided for key datasets

## 🤝 Contributing

This project is part of an EDA analysis. To modify:
1. Update preprocessing in `EDA on gender in videogames.ipynb`
2. Update analysis in `Gender Representation Analysis - EDA.ipynb`
3. Modify app pages as needed

## 📄 License

Educational project - Gender representation analysis in video games.

## 🎯 Future Enhancements

- [ ] Add more interactive filters
- [ ] Include predictive modeling
- [ ] Add comparison tools
- [ ] Export full reports
- [ ] Mobile optimization

## 📧 Contact

For questions or suggestions about this analysis, please refer to the main project documentation.

---

**Data Science Project** | Video Game Gender Representation Analysis | 2012-2022
