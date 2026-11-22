"""
Team Analytics module for IPL.
Computes win rates, head-to-head records, toss impact, and venue statistics.
"""

import pandas as pd
from typing import Dict, Any

def get_overall_team_stats(matches: pd.DataFrame) -> pd.DataFrame:
    """
    Computes overall matches played, wins, losses, and win percentage per team.
    """
    teams = sorted(list(set(matches["team1"].dropna().unique()).union(set(matches["team2"].dropna().unique()))))
    stats = []

    for team in teams:
        played = matches[(matches["team1"] == team) | (matches["team2"] == team)].shape[0]
        won = matches[matches["winner"] == team].shape[0]
        lost = played - won
        win_pct = round((won / played) * 100, 2) if played > 0 else 0.0

        stats.append({
            "Team": team,
            "Matches Played": played,
            "Wins": won,
            "Losses": lost,
            "Win %": win_pct
        })

    df = pd.DataFrame(stats)
    return df.sort_values(by="Wins", ascending=False).reset_index(drop=True)

def get_head_to_head(matches: pd.DataFrame, team1: str, team2: str) -> Dict[str, Any]:
    """
    Computes head-to-head record between two teams.
    """
    h2h_matches = matches[
        ((matches["team1"] == team1) & (matches["team2"] == team2)) |
        ((matches["team1"] == team2) & (matches["team2"] == team1))
    ]

    total_matches = len(h2h_matches)
    team1_wins = len(h2h_matches[h2h_matches["winner"] == team1])
    team2_wins = len(h2h_matches[h2h_matches["winner"] == team2])
    no_result = total_matches - (team1_wins + team2_wins)

    recent_matches = h2h_matches.sort_values(by="season", ascending=False).head(5)[
        ["season", "venue", "toss_winner", "toss_decision", "winner", "result", "result_margin"]
    ]

    return {
        "total_matches": total_matches,
        "team1": team1,
        "team2": team2,
        "team1_wins": team1_wins,
        "team2_wins": team2_wins,
        "no_result": no_result,
        "recent_matches": recent_matches
    }

def get_toss_impact_analysis(matches: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyzes whether winning the toss translates to winning the match,
    and batting first vs fielding first win ratios.
    """
    valid_matches = matches[matches["winner"] != "No Result"].copy()
    total = len(valid_matches)
    if total == 0:
        return {}

    toss_and_match_winner = valid_matches[valid_matches["toss_winner"] == valid_matches["winner"]].shape[0]
    toss_win_match_win_pct = round((toss_and_match_winner / total) * 100, 2)

    # Batting first vs Fielding first win counts
    # Batting first wins: when toss winner elected to bat and won, or elected to field and lost
    # Better yet: check 'result' column if 'runs' -> team batting first won; if 'wickets' -> team fielding first won
    bat_first_wins = valid_matches[valid_matches["result"] == "runs"].shape[0]
    chase_wins = valid_matches[valid_matches["result"] == "wickets"].shape[0]

    decision_counts = valid_matches["toss_decision"].value_counts().to_dict()

    return {
        "total_matches": total,
        "toss_win_match_win_count": toss_and_match_winner,
        "toss_win_match_win_pct": toss_win_match_win_pct,
        "bat_first_wins": bat_first_wins,
        "chase_wins": chase_wins,
        "decision_counts": decision_counts
    }

def get_venue_stats(matches: pd.DataFrame, deliveries: pd.DataFrame, venue: str) -> Dict[str, Any]:
    """
    Computes venue-specific statistics (average 1st innings score, win by batting first vs chasing).
    """
    v_matches = matches[matches["venue"] == venue]
    total_matches = len(v_matches)

    bat_first_wins = len(v_matches[v_matches["result"] == "runs"])
    chase_wins = len(v_matches[v_matches["result"] == "wickets"])

    # Average 1st innings score
    match_ids = v_matches["id"].unique()
    inn1_deliveries = deliveries[(deliveries["match_id"].isin(match_ids)) & (deliveries["inning"] == 1)]
    inn1_totals = inn1_deliveries.groupby("match_id")["total_runs"].sum()
    avg_inn1_score = round(inn1_totals.mean(), 1) if not inn1_totals.empty else 0

    return {
        "venue": venue,
        "total_matches": total_matches,
        "bat_first_wins": bat_first_wins,
        "chase_wins": chase_wins,
        "avg_inn1_score": avg_inn1_score
    }
