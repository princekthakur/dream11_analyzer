import streamlit as st
import pandas as pd
from itertools import combinations
import numpy as np

# ----------------------------
# 1. STREAMLIT CONFIG
# ----------------------------
st.set_page_config(page_title="Dream11 Optimizer", layout="wide")
st.title("🎯 Dream11 Team Generator")

# ----------------------------
# 2. DATA PROCESSING
# ----------------------------
def process_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    players = []
    
    for _, row in df.iterrows():
        players.append({
            "name": row["Player Name"],
            "role": classify_role(row["Role"]),
            "is_captain": row.get("Captain", "") == "Yes",
            "is_wicketkeeper": row.get("Wicketkeeper", "") == "Yes",
            "team": row["Team"],
            "bat_avg": np.random.randint(20,50) if "Batter" in str(row["Role"]) else 10,
            "strike_rate": np.random.randint(110,150) if "Batter" in str(row["Role"]) else 0,
            "bowl_avg": np.random.randint(15,30) if "Bowler" in str(row["Role"]) else 50,
            "credits": assign_credits(row["Role"])
        })
    return players

def classify_role(role_str):
    if "Wicketkeeper" in str(role_str): return "WK"
    elif "Batter" in str(role_str): return "BAT"
    elif "Bowler" in str(role_str): return "BOWL"
    elif "All-rounder" in str(role_str): return "AR"
    return "UNK"

def assign_credits(role_str):
    if "All-rounder" in str(role_str): return 9.0
    elif "Batter" in str(role_str): return 8.5
    elif "Bowler" in str(role_str): return 8.0
    return 7.5

# ----------------------------
# 3. PITCH ADJUSTMENTS
# ----------------------------
def apply_pitch_effects(players, pitch_type):
    multipliers = {
        "batting": {"BAT": 1.2, "AR": 1.1, "BOWL": 0.8},
        "bowling": {"BOWL": 1.3, "AR": 1.1, "BAT": 0.7},
        "neutral": {"BAT": 1.0, "BOWL": 1.0, "AR": 1.0}
    }
    
    for player in players:
        player["score"] *= multipliers[pitch_type].get(player["role"], 1.0)

# ----------------------------
# 4. TEAM OPTIMIZATION
# ----------------------------
def optimize_team(players, pitch_type):
    # Calculate base scores
    for player in players:
        bat_score = (player["bat_avg"] * 0.5) + (player["strike_rate"] * 0.3)
        bowl_score = (25 - player["bowl_avg"]) * 0.6
        player["base_score"] = bat_score + bowl_score
        player["score"] = player["base_score"]
    
    # Apply pitch effects
    apply_pitch_effects(players, pitch_type)
    
    # Generate all possible teams
    valid_teams = []
    for team in combinations(players, 11):
        credits = sum(p["credits"] for p in team)
        role_counts = {"WK": 0, "BAT": 0, "BOWL": 0, "AR": 0}
        
        for p in team:
            role_counts[p["role"]] += 1
            
        if (credits <= 100 and role_counts["WK"] >= 1 and 
            3 <= role_counts["BAT"] <= 5 and 
            3 <= role_counts["BOWL"] <= 5 and 
            1 <= role_counts["AR"] <= 4):
            
            sorted_team = sorted(team, key=lambda x: x["score"], reverse=True)
            total_score = sum(p["score"] for p in team)
            total_score += sorted_team[0]["score"] * 0.5  # Captain bonus
            total_score += sorted_team[1]["score"] * 0.25  # VC bonus
            
            valid_teams.append({
                "players": team,
                "total_score": total_score,
                "captain": sorted_team[0],
                "vice_captain": sorted_team[1]
            })
    
    return sorted(valid_teams, key=lambda x: x["total_score"], reverse=True)[:3]

# ----------------------------
# 5. STREAMLIT UI
# ----------------------------
uploaded_file = st.file_uploader("Upload Playing XI Excel", type=["xlsx"])

if uploaded_file:
    players = process_data(uploaded_file)
    
    col1, col2 = st.columns(2)
    with col1:
        pitch_type = st.selectbox("Pitch Type", ["neutral", "batting", "bowling"])
    with col2:
        contest_type = st.selectbox("Contest Type", ["Small League", "Grand League"])
    
    if st.button("Generate Teams"):
        with st.spinner("Optimizing teams..."):
            top_teams = optimize_team(players, pitch_type)
            
            for i, team in enumerate(top_teams, 1):
                with st.expander(f"Team #{i} | Score: {team['total_score']:.1f}"):
                    st.markdown(f"**Captain:** {team['captain']['name']} | "
                               f"**Vice Captain:** {team['vice_captain']['name']}")
                    
                    df = pd.DataFrame([
                        {
                            "Player": p["name"],
                            "Role": p["role"],
                            "Team": p["team"],
                            "Credits": p["credits"],
                            "Score": f"{p['score']:.1f}"
                        } for p in sorted(team["players"], key=lambda x: (-x['score'], x['role']))
                    ])
                    st.dataframe(df, hide_index=True)
