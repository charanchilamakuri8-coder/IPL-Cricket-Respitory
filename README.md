# 🏏 IPL Cricket Analytics & Match Predictor Hub

An end-to-end, beginner-friendly **IPL (Indian Premier League) Analytics and Machine Learning Prediction System** built in Python with **Streamlit** and **Plotly**.

---

## 🌟 Key Features

1. **📊 Tournament Overview**:
   - High-level KPIs: Total matches, franchises, total runs, wickets, and average 1st innings scores.
   - Most successful franchises by total wins and win percentage.
   - Toss impact analysis (Batting first vs. Bowling first win distribution).
   - Stadium and venue match distribution.

2. **⚔️ Team Analytics & Head-to-Head (H2H)**:
   - Deep dive into franchise performance records.
   - Direct Head-to-Head rivalry comparison tool between any two franchises.
   - Historical match outcomes and victory margins.

3. **🏏 Batting Statistics**:
   - **Orange Cap** leaderboard (Top run-scorers).
   - Strike rate vs. batting average interactive scatter charts.
   - Boundary distribution (Fours and Sixes).
   - Adjustable minimum runs filter.

4. **🎯 Bowling Statistics**:
   - **Purple Cap** leaderboard (Top wicket-takers).
   - Economy rate vs. wickets scatter plots.
   - Dot-ball percentages and death-over specialists.
   - Adjustable minimum wickets filter.

5. **👤 Individual Player Profiles**:
   - Unified search tool for any player.
   - Complete career snapshot covering both batting and bowling metrics.

6. **🔮 Machine Learning Match Predictor**:
   - **Pre-Match Outcome Predictor**: Logistic Regression ML pipeline predicting winning probability based on Team 1, Team 2, Venue, Toss Winner, and Toss Decision.
   - **Live In-Game Chase Simulator**: Situation-aware win probability meter that recalculates win chance in real time using target score, current score, overs completed, and wickets lost.

---

## 📁 Project Architecture

```text
IPL-Analysis/
├── data/
│   └── raw/
│       ├── matches.csv              # Match-level records (2008–2024)
│       └── deliveries.csv           # Ball-by-ball delivery events
├── src/
│   ├── __init__.py
│   ├── data_loader.py               # Data ingestion, cleaning & team standardization
│   ├── team_analysis.py             # Team win rates, H2H & toss analytics
│   ├── player_analysis.py           # Batting/bowling stats & individual profiles
│   └── predictor.py                 # Scikit-Learn ML pipeline & chase simulator
├── models/
│   └── match_predictor.pkl          # Trained and serialized ML model
├── scripts/
│   └── generate_sample_data.py      # Realistic IPL dataset generator
├── app.py                           # Interactive Streamlit Web Dashboard
├── requirements.txt                 # Project dependencies
└── README.md                        # Documentation & setup guide
```

---

## 🚀 Step-by-Step Getting Started Guide

### Step 1: Open Terminal in Project Folder
Open PowerShell or Command Prompt in the project folder:
```powershell
cd c:\Users\HP\Desktop\IPL-Analysis
```

### Step 2: (Recommended) Create a Virtual Environment
```powershell
python -m venv venv
```
Activate the virtual environment:
- **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt)**:
  ```cmd
  venv\Scripts\activate.bat
  ```

### Step 3: Install Required Packages
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Streamlit Dashboard
```powershell
streamlit run app.py
```
The dashboard will automatically open in your default browser at `http://localhost:8501`.

---

## 📊 Using Real Historical Kaggle IPL Datasets

This project includes a built-in realistic sample dataset generator so that it works out of the box immediately.

If you want to analyze the complete 2008–2024 Kaggle dataset:
1. Download `matches.csv` and `deliveries.csv` from Kaggle (e.g. from *IPL Complete Dataset (2008-2024)*).
2. Place both files in the `data/raw/` directory:
   - `data/raw/matches.csv`
   - `data/raw/deliveries.csv`
3. Restart or refresh the Streamlit app. The system automatically standardizes franchise names (such as *Delhi Daredevils* to *Delhi Capitals*) and recalculates all metrics!

---

## 🤖 Machine Learning Workflow Explained

1. **Preprocessing & Standardization**:
   - Handles rebranded teams (`Kings XI Punjab` $\rightarrow$ `Punjab Kings`, etc.).
   - Drops abandoned / no-result fixtures to ensure accurate target labels.
2. **Feature Engineering**:
   - Selected features: `team1`, `team2`, `venue`, `toss_winner`, `toss_decision`.
   - `OneHotEncoder(handle_unknown='ignore')` maps categorical data into numerical matrices.
3. **Model Selection**:
   - Utilizes `LogisticRegression(max_iter=1000)` inside a Scikit-Learn `Pipeline` for calibrated probabilities.
4. **Serialization**:
   - Model artifact stored in `models/match_predictor.pkl` via `joblib`.
