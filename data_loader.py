"""
Data loading and preprocessing module for IPL datasets.
Handles file ingestion, team name standardization, and data cleansing.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, List

# Mapping for team rebrands and historical name variations
TEAM_MAPPINGS = {
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Deccan Chargers": "Sunrisers Hyderabad",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
}

def standardize_team_names(name: str) -> str:
    if pd.isna(name):
        return name
    return TEAM_MAPPINGS.get(name.strip(), name.strip())

def ensure_datasets_exist(data_dir: str = "data/raw"):
    """
    Checks if matches.csv and deliveries.csv exist.
    If not found, triggers sample data generator.
    """
    matches_path = os.path.join(data_dir, "matches.csv")
    deliveries_path = os.path.join(data_dir, "deliveries.csv")

    if not (os.path.exists(matches_path) and os.path.exists(deliveries_path)):
        print("Data files not found. Generating sample IPL dataset...")
        try:
            from scripts.generate_sample_data import generate_ipl_dataset
            generate_ipl_dataset(output_dir=data_dir)
        except Exception as e:
            print(f"Error generating data: {e}")

def load_and_clean_data(data_dir: str = "data/raw") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads matches.csv and deliveries.csv, standardizes franchise names,
    and returns cleaned DataFrames.
    """
    ensure_datasets_exist(data_dir)

    matches_path = os.path.join(data_dir, "matches.csv")
    deliveries_path = os.path.join(data_dir, "deliveries.csv")

    matches = pd.read_csv(matches_path)
    deliveries = pd.read_csv(deliveries_path)

    # Standardize team names in matches
    for col in ["team1", "team2", "toss_winner", "winner"]:
        if col in matches.columns:
            matches[col] = matches[col].apply(standardize_team_names)

    # Standardize team names in deliveries
    for col in ["batting_team", "bowling_team"]:
        if col in deliveries.columns:
            deliveries[col] = deliveries[col].apply(standardize_team_names)

    # Clean missing winners or results
    if "winner" in matches.columns:
        matches["winner"] = matches["winner"].fillna("No Result")

    # Ensure correct types
    if "is_wicket" in deliveries.columns:
        deliveries["is_wicket"] = deliveries["is_wicket"].fillna(0).astype(int)
    if "total_runs" in deliveries.columns:
        deliveries["total_runs"] = deliveries["total_runs"].fillna(0).astype(int)
    if "batsman_runs" in deliveries.columns:
        deliveries["batsman_runs"] = deliveries["batsman_runs"].fillna(0).astype(int)

    return matches, deliveries

def get_all_teams(matches: pd.DataFrame) -> List[str]:
    """Returns sorted unique active teams."""
    teams = set(matches["team1"].dropna().unique()).union(set(matches["team2"].dropna().unique()))
    return sorted(list(teams))

def get_all_venues(matches: pd.DataFrame) -> List[str]:
    """Returns sorted unique venues."""
    if "venue" in matches.columns:
        return sorted([v for v in matches["venue"].dropna().unique() if v.strip()])
    return []

def get_all_seasons(matches: pd.DataFrame) -> List[int]:
    """Returns sorted seasons."""
    if "season" in matches.columns:
        return sorted(list(matches["season"].dropna().unique()))
    return []
