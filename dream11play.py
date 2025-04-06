import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations

# ----------------------------
# 1. DATA INPUT SECTION
# ----------------------------
def show_data_input():
    st.sidebar.header("📥 Input Method")
    input_method = st.sidebar.radio("Choose input:", 
                                  ["Demo Data", "Manual Entry", "CSV Upload"])

    players = {}
    
    if input_method == "Demo Data":
        players = {
            "Virat Kohli": {"team": "RCB", "role": "BAT", "credits": 10.5, "last5_avg": 52, "sr": 145},
            "Jasprit Bumrah": {"team": "MI", "role": "BOWL", "credits": 9.5, "last5_wickets": 8, "economy": 6.5}
        }
        st.success("Loaded demo data with 2 players")

    elif input_method == "Manual Entry":
        with st.form("player_form"):
            cols = st.columns(4)
            name = cols[0].text_input("Player Name")
            role = cols[1].selectbox("Role", ["BAT", "BOWL", "AR", "WK"])
            team = cols[2].selectbox("Team", ["SRH", "GT", "RCB", "MI", "CSK"])
            credits = cols[3].number_input("Credits", min_value=7.0, max_value=12.0, value=8.5)
            
            if role in ["BAT", "WK", "AR"]:
                last5_avg = st.number_input("Batting Avg (Last 5)", min_value=0.0, value=35.0)
                sr = st.number_input("Strike Rate", min_value=0.0, value=135.0)
            else:
                last5_avg, sr = 0, 0
                
            if role in ["BOWL", "AR"]:
                last5_wickets = st.number_input("Wickets (Last 5)", min_value=0, value=3)
                economy = st.number_input("Economy Rate", min_value=0.0, value=7.5)
            else:
                last5_wickets, economy = 0, 0
                
            if st.form_submit_button("Add Player"):
                players[name] = {
                    "team": team,
                    "role": role,
                    "credits": credits,
                    "last5_avg": last5_avg,
                    "sr": sr,
                    "last5_wickets": last5_wickets,
                    "economy": economy
                }
                st.rerun()

    elif input_method == "CSV Upload":
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            players = df.set_index('name').to_dict(orient='index')
    
    return players

# ----------------------------
# 2. PREDICTION ENGINE 
# ----------------------------
def show_prediction(players):
    if not players:
        st.warning("No player data! Add players first")
        return
    
    st.header("🎯 Dream11 Team Generator")
    
    # Prediction UI
    pitch = st.selectbox("Pitch Condition", ["Batting", "Bowling", "Neutral"])
    if st.button("Generate Team"):
        with st.spinner("Optimizing..."):
            # Mock prediction (replace with real logic)
            df = pd.DataFrame.from_dict(players, orient='index')
            st.dataframe(
                df.sort_values("credits", ascending=False),
                height=500
            )
            st.balloons()

# ----------------------------
# 3. MAIN APP FLOW
# ----------------------------
def main():
    st.set_page_config(layout="wide")
    
    # Get player data
    players = show_data_input()
    
    # Show prediction if data exists
    if players:
        show_prediction(players)

if __name__ == "__main__":
    main()
