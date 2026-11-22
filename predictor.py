"""
Machine Learning Predictor module for IPL matches.
Trains and evaluates match outcome prediction models and provides inference functions.
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "match_predictor.pkl")

def prepare_match_features(matches: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Extracts features and target for pre-match winner prediction.
    """
    # Exclude No Result or tied matches without clear winner
    valid = matches[
        (matches["winner"].notna()) &
        (matches["winner"] != "No Result") &
        (matches["team1"].notna()) &
        (matches["team2"].notna())
    ].copy()

    # Features: team1, team2, venue, toss_winner, toss_decision
    features = ["team1", "team2", "venue", "toss_winner", "toss_decision"]
    X = valid[features]
    y = valid["winner"]

    return X, y

def train_match_predictor(matches: pd.DataFrame, force_retrain: bool = False) -> Dict[str, Any]:
    """
    Trains a classification pipeline and saves the model to disk.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)

    if os.path.exists(MODEL_PATH) and not force_retrain:
        try:
            saved_data = joblib.load(MODEL_PATH)
            return saved_data
        except Exception:
            pass

    X, y = prepare_match_features(matches)

    # In case dataset is small during initial tests
    if len(X) < 10:
        return {"error": "Not enough match records to train model."}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    categorical_features = ["team1", "team2", "venue", "toss_winner", "toss_decision"]
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ]
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42))
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = round(accuracy_score(y_test, y_pred) * 100, 2)

    data_to_save = {
        "pipeline": pipeline,
        "accuracy": acc,
        "features": categorical_features,
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    }

    joblib.dump(data_to_save, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH} with test accuracy: {acc}%")
    return data_to_save

def predict_pre_match(team1: str, team2: str, venue: str, toss_winner: str, toss_decision: str) -> Dict[str, Any]:
    """
    Predicts winning probabilities between team1 and team2 before the match starts.
    """
    if not os.path.exists(MODEL_PATH):
        from src.data_loader import load_and_clean_data
        matches, _ = load_and_clean_data()
        train_match_predictor(matches)

    model_data = joblib.load(MODEL_PATH)
    pipeline = model_data["pipeline"]

    input_df = pd.DataFrame([{
        "team1": team1,
        "team2": team2,
        "venue": venue,
        "toss_winner": toss_winner,
        "toss_decision": toss_decision
    }])

    probs = pipeline.predict_proba(input_df)[0]
    classes = pipeline.classes_

    team1_prob = 0.5
    team2_prob = 0.5

    if team1 in classes:
        team1_prob = probs[list(classes).index(team1)]
    if team2 in classes:
        team2_prob = probs[list(classes).index(team2)]

    total_prob = team1_prob + team2_prob
    if total_prob > 0:
        team1_prob = round(float(team1_prob / total_prob) * 100, 1)
        team2_prob = round(float(team2_prob / total_prob) * 100, 1)
    else:
        team1_prob, team2_prob = 50.0, 50.0

    winner = team1 if team1_prob >= team2_prob else team2

    return {
        "predicted_winner": winner,
        "team1": team1,
        "team1_prob": team1_prob,
        "team2": team2,
        "team2_prob": team2_prob,
        "model_accuracy": model_data.get("accuracy", 0.0)
    }

def calculate_live_chase_probability(
    batting_team: str,
    bowling_team: str,
    target_runs: int,
    current_score: int,
    overs_completed: float,
    wickets_lost: int
) -> Dict[str, Any]:
    """
    Calculates live in-game chase win probability using situational cricket metrics
    (runs needed, balls left, wickets remaining, required run rate vs current run rate).
    """
    runs_needed = max(0, target_runs - current_score)
    full_overs = int(overs_completed)
    balls_in_over = int(round((overs_completed - full_overs) * 10))
    balls_bowled = min(120, (full_overs * 6) + balls_in_over)
    balls_left = max(0, 120 - balls_bowled)
    wickets_left = max(0, 10 - wickets_lost)

    crr = round((current_score / (balls_bowled / 6)), 2) if balls_bowled > 0 else 0.0
    rrr = round((runs_needed / (balls_left / 6)), 2) if balls_left > 0 else (0.0 if runs_needed == 0 else 99.0)

    # Situational heuristic calibrated to T20 chase dynamics
    if runs_needed == 0:
        chase_prob = 100.0
    elif wickets_left == 0 or (balls_left == 0 and runs_needed > 0):
        chase_prob = 0.0
    else:
        # Base probability from RRR vs benchmark (8.5 rpo in modern T20)
        # Higher wickets in hand increases chances
        wickets_factor = (wickets_left / 10.0) ** 1.3
        rr_pressure = (rrr - crr)
        
        # Logistic curve based on pressure
        z = -0.35 * rr_pressure + 1.2 * (wickets_factor - 0.5)
        raw_prob = 1 / (1 + np.exp(-z))
        chase_prob = float(np.clip(raw_prob * 100, 1.0, 99.0))

    defend_prob = round(100.0 - chase_prob, 1)
    chase_prob = round(chase_prob, 1)

    return {
        "batting_team": batting_team,
        "bowling_team": bowling_team,
        "runs_needed": runs_needed,
        "balls_left": balls_left,
        "wickets_left": wickets_left,
        "crr": crr,
        "rrr": rrr,
        "chase_win_prob": chase_prob,
        "defend_win_prob": defend_prob
    }
