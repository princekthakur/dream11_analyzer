import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from itertools import combinations

# ----------------------------
# 1. TODAY'S PLAYING XI DATA (SRH vs GT - May 16, 2024)
# ----------------------------
srh_gt_players = {
    # SRH Players (with recent performance stats)
    "Travis Head": {"team": "SRH", "role": "BAT", "last5_avg": 52.3, "sr": 175.4, "credits": 9.5},
    "Abhishek Sharma": {"team": "SRH", "role": "AR", "last5_avg": 38.2, "sr": 160.1, "last5_wickets": 4, "credits": 8.5},
    "Heinrich Klaasen": {"team": "SRH", "role": "WK", "last5_avg": 45.6, "sr": 182.3, "credits": 9.0},
    "Pat Cummins": {"team": "SRH", "role": "BOWL", "last5_wickets": 9, "economy": 7.8, "credits": 8.5},
    "Bhuvneshwar Kumar": {"team": "SRH", "role": "BOWL", "last5_wickets": 7, "economy": 8.1, "credits": 8.0},
    
    # GT Players
    "Shubman Gill": {"team": "GT", "role": "BAT", "last5_avg": 48.7, "sr": 145.2, "credits": 10.0},
    "David Miller": {"team": "GT", "role": "BAT", "last5_avg": 42.1, "sr": 155.6, "credits": 9.0},
    "Rashid Khan": {"team": "GT", "role": "BOWL", "last5_wickets": 11, "economy": 6.9, "credits": 9.5},
    "Mohammed Shami": {"team": "GT", "role": "BOWL", "last5_wickets": 8, "economy": 7.5, "credits": 8.5}
}

# ----------------------------
# 2. MACHINE LEARNING MODEL
# ----------------------------
def train_model():
    # Mock training data (replace with real historical Dream11 data)
    data = {
        'avg': [45, 32, 28, 15, 50, 38],
        'sr': [135, 125, 140, 0, 155, 120],
        'wickets': [0, 2, 0, 12, 0, 5],
        'economy': [0, 7.5, 0, 6.8, 0, 8.2],
        'actual_points': [67, 72, 53, 85, 75, 68]
    }
    df = pd.DataFrame(data)
    
    X = df[['avg', 'sr', 'wickets', 'economy']]
    y = df['actual_points']
    
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    return model

# ----------------------------
# 3. PREDICTION ENGINE
# ----------------------------
def predict_points(player_stats, model):
    """Predict Dream11 points using ML model"""
    if player_stats["role"] in ["BAT", "WK"]:
        X = [[player_stats["last5_avg"], player_stats["sr"], 0, 0]]
    else:
        X = [[0, 0, player_stats["last5_wickets"], player_stats["economy"]]]
    return max(10, model.predict(X)[0])  # Ensure minimum 10 points

# ----------------------------
# 4. TEAM OPTIMIZATION
# ----------------------------
def optimize_team(players, model):
    player_list = []
    for name, stats in players.items():
        stats["name"] = name
        stats["predicted"] = predict_points(stats, model)
        player_list.append(stats)
    
    valid_teams = []
    for team in combinations(player_list, 11):
        credits = sum(p["credits"] for p in team)
        roles = {"BAT": 0, "BOWL": 0, "AR": 0, "WK": 0}
        
        for p in team:
            roles[p["role"]] += 1
        
        if (credits <= 100 and roles["WK"] >= 1 and 
            3 <= roles["BAT"] <= 5 and 
            3 <= roles["BOWL"] <= 5 and 
            1 <= roles["AR"] <= 3):
            
            sorted_team = sorted(team, key=lambda x: x["predicted"], reverse=True)
            total = sum(p["predicted"] for p in team)
            total += sorted_team[0]["predicted"] * 0.5  # Captain
            total += sorted_team[1]["predicted"] * 0.25  # VC
            
            valid_teams.append({
                "players": sorted_team,
                "total": round(total),
                "captain": sorted_team[0]["name"],
                "vc": sorted_team[1]["name"]
            })
    
    return sorted(valid_teams, key=lambda x: x["total"], reverse=True)[:3]

# ----------------------------
# 5. STREAMLIT APP
# ----------------------------
def main():
    st.set_page_config(layout="wide")
    st.title("🔥 SRH vs GT Dream11 Predictor (May 16)")
    
    # Load model
    model = train_model()
    
    # Pitch selector
    pitch = st.selectbox("Pitch Condition", ["Batting Paradise", "Balanced", "Bowling Friendly"])
    
    if st.button("Generate Optimal Teams"):
        with st.spinner("Predicting today's best team..."):
            # Adjust stats based on pitch
            for player in srh_gt_players.values():
                if pitch == "Batting Paradise" and player["role"] in ["BAT", "AR", "WK"]:
                    player["last5_avg"] *= 1.15
                    player["sr"] *= 1.05
                elif pitch == "Bowling Friendly" and player["role"] in ["BOWL", "AR"]:
                    player["last5_wickets"] *= 1.2
            
            # Optimize
            teams = optimize_team(srh_gt_players, model)
            
            # Display
            for i, team in enumerate(teams, 1):
                with st.expander(f"Team #{i} | Predicted Points: {team['total']}"):
                    st.markdown(f"**Captain:** {team['captain']} | **Vice Captain:** {team['vc']}")
                    
                    df = pd.DataFrame([{
                        "Player": p["name"],
                        "Role": p["role"],
                        "Team": p["team"],
                        "Credits": p["credits"],
                        "Predicted": p["predicted"]
                    } for p in team["players"]])
                    
                    st.dataframe(
                        df.sort_values("Predicted", ascending=False),
                        hide_index=True,
                        use_container_width=True
                    )

if __name__ == "__main__":
    main()
