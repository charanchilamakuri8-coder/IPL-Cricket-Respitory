"""
IPL Cricket Analysis & Match Prediction Dashboard
Built with Streamlit and Plotly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

from src.data_loader import load_and_clean_data, get_all_teams, get_all_venues, get_all_seasons
from src.team_analysis import (
    get_overall_team_stats,
    get_head_to_head,
    get_toss_impact_analysis,
    get_venue_stats
)
from src.player_analysis import (
    get_batting_leaderboard,
    get_bowling_leaderboard,
    get_player_profile
)
from src.predictor import (
    train_match_predictor,
    predict_pre_match,
    calculate_live_chase_probability
)

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="IPL Analytics & Predictor Hub",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Ingestion & Caching
# ---------------------------------------------------------
@st.cache_data
def get_cached_data():
    matches, deliveries = load_and_clean_data()
    return matches, deliveries

matches_df, deliveries_df = get_cached_data()
all_teams = get_all_teams(matches_df)
all_venues = get_all_venues(matches_df)
all_seasons = get_all_seasons(matches_df)

# Train ML model once in background if needed
train_match_predictor(matches_df)

# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/cricket.png", width=64)
    st.title("IPL Hub")
    st.caption("Comprehensive Cricket Analytics & Prediction")

    page = st.radio(
        "Navigate",
        [
            "📊 Tournament Overview",
            "⚔️ Team Analysis & H2H",
            "🏏 Batting Statistics",
            "🎯 Bowling Statistics",
            "👤 Player Profile",
            "🔮 Match Predictor",
            "📘 Project Guide"
        ]
    )

    st.divider()
    st.markdown("**Dataset Stats**")
    st.write(f"• Matches: **{len(matches_df)}**")
    st.write(f"• Deliveries: **{len(deliveries_df):,}**")
    st.write(f"• Franchises: **{len(all_teams)}**")

# ---------------------------------------------------------
# Page 1: Tournament Overview
# ---------------------------------------------------------
if page == "📊 Tournament Overview":
    st.markdown('<p class="main-title">🏏 IPL Tournament Overview</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">High-level insights, season summaries, and all-time tournament records.</p>', unsafe_allow_html=True)

    # Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    total_runs = deliveries_df["total_runs"].sum()
    total_wickets = deliveries_df[
        (deliveries_df["is_wicket"] == 1) &
        (~deliveries_df["dismissal_kind"].isin(["run out", "retired hurt"]))
    ].shape[0]

    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len(matches_df)}</div><div class="metric-label">Total Matches</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len(all_teams)}</div><div class="metric-label">Franchises</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{total_runs:,}</div><div class="metric-label">Total Runs</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{total_wickets:,}</div><div class="metric-label">Total Wickets</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Team Wins Leaderboard & Toss Decisions
    c1, c2 = st.columns([3, 2])

    with c1:
        st.subheader("🏆 Most Successful Franchises (Wins)")
        team_stats = get_overall_team_stats(matches_df)
        fig_wins = px.bar(
            team_stats,
            x="Wins",
            y="Team",
            orientation="h",
            text="Wins",
            color="Win %",
            color_continuous_scale="Blues",
            title="Total Match Victories & Win Rate %"
        )
        fig_wins.update_layout(yaxis={"categoryorder": "total ascending"}, height=450)
        st.plotly_chart(fig_wins, use_container_width=True)

    with c2:
        st.subheader("🪙 Toss Decision Impact")
        toss_data = get_toss_impact_analysis(matches_df)
        if toss_data:
            decisions = pd.DataFrame(list(toss_data["decision_counts"].items()), columns=["Decision", "Count"])
            fig_toss = px.pie(
                decisions,
                names="Decision",
                values="Count",
                hole=0.45,
                color="Decision",
                color_discrete_map={"bat": "#3B82F6", "field": "#10B981"}
            )
            fig_toss.update_layout(height=450)
            st.plotly_chart(fig_toss, use_container_width=True)

            st.info(
                f"Toss winners went on to win the match in **{toss_data['toss_win_match_win_pct']}%** of fixtures."
            )

    st.markdown("---")
    st.subheader("📈 Matches by Venue")
    venue_counts = matches_df["venue"].value_counts().reset_index()
    venue_counts.columns = ["Venue", "Matches"]
    fig_venue = px.bar(
        venue_counts.head(10),
        x="Venue",
        y="Matches",
        color="Matches",
        color_continuous_scale="Viridis",
        title="Top 10 Stadiums by Matches Hosted"
    )
    fig_venue.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig_venue, use_container_width=True)

# ---------------------------------------------------------
# Page 2: Team Analysis & Head-to-Head
# ---------------------------------------------------------
elif page == "⚔️ Team Analysis & H2H":
    st.markdown('<p class="main-title">⚔️ Team Performance & Head-to-Head</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Detailed franchise records and head-to-head match comparisons.</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Franchise Profile", "Head-to-Head Rivalry"])

    with tab1:
        selected_team = st.selectbox("Select Team", all_teams, index=0)
        team_stats = get_overall_team_stats(matches_df)
        t_row = team_stats[team_stats["Team"] == selected_team].iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Matches Played", t_row["Matches Played"])
        with c2:
            st.metric("Wins", t_row["Wins"])
        with c3:
            st.metric("Losses", t_row["Losses"])
        with c4:
            st.metric("Win %", f"{t_row['Win %']}%")

        st.markdown("#### Recent Matches")
        team_matches = matches_df[(matches_df["team1"] == selected_team) | (matches_df["team2"] == selected_team)]
        recent = team_matches.sort_values(by="id", ascending=False).head(10)[
            ["season", "team1", "team2", "toss_winner", "winner", "result", "result_margin", "venue"]
        ]
        st.dataframe(recent, use_container_width=True)

    with tab2:
        st.markdown("#### Compare Two Teams")
        col_a, col_b = st.columns(2)
        with col_a:
            t1 = st.selectbox("Team 1", all_teams, index=0)
        with col_b:
            t2 = st.selectbox("Team 2", all_teams, index=1 if len(all_teams) > 1 else 0)

        if t1 == t2:
            st.warning("Please select two distinct teams for comparison.")
        else:
            h2h = get_head_to_head(matches_df, t1, t2)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(f"{t1} Wins", h2h["team1_wins"])
            with c2:
                st.metric("Total Encounters", h2h["total_matches"])
            with c3:
                st.metric(f"{t2} Wins", h2h["team2_wins"])

            if h2h["total_matches"] > 0:
                h2h_df = pd.DataFrame({
                    "Team": [t1, t2],
                    "Wins": [h2h["team1_wins"], h2h["team2_wins"]]
                })
                fig_h2h = px.pie(
                    h2h_df,
                    names="Team",
                    values="Wins",
                    title=f"{t1} vs {t2} Win Distribution",
                    hole=0.4,
                    color_discrete_sequence=["#2563EB", "#F59E0B"]
                )
                st.plotly_chart(fig_h2h, use_container_width=True)

                st.markdown("##### Recent Clashes")
                st.dataframe(h2h["recent_matches"], use_container_width=True)
            else:
                st.info("No recorded matches between these two teams in the current dataset.")

# ---------------------------------------------------------
# Page 3: Batting Statistics
# ---------------------------------------------------------
elif page == "🏏 Batting Statistics":
    st.markdown('<p class="main-title">🏏 Batting Statistics & Leaderboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Top run-scorers, highest strike rates, and boundary kings.</p>', unsafe_allow_html=True)

    min_runs = st.slider("Minimum Runs Filter", 20, 500, 100, step=20)
    batting_df = get_batting_leaderboard(deliveries_df, min_runs=min_runs)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("🟠 Orange Cap Contenders (Top 10 Runs)")
        top10_bat = batting_df.head(10)
        fig_bat = px.bar(
            top10_bat,
            x="Runs",
            y="Batter",
            orientation="h",
            color="Strike Rate",
            text="Runs",
            color_continuous_scale="Reds",
            title="Top 10 Run-Scorers"
        )
        fig_bat.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_bat, use_container_width=True)

    with col2:
        st.subheader("⚡ Strike Rate vs Average")
        fig_scatter = px.scatter(
            batting_df.head(25),
            x="Strike Rate",
            y="Average",
            size="Runs",
            color="Boundary %",
            hover_name="Batter",
            title="Strike Rate vs Batting Average (Top 25)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Comprehensive Batting Table")
    st.dataframe(batting_df, use_container_width=True)

# ---------------------------------------------------------
# Page 4: Bowling Statistics
# ---------------------------------------------------------
elif page == "🎯 Bowling Statistics":
    st.markdown('<p class="main-title">🎯 Bowling Statistics & Purple Cap</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Wicket leaders, economy specialists, and strike bowlers.</p>', unsafe_allow_html=True)

    min_w = st.slider("Minimum Wickets Filter", 1, 30, 5, step=1)
    bowling_df = get_bowling_leaderboard(deliveries_df, min_wickets=min_w)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("🟣 Purple Cap Contenders (Top 10 Wickets)")
        top10_bowl = bowling_df.head(10)
        fig_bowl = px.bar(
            top10_bowl,
            x="Wickets",
            y="Bowler",
            orientation="h",
            color="Economy",
            text="Wickets",
            color_continuous_scale="Purples",
            title="Top 10 Wicket-Takers"
        )
        fig_bowl.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_bowl, use_container_width=True)

    with col2:
        st.subheader("🛡️ Economy vs Wickets")
        fig_eco = px.scatter(
            bowling_df.head(25),
            x="Economy",
            y="Wickets",
            size="Dot Ball %",
            color="Average",
            hover_name="Bowler",
            title="Economy vs Wickets (Top 25)"
        )
        st.plotly_chart(fig_eco, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Comprehensive Bowling Table")
    st.dataframe(bowling_df, use_container_width=True)

# ---------------------------------------------------------
# Page 5: Player Profile
# ---------------------------------------------------------
elif page == "👤 Player Profile":
    st.markdown('<p class="main-title">👤 Individual Player Profile</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Detailed individual batting and bowling statistics card.</p>', unsafe_allow_html=True)

    all_players = sorted(list(set(deliveries_df["batter"].dropna().unique()).union(set(deliveries_df["bowler"].dropna().unique()))))
    selected_player = st.selectbox("Search / Select Player", all_players)

    if selected_player:
        profile = get_player_profile(deliveries_df, selected_player)

        st.subheader(f"Performance Summary: {selected_player}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🏏 Batting Record")
            b = profile["batting"]
            st.write(f"• **Total Runs:** {b['runs']}")
            st.write(f"• **Balls Faced:** {b['balls']}")
            st.write(f"• **Batting Average:** {b['average']}")
            st.write(f"• **Strike Rate:** {b['strike_rate']}")
            st.write(f"• **Boundaries:** {b['fours']} Fours, {b['sixes']} Sixes")

        with c2:
            st.markdown("#### 🎯 Bowling Record")
            bw = profile["bowling"]
            st.write(f"• **Wickets:** {bw['wickets']}")
            st.write(f"• **Overs Bowled:** {bw['overs']}")
            st.write(f"• **Runs Conceded:** {bw['runs_conceded']}")
            st.write(f"• **Economy Rate:** {bw['economy']}")

# ---------------------------------------------------------
# Page 6: Match Predictor
# ---------------------------------------------------------
elif page == "🔮 Match Predictor":
    st.markdown('<p class="main-title">🔮 Machine Learning Match Predictor</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Predict pre-match winner probabilities or simulate in-game chase dynamics.</p>', unsafe_allow_html=True)

    pred_mode = st.radio("Prediction Mode", ["Pre-Match Winner Predictor", "Live Chase Win Meter"], horizontal=True)

    if pred_mode == "Pre-Match Winner Predictor":
        st.subheader("Match Setup")
        c1, c2 = st.columns(2)
        with c1:
            team1 = st.selectbox("Team 1 (Batting First)", all_teams, index=0)
            venue = st.selectbox("Venue / Stadium", all_venues, index=0)
        with c2:
            team2 = st.selectbox("Team 2 (Fielding First)", [t for t in all_teams if t != team1], index=0)
            toss_winner = st.selectbox("Toss Winner", [team1, team2])
            toss_decision = st.selectbox("Toss Decision", ["bat", "field"])

        if st.button("🚀 Predict Match Outcome", use_container_width=True):
            res = predict_pre_match(team1, team2, venue, toss_winner, toss_decision)

            st.success(f"### Predicted Winner: **{res['predicted_winner']}**")

            c_prob1, c_prob2 = st.columns(2)
            with c_prob1:
                st.metric(label=f"{team1} Win Probability", value=f"{res['team1_prob']}%")
                st.progress(res["team1_prob"] / 100.0)
            with c_prob2:
                st.metric(label=f"{team2} Win Probability", value=f"{res['team2_prob']}%")
                st.progress(res["team2_prob"] / 100.0)

            st.caption(f"Model Baseline Accuracy on Test Set: **{res['model_accuracy']}%**")

    else:
        st.subheader("🎯 Live In-Game Chase Simulator")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            chasing_team = st.selectbox("Chasing Team (Batting)", all_teams, index=0)
        with col_t2:
            defending_team = st.selectbox("Defending Team (Bowling)", [t for t in all_teams if t != chasing_team], index=0)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            target = st.number_input("Target Score", min_value=50, max_value=300, value=180, step=1)
        with c2:
            current_score = st.number_input("Current Score", min_value=0, max_value=target, value=95, step=1)
        with c3:
            overs = st.number_input("Overs Completed", min_value=0.1, max_value=19.5, value=10.0, step=0.1)
        with c4:
            wickets = st.number_input("Wickets Lost", min_value=0, max_value=10, value=3, step=1)

        chase_res = calculate_live_chase_probability(
            chasing_team, defending_team, target, current_score, overs, wickets
        )

        st.markdown("---")
        st.subheader("Live Win Probability Meter")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Runs Needed", chase_res["runs_needed"])
        with m2:
            st.metric("Balls Remaining", chase_res["balls_left"])
        with m3:
            st.metric("Current Run Rate (CRR)", chase_res["crr"])
        with m4:
            st.metric("Required Run Rate (RRR)", chase_res["rrr"])

        gauge_col1, gauge_col2 = st.columns(2)
        with gauge_col1:
            st.metric(f"{chasing_team} (Chasing)", f"{chase_res['chase_win_prob']}%")
            st.progress(chase_res["chase_win_prob"] / 100.0)
        with gauge_col2:
            st.metric(f"{defending_team} (Defending)", f"{chase_res['defend_win_prob']}%")
            st.progress(chase_res["defend_win_prob"] / 100.0)

# ---------------------------------------------------------
# Page 7: Project Guide
# ---------------------------------------------------------
elif page == "📘 Project Guide":
    st.markdown('<p class="main-title">📘 Beginner Project Architecture & Guide</p>', unsafe_allow_html=True)
    st.markdown("""
    Welcome to the **IPL Cricket Analysis & Prediction Project**!
    
    ### 📂 Folder Structure
    ```text
    IPL-Analysis/
    ├── data/
    │   └── raw/
    │       ├── matches.csv        <- Match-level data (toss, venue, winner)
    │       └── deliveries.csv     <- Ball-by-ball delivery events
    ├── src/
    │   ├── data_loader.py         <- Cleaning, normalization, team mappings
    │   ├── team_analysis.py       <- Win rates, H2H, toss and venue stats
    │   ├── player_analysis.py     <- Batting/bowling metrics & profiles
    │   └── predictor.py           <- Machine learning model & live chase probability
    ├── models/
    │   └── match_predictor.pkl    <- Serialized Scikit-Learn ML pipeline
    ├── scripts/
    │   └── generate_sample_data.py<- Realistic dataset generator
    ├── app.py                     <- Interactive Streamlit dashboard
    ├── requirements.txt           <- Python dependencies
    └── README.md                  <- Detailed step-by-step documentation
    ```

    ### 🚀 How to Run
    1. Activate your virtual environment:
       ```bash
       python -m venv venv
       .\\venv\\Scripts\\activate
       ```
    2. Install dependencies:
       ```bash
       pip install -r requirements.txt
       ```
    3. Launch the dashboard:
       ```bash
       streamlit run app.py
       ```

    ### 🌟 How to Use Real Kaggle Data
    Simply replace `data/raw/matches.csv` and `data/raw/deliveries.csv` with standard Kaggle IPL datasets. The project will automatically load and normalize them!
    """)
