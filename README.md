# Gender Representation in Video Games - Interactive Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 📊 Project Overview

This interactive Streamlit dashboard provides a comprehensive analysis of gender representation in video games from 2012-2022, data obtained from Kaggle public dataset https://www.kaggle.com/datasets/br33sa/gender-representation-in-video-games/ by Brisa. The project examines patterns across multiple dimensions including temporal trends, character roles, sexualization, team composition, and intersectional patterns.

## 🎯 Features

The dashboard includes 5 analytical pages:

1. **📈 Temporal Trends** - Evolution of representation over time
2. **👥 Character Analysis** - Character-level patterns (roles, age, sexualization)
3. **🎮 Game Patterns** - Game-level representation analysis
4. **👥 Team Impact** - How development team composition affects representation
5. **🔍 Intersectional Analysis** - Multi-dimensional pattern exploration

## 🚀 Live Demo

Visit the live dashboard: [Link](https://videogames-gender-analysis-jutskwb47xnnntjg7lnkkx.streamlit.app)

## 📁 Project Structure

```
videogames-gender-analysis/
├── streamlit_app/
│   ├── app.py                          # Main dashboard page
│   ├── requirements.txt                # Python dependencies
│   ├── pages/
│   │   ├── 1_📈_Temporal_Trends.py
│   │   ├── 2_👥_Character_Analysis.py
│   │   ├── 3_🎮_Game_Patterns.py
│   │   ├── 4_👥_Team_Impact.py
│   │   └── 5_🔍_Intersectional_Analysis.py
│   └── utils/
│       ├── __init__.py
│       ├── data_loader.py              # Data loading utilities
│       └── viz_utils.py                # Visualization helpers
├── characters.grivg.csv                # Character-level data
├── games.grivg.csv                     # Game-level data
├── sexualization.grivg.csv             # Sexualization data
├── .gitignore                          # Git ignore rules
└── README.md                           # This file
```

## 💻 Local Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/videogames-gender-analysis.git
cd videogames-gender-analysis
```

2. Install dependencies:
```bash
pip install -r streamlit_app/requirements.txt
```

3. Run the app:
```bash
streamlit run streamlit_app/app.py
```

4. Open your browser to `http://localhost:8501`

## 📦 Dependencies

- streamlit >= 1.28.0
- pandas >= 2.0.0
- plotly >= 5.17.0
- numpy >= 1.24.0
- scipy >= 1.11.0

See `streamlit_app/requirements.txt` for complete list.

## 📊 Data

The analysis is based on three CSV datasets located in the root directory:

- **games.grivg.csv** - Game metadata (64 games):
  - Game ID, title, release date, genre, platform
  - Team composition (total team size, female team members, percentages)
  - Protagonist information
  - Review scores (Metacritic, IGN, GameSpot, etc.)

- **characters.grivg.csv** - Character-level information (600+ characters):
  - Name, gender, age, species
  - Playability status, protagonist status
  - Plot relevance, romantic interest
  - Sexualization indicators

- **sexualization.grivg.csv** - Detailed sexualization metrics:
  - Character-specific sexualization data
  - Visual and narrative indicators

All data is automatically loaded and processed by the Streamlit app from these CSV files.

## 🔧 Configuration

The app automatically loads data from the three CSV files in the root directory:
- `games.grivg.csv`
- `characters.grivg.csv`
- `sexualization.grivg.csv`

No preprocessing or additional setup is required - the data is loaded and transformed automatically by `utils/data_loader.py`.

## 📈 Analysis Framework

The dashboard tests specific hypotheses across 7 dimensions:

- **H1**: Temporal evolution of representation
- **H2**: Character-level patterns (protagonist roles, age, sexualization)
- **H3**: Game-level factors (customization, genre, developer)
- **H4**: Development team impact
- **H5**: Platform and publisher effects
- **H6**: Geographic patterns
- **H7**: Intersectional analysis

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is for educational and research purposes.

## 👥 Authors

- Al Gallego - Initial work

## 🙏 Acknowledgments

- Data sourced from video game databases retrieved by Brisa in Kaggle
- Built with Streamlit, Plotly, and Pandas

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This is an exploratory data analysis (EDA) project focused on understanding patterns in gender representation. No machine learning models are included.
