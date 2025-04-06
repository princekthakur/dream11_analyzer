import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations

# ----------------------------
# 1. CORE FUNCTIONS
# ----------------------------
def classify_role(role_str):
    """Robust role classification with fallback"""
    if pd.isna(role_str):
        return "UNK"
    
    role = str(role_str).lower()
    if "wicket" in role:
        return "WK"
    elif "batter" in role or "bat" in role:
        return "BAT"
    elif "bowler" in role or "bowl" in role:
        return "BOWL"
    elif "all" in role or "rounder" in role:
        return "AR"
    return "UNK"

def assign_credits(role):
    """Dynamic credit assignment"""
    return {
        "WK": 8.5, "BAT": 8.5, 
        "BOWL": 8.0, "AR": 9.0
    }.get(role, 7.5)

def calculate_scores(players):
    """Generate realistic mock scores"""
    for p in players:
        if p["role"] == "BAT":
            p["bat_score"] = np.random.normal(35, 10)
            p["bowl_score"] = 0
        elif p["role"] == "BOWL":
            p["bowl_score"] = np.random.normal(25, 8)
            p["bat_score"] = 0
        else:  # AR/WK
            p["bat_score"] = np.random.normal(25, 7)
            p["bowl_score"] = np.random.normal(15, 5)
        
        p["score"] = (p["bat_score"] * 0.7) + (p["bowl_score"] * 0.5)
        p["credits"] = assign_credits(p["role"])

# ----------------------------
# 2. OPTIMIZATION ENGINE
# ----------------------------
def optimize_team(players, pitch_type="neutral"):
    """Main optimization logic with role balancing"""
    # Pitch multipliers
    multipliers = {
        "batting": {"BAT": 1.2, "AR": 1.1, "WK": 1.1, "BOWL": 0.9},
        "bowling": {"BOWL": 1.3, "AR": 1.1, "BAT": 0.8},
        "neutral": {k: 1.0 for k in ["BAT", "BOWL", "AR", "WK"]}
    }
    
    # Apply pitch effects
    for p in players:
        p["pitch_score"] = p["score"] * multipliers[pitch_type].get(p["role"], 1.0)
    
    # Generate valid teams
    valid_teams = []
    all_players = [p for p in players if p["role"] != "UNK"]  # Exclude unknowns
    
    for team in combinations(all_players, 11):
        credits = sum(p["credits"] for p in team)
        roles = {"WK": 0, "BAT": 0, "BOWL": 0, "AR": 0}
        
        for p in team:
            if p["role"] in roles:
                roles[p["role"]] += 1
        
        # Validate team composition
        if (credits <= 100 and roles["WK"] >= 1 and 
            3 <= roles["BAT"] <= 5 and 
            3 <= roles["BOWL"] <= 5 and 
            1 <= roles["AR"] <= 3):
            
            # Sort by score for captain selection
            sorted_team = sorted(team, key=lambda x: x["pitch_score"], reverse=True)
            total = sum(p["pitch_score"] for p in team)
            total += sorted_team[0]["pitch_score"] * 0.5  # Captain bonus
            total += sorted_team[1]["pitch_score"] * 0.25  # VC bonus
            
            valid_teams.append({
                "players": sorted_team,
                "total": round(total, 1),
                "credits": credits,
                "captain": sorted_team[0]["name"],
                "vc": sorted_team[1]["name"]
            })
    
    return sorted(valid_teams, key=lambda x: x["total"], reverse=True)[:3]

# ----------------------------
# 3. STREAMLIT UI
# ----------------------------
def main():
    st.set_page_config(layout="wide")
    st.title("🏏 Dream11 Team Optimizer")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Playing XI (Excel)", type=["xlsx"])
    if not uploaded_file:
        st.info("👉 Sample format: Player Name | Role | Team | Captain (Yes/No) | Wicketkeeper (Yes/No)")
        return
    
    # Process data
    try:
        df = pd.read_excel(uploaded_file)
        if not all(col in df.columns for col in ["Player Name", "Role", "Team"]):
            st.error("❌ Missing required columns: Player Name, Role, Team")
            return
        
        # Convert to player dicts
        players = []
        for _, row in df.iterrows():
            players.append({
                "name": row["Player Name"],
                "role": classify_role(row["Role"]),
                "team": row["Team"],
                "is_captain": row.get("Captain", "") == "Yes",
                "is_wk": row.get("Wicketkeeper", "") == "Yes"
            })
        
        # Generate mock stats
        calculate_scores(players)
        
        # User inputs
        col1, col2 = st.columns(2)
        with col1:
            pitch = st.selectbox("Pitch Type", ["neutral", "batting", "bowling"])
        with col2:
            contest = st.selectbox("Contest Type", ["Small League", "Grand League"])
        
        # Optimization trigger
        if st.button("✨ Generate Optimal Teams", type="primary"):
            with st.spinner("Crunching numbers..."):
                teams = optimize_team(players, pitch)
                
                if not teams:
                    st.warning("No valid teams found! Check player roles/credits.")
                    return
                
                # Display results
                for i, team in enumerate(teams, 1):
                    with st.expander(f"Team #{i} | Score: {team['total']} | Credits: {team['credits']}"):
                        st.markdown(f"**Captain:** {team['captain']} | **Vice Captain:** {team['vc']}")
                        
                        # Create display dataframe
                        display_df = pd.DataFrame([{
                            "Player": p["name"],
                            "Role": p["role"],
                            "Team": p["team"],
                            "Credits": p["credits"],
                            "Score": round(p["pitch_score"], 1)
                        } for p in team["players"]])
                        
                        st.dataframe(
                            display_df.sort_values("Score", ascending=False),
                            hide_index=True,
                            use_container_width=True
                        )
    
    except Exception as e:
        st.error(f"🚨 Error: {str(e)}")
        st.stop()

if __name__ == "__main__":
    main()
