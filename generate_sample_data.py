"""
Sample IPL Dataset Generator
Generates realistic matches.csv and deliveries.csv datasets for IPL analysis.
Compatible with standard Kaggle/Cricsheet IPL schemas.
"""

import os
import random
import csv

def generate_ipl_dataset(output_dir="data/raw", num_matches=120):
    os.makedirs(output_dir, exist_ok=True)
    matches_file = os.path.join(output_dir, "matches.csv")
    deliveries_file = os.path.join(output_dir, "deliveries.csv")

    random.seed(42)

    teams = [
        "Chennai Super Kings",
        "Mumbai Indians",
        "Royal Challengers Bangalore",
        "Kolkata Knight Riders",
        "Rajasthan Royals",
        "Sunrisers Hyderabad",
        "Delhi Capitals",
        "Punjab Kings",
        "Gujarat Titans",
        "Lucknow Super Giants"
    ]

    venues = [
        ("Wankhede Stadium, Mumbai", "Mumbai"),
        ("M Chinnaswamy Stadium, Bengaluru", "Bengaluru"),
        ("MA Chidambaram Stadium, Chepauk, Chennai", "Chennai"),
        ("Eden Gardens, Kolkata", "Kolkata"),
        ("Narendra Modi Stadium, Ahmedabad", "Ahmedabad"),
        ("Arun Jaitley Stadium, Delhi", "Delhi"),
        ("Rajiv Gandhi International Stadium, Uppal, Hyderabad", "Hyderabad"),
        ("Sawai Mansingh Stadium, Jaipur", "Jaipur")
    ]

    team_players = {
        "Chennai Super Kings": {
            "batters": ["MS Dhoni", "RD Gaikwad", "S Dube", "RA Jadeja", "AM Rahane", "DJ Mitchell", "MM Ali"],
            "bowlers": ["RA Jadeja", "M Pathirana", "DL Chahar", "T Deshpande", "Mustafizur Rahman", "SN Thakur"]
        },
        "Mumbai Indians": {
            "batters": ["RG Sharma", "SA Yadav", "HH Pandya", "Ishan Kishan", "TH David", "Tilak Varma", "N Wadhera"],
            "bowlers": ["JJ Bumrah", "HH Pandya", "G Coetzee", "PP Chawla", "N Thushara", "L Wood"]
        },
        "Royal Challengers Bangalore": {
            "batters": ["V Kohli", "F du Plessis", "RM Patidar", "GJ Maxwell", "DK Karthik", "WG Jacks", "MK Lomror"],
            "bowlers": ["Mohammed Siraj", "GJ Maxwell", "LH Ferguson", "Yash Dayal", "KV Sharma", "C Green"]
        },
        "Kolkata Knight Riders": {
            "batters": ["SP Narine", "PD Salt", "SS Iyer", "RK Singh", "AD Russell", "VR Iyer", "Ramandeep Singh"],
            "bowlers": ["SP Narine", "CV Varun", "MA Starc", "AD Russell", "Harshit Rana", "VG Arora"]
        },
        "Rajasthan Royals": {
            "batters": ["YBK Jaiswal", "JC Buttler", "SV Samson", "R Parag", "SO Hetmyer", "R Powell", "DC Jurel"],
            "bowlers": ["YS Chahal", "TA Boult", "R Ashwin", "Avesh Khan", "Sandeep Sharma", "NA Burger"]
        },
        "Sunrisers Hyderabad": {
            "batters": ["TM Head", "Abhishek Sharma", "H Klaasen", "AK Markram", "Nithish Kumar Reddy", "Abdul Samad", "Shahbaz Ahmed"],
            "bowlers": ["PJ Cummins", "B Kumar", "T Natarajan", "M Markande", "JD Unadkat", "Shahbaz Ahmed"]
        },
        "Delhi Capitals": {
            "batters": ["RR Pant", "DA Warner", "J Fraser-McGurk", "AR Patel", "T Stubbs", "P Shaw", "Abishek Porel"],
            "bowlers": ["Kuldeep Yadav", "AR Patel", "KK Ahmed", "A Nortje", "Mukesh Kumar", "I Sharma"]
        },
        "Punjab Kings": {
            "batters": ["S Dhawan", "JM Bairstow", "Prabhsimran Singh", "SM Curran", "Shashank Singh", "Ashutosh Sharma", "JM Sharma"],
            "bowlers": ["Arshdeep Singh", "K Rabada", "SM Curran", "HV Patel", "RD Chahar", "Harpreet Brar"]
        },
        "Gujarat Titans": {
            "batters": ["Shubman Gill", "WP Saha", "B Sai Sudharsan", "DA Miller", "A Manohar", "R Tewatia", "Rashid Khan"],
            "bowlers": ["Rashid Khan", "Mohammed Shami", "MM Sharma", "Noor Ahmad", "Umesh Yadav", "SH Johnson"]
        },
        "Lucknow Super Giants": {
            "batters": ["KL Rahul", "Q de Kock", "MP Stoinis", "N Pooran", "A Badoni", "D Padikkal", "Krunal Pandya"],
            "bowlers": ["Ravi Bishnoi", "Mayank Yadav", "Krunal Pandya", "Naveen-ul-Haq", "Yash Thakur", "Mohsin Khan"]
        }
    }

    matches_data = []
    deliveries_data = []

    seasons = [2021, 2022, 2023, 2024]

    for match_id in range(1, num_matches + 1):
        season = random.choice(seasons)
        team1, team2 = random.sample(teams, 2)
        venue, city = random.choice(venues)
        toss_winner = random.choice([team1, team2])
        toss_decision = random.choice(["bat", "field"])

        # Decide first batting team
        if (toss_winner == team1 and toss_decision == "bat") or (toss_winner == team2 and toss_decision == "field"):
            batting_first = team1
            bowling_first = team2
        else:
            batting_first = team2
            bowling_first = team1

        # Simulate Inning 1
        inn1_runs = 0
        inn1_wickets = 0
        inn1_batters = team_players[batting_first]["batters"]
        inn1_bowlers = team_players[bowling_first]["bowlers"]

        striker_idx = 0
        non_striker_idx = 1
        striker = inn1_batters[striker_idx]
        non_striker = inn1_batters[non_striker_idx]
        next_batter_idx = 2

        for over in range(20):
            bowler = random.choice(inn1_bowlers)
            for ball in range(1, 7):
                if inn1_wickets >= 10:
                    break

                # Probability distribution for T20 cricket
                r = random.random()
                is_wicket = 0
                dismissal_kind = ""
                player_dismissed = ""
                fielder = ""

                if r < 0.35: # dot ball
                    batsman_runs = 0
                elif r < 0.65: # single
                    batsman_runs = 1
                elif r < 0.77: # two
                    batsman_runs = 2
                elif r < 0.79: # three
                    batsman_runs = 3
                elif r < 0.88: # four
                    batsman_runs = 4
                elif r < 0.94: # six
                    batsman_runs = 6
                else: # wicket
                    is_wicket = 1
                    batsman_runs = 0
                    inn1_wickets += 1
                    player_dismissed = striker
                    dismissal_kind = random.choice(["caught", "bowled", "lbw", "run out", "stumped"])
                    if dismissal_kind in ["caught", "run out", "stumped"]:
                        fielder = random.choice(team_players[bowling_first]["batters"] + team_players[bowling_first]["bowlers"])

                extra_runs = 1 if random.random() < 0.05 else 0
                total_runs = batsman_runs + extra_runs
                inn1_runs += total_runs

                deliveries_data.append({
                    "match_id": match_id,
                    "inning": 1,
                    "batting_team": batting_first,
                    "bowling_team": bowling_first,
                    "over": over,
                    "ball": ball,
                    "batter": striker,
                    "bowler": bowler,
                    "non_striker": non_striker,
                    "batsman_runs": batsman_runs,
                    "extra_runs": extra_runs,
                    "total_runs": total_runs,
                    "is_wicket": is_wicket,
                    "player_dismissed": player_dismissed,
                    "dismissal_kind": dismissal_kind,
                    "fielder": fielder
                })

                if is_wicket and next_batter_idx < len(inn1_batters):
                    striker = inn1_batters[next_batter_idx]
                    next_batter_idx += 1
                elif batsman_runs in [1, 3]:
                    striker, non_striker = non_striker, striker

            # Rotate strike at end of over
            striker, non_striker = non_striker, striker

        target_runs = inn1_runs + 1

        # Simulate Inning 2
        inn2_runs = 0
        inn2_wickets = 0
        inn2_batters = team_players[bowling_first]["batters"]
        inn2_bowlers = team_players[batting_first]["bowlers"]

        striker_idx = 0
        non_striker_idx = 1
        striker = inn2_batters[striker_idx]
        non_striker = inn2_batters[non_striker_idx]
        next_batter_idx = 2

        match_finished = False

        for over in range(20):
            if match_finished:
                break
            bowler = random.choice(inn2_bowlers)
            for ball in range(1, 7):
                if inn2_wickets >= 10:
                    match_finished = True
                    break

                r = random.random()
                is_wicket = 0
                dismissal_kind = ""
                player_dismissed = ""
                fielder = ""

                if r < 0.35:
                    batsman_runs = 0
                elif r < 0.65:
                    batsman_runs = 1
                elif r < 0.77:
                    batsman_runs = 2
                elif r < 0.79:
                    batsman_runs = 3
                elif r < 0.88:
                    batsman_runs = 4
                elif r < 0.94:
                    batsman_runs = 6
                else:
                    is_wicket = 1
                    batsman_runs = 0
                    inn2_wickets += 1
                    player_dismissed = striker
                    dismissal_kind = random.choice(["caught", "bowled", "lbw", "run out"])
                    if dismissal_kind in ["caught", "run out"]:
                        fielder = random.choice(team_players[batting_first]["batters"] + team_players[batting_first]["bowlers"])

                extra_runs = 1 if random.random() < 0.05 else 0
                total_runs = batsman_runs + extra_runs
                inn2_runs += total_runs

                deliveries_data.append({
                    "match_id": match_id,
                    "inning": 2,
                    "batting_team": bowling_first,
                    "bowling_team": batting_first,
                    "over": over,
                    "ball": ball,
                    "batter": striker,
                    "bowler": bowler,
                    "non_striker": non_striker,
                    "batsman_runs": batsman_runs,
                    "extra_runs": extra_runs,
                    "total_runs": total_runs,
                    "is_wicket": is_wicket,
                    "player_dismissed": player_dismissed,
                    "dismissal_kind": dismissal_kind,
                    "fielder": fielder
                })

                if inn2_runs >= target_runs:
                    match_finished = True
                    break

                if is_wicket and next_batter_idx < len(inn2_batters):
                    striker = inn2_batters[next_batter_idx]
                    next_batter_idx += 1
                elif batsman_runs in [1, 3]:
                    striker, non_striker = non_striker, striker

            striker, non_striker = non_striker, striker

        # Determine winner
        if inn2_runs >= target_runs:
            winner = bowling_first
            result = "wickets"
            result_margin = 10 - inn2_wickets
        elif inn1_runs > inn2_runs:
            winner = batting_first
            result = "runs"
            result_margin = inn1_runs - inn2_runs
        else:
            winner = batting_first # Super over edge
            result = "tie"
            result_margin = 0

        potm = random.choice(team_players[winner]["batters"][:3] + team_players[winner]["bowlers"][:2])

        matches_data.append({
            "id": match_id,
            "season": season,
            "city": city,
            "date": f"{season}-04-{random.randint(10, 28):02d}",
            "match_type": "League",
            "player_of_match": potm,
            "venue": venue,
            "team1": team1,
            "team2": team2,
            "toss_winner": toss_winner,
            "toss_decision": toss_decision,
            "winner": winner,
            "result": result,
            "result_margin": result_margin,
            "target_runs": target_runs
        })

    # Save matches.csv
    match_fields = ["id", "season", "city", "date", "match_type", "player_of_match", "venue", "team1", "team2", "toss_winner", "toss_decision", "winner", "result", "result_margin", "target_runs"]
    with open(matches_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=match_fields)
        writer.writeheader()
        writer.writerows(matches_data)

    # Save deliveries.csv
    deliv_fields = ["match_id", "inning", "batting_team", "bowling_team", "over", "ball", "batter", "bowler", "non_striker", "batsman_runs", "extra_runs", "total_runs", "is_wicket", "player_dismissed", "dismissal_kind", "fielder"]
    with open(deliveries_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=deliv_fields)
        writer.writeheader()
        writer.writerows(deliveries_data)

    print(f"Generated {len(matches_data)} matches in {matches_file}")
    print(f"Generated {len(deliveries_data)} deliveries in {deliveries_file}")

if __name__ == "__main__":
    generate_ipl_dataset()
