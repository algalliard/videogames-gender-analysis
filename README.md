# Gender Representation in Video Games - Interactive Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 📊 Project Overview

This interactive Streamlit dashboard provides a comprehensive analysis of gender representation in video games from 2012-2022. The project examines patterns across multiple dimensions including temporal trends, character roles, sexualization, team composition, and intersectional patterns.

## 🎯 Features

The dashboard includes 5 analytical pages:

1. **📈 Temporal Trends** - Evolution of representation over time
2. **👥 Character Analysis** - Character-level patterns (roles, age, sexualization)
3. **🎮 Game Patterns** - Game-level representation analysis
4. **👥 Team Impact** - How development team composition affects representation
5. **🔍 Intersectional Analysis** - Multi-dimensional pattern exploration

## 🚀 Live Demo

Visit the live dashboard: [Your Streamlit App URL]

## 📁 Project Structure

```
videogames gender/
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

The analysis is based on three datasets:

- **games.grivg.csv** - Game metadata including release year, genre, platform, team composition
- **characters.grivg.csv** - Character-level information including gender, age, role, plot relevance
- **sexualization.grivg.csv** - Sexualization indicators for characters

## 🔧 Configuration

The app uses preprocessed data loaded from CSV files. To use your own data:

1. Update the CSV files in the root directory
2. Ensure column names match the expected format (see `utils/data_loader.py`)
3. Restart the Streamlit app

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

- Your Name - Initial work

## 🙏 Acknowledgments

- Data sourced from video game databases
- Built with Streamlit, Plotly, and Pandas

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This is an exploratory data analysis (EDA) project focused on understanding patterns in gender representation. No machine learning models are included.
