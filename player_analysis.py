"""
Player Analytics module for IPL.
Computes batting leaderboards, bowling statistics, and individual player performance breakdowns.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def get_batting_leaderboard(deliveries: pd.DataFrame, min_runs: int = 50) -> pd.DataFrame:
    """
    Computes overall batting statistics for all batters in the dataset.
    """
    # Group by batter
    batter_stats = deliveries.groupby("batter").agg(
        runs=("batsman_runs", "sum"),
        balls=("ball", "count"),
        fours=("batsman_runs", lambda x: (x == 4).sum()),
        sixes=("batsman_runs", lambda x: (x == 6).sum())
    ).reset_index()

    # Calculate dismissals
    dismissals = deliveries[deliveries["player_dismissed"].notna()].groupby("player_dismissed").size().reset_index()
    dismissals.columns = ["batter", "dismissals"]

    # Merge stats
    df = pd.merge(batter_stats, dismissals, on="batter", how="left")
    df["dismissals"] = df["dismissals"].fillna(0).astype(int)

    # Filter by minimum runs
    df = df[df["runs"] >= min_runs].copy()

    # Calculate strike rate & average
    df["strike_rate"] = np.where(df["balls"] > 0, (df["runs"] / df["balls"]) * 100, 0.0)
    df["average"] = np.where(df["dismissals"] > 0, df["runs"] / df["dismissals"], df["runs"])
    df["boundary_runs"] = (df["fours"] * 4) + (df["sixes"] * 6)
    df["boundary_pct"] = np.where(df["runs"] > 0, (df["boundary_runs"] / df["runs"]) * 100, 0.0)

    # Round columns
    df["strike_rate"] = df["strike_rate"].round(2)
    df["average"] = df["average"].round(2)
    df["boundary_pct"] = df["boundary_pct"].round(1)

    df = df.rename(columns={
        "batter": "Batter",
        "runs": "Runs",
        "balls": "Balls Faced",
        "fours": "4s",
        "sixes": "6s",
        "dismissals": "Dismissals",
        "average": "Average",
        "strike_rate": "Strike Rate",
        "boundary_pct": "Boundary %"
    })

    return df.sort_values(by="Runs", ascending=False).reset_index(drop=True)

def get_bowling_leaderboard(deliveries: pd.DataFrame, min_wickets: int = 3) -> pd.DataFrame:
    """
    Computes overall bowling statistics for all bowlers in the dataset.
    """
    # Valid bowler wickets exclude run out
    bowler_wickets_df = deliveries[
        (deliveries["is_wicket"] == 1) &
        (~deliveries["dismissal_kind"].isin(["run out", "retired hurt", "obstructing the field"]))
    ]
    wickets = bowler_wickets_df.groupby("bowler").size().reset_index(name="wickets")

    # Runs conceded & balls bowled
    bowler_stats = deliveries.groupby("bowler").agg(
        runs_conceded=("total_runs", "sum"),
        balls=("ball", "count"),
        dot_balls=("total_runs", lambda x: (x == 0).sum())
    ).reset_index()

    df = pd.merge(bowler_stats, wickets, on="bowler", how="left")
    df["wickets"] = df["wickets"].fillna(0).astype(int)

    # Filter
    df = df[df["wickets"] >= min_wickets].copy()

    df["overs"] = (df["balls"] // 6) + ((df["balls"] % 6) / 10)
    df["economy"] = np.where(df["balls"] > 0, (df["runs_conceded"] / (df["balls"] / 6)), 0.0)
    df["bowling_average"] = np.where(df["wickets"] > 0, df["runs_conceded"] / df["wickets"], np.nan)
    df["bowling_strike_rate"] = np.where(df["wickets"] > 0, df["balls"] / df["wickets"], np.nan)
    df["dot_ball_pct"] = np.where(df["balls"] > 0, (df["dot_balls"] / df["balls"]) * 100, 0.0)

    # Rounding
    df["economy"] = df["economy"].round(2)
    df["bowling_average"] = df["bowling_average"].round(2)
    df["bowling_strike_rate"] = df["bowling_strike_rate"].round(2)
    df["dot_ball_pct"] = df["dot_ball_pct"].round(1)

    df = df.rename(columns={
        "bowler": "Bowler",
        "overs": "Overs",
        "runs_conceded": "Runs Conceded",
        "wickets": "Wickets",
        "economy": "Economy",
        "bowling_average": "Average",
        "bowling_strike_rate": "Strike Rate",
        "dot_ball_pct": "Dot Ball %"
    })

    return df.sort_values(by="Wickets", ascending=False).reset_index(drop=True)

def get_player_profile(deliveries: pd.DataFrame, player_name: str) -> Dict[str, Any]:
    """
    Returns a unified profile for a player containing both batting and bowling records.
    """
    # Batting
    batter_balls = deliveries[deliveries["batter"] == player_name]
    total_runs = int(batter_balls["batsman_runs"].sum())
    balls_faced = len(batter_balls)
    fours = int((batter_balls["batsman_runs"] == 4).sum())
    sixes = int((batter_balls["batsman_runs"] == 6).sum())
    dismissals = int((deliveries["player_dismissed"] == player_name).sum())
    batting_sr = round((total_runs / balls_faced * 100), 2) if balls_faced > 0 else 0.0
    batting_avg = round(total_runs / dismissals, 2) if dismissals > 0 else total_runs

    # Bowling
    bowler_balls = deliveries[deliveries["bowler"] == player_name]
    balls_bowled = len(bowler_balls)
    overs = (balls_bowled // 6) + ((balls_bowled % 6) / 10)
    runs_conceded = int(bowler_balls["total_runs"].sum())
    valid_wickets = bowler_balls[
        (bowler_balls["is_wicket"] == 1) &
        (~bowler_balls["dismissal_kind"].isin(["run out", "retired hurt", "obstructing the field"]))
    ]
    wickets = len(valid_wickets)
    economy = round(runs_conceded / (balls_bowled / 6), 2) if balls_bowled > 0 else 0.0

    return {
        "player": player_name,
        "batting": {
            "runs": total_runs,
            "balls": balls_faced,
            "fours": fours,
            "sixes": sixes,
            "dismissals": dismissals,
            "strike_rate": batting_sr,
            "average": batting_avg
        },
        "bowling": {
            "balls": balls_bowled,
            "overs": overs,
            "runs_conceded": runs_conceded,
            "wickets": wickets,
            "economy": economy
        }
    }
