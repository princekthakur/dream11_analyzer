import streamlit as st
import pandas as pd
import numpy as np

def manual_input_form():
    """Streamlit form for manual data entry"""
    with st.form("player_form"):
        cols = st.columns(4)
        with cols[0]:
            name = st.text_input("Player Name")
        with cols[1]:
            role = st.selectbox("Role", ["BAT", "BOWL", "AR", "WK"])
        with cols[2]:
            team = st.selectbox("Team", ["SRH", "GT"])
        with cols[3]:
            credits = st.number_input("Credits", min_value=7.0, max_value=11.0, value=8.5)
        
        st.subheader("Performance Stats")
        stat_cols = st.columns(3)
        with stat_cols[0]:
            last5_avg = st.number_input("Bat Avg (Last 5)", min_value=0.0, value=35.0)
        with stat_cols[1]:
            sr = st.number_input("Strike Rate", min_value=0.0, value=135.0)
        with stat_cols[2]:
            last5_wickets = st.number_input("Wickets (Last 5)", min_value=0, value=3)
        
        economy = st.number_input("Economy Rate", min_value=0.0, value=7.5) if role in ["BOWL", "AR"] else 0.0
        
        if st.form_submit_button("Add Player"):
            return {
                "name": name,
                "role": role,
                "team": team,
                "credits": credits,
                "last5_avg": last5_avg,
                "sr": sr,
                "last5_wickets": last5_wickets,
                "economy": economy
            }
    return None

def main():
    st.title("📥 Dream11 Data Fetcher")
    
    # Input Method Selection
    input_method = st.radio("Select Input Method", 
                           ["CSV Upload", "Manual Entry"])
    
    players = {}
    
    if input_method == "CSV Upload":
        uploaded_file = st.file_uploader("Upload Player CSV", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df)
            players = df.set_index('name').to_dict(orient='index')
    
    else:  # Manual Entry
        st.warning("Enter players one by one")
        if 'player_list' not in st.session_state:
            st.session_state.player_list = []
            
        new_player = manual_input_form()
        if new_player:
            st.session_state.player_list.append(new_player)
        
        for i, player in enumerate(st.session_state.player_list):
            cols = st.columns([3,1,1,1,2])
            cols[0].write(player['name'])
            cols[1].write(player['role'])
            cols[2].write(player['team'])
            cols[3].write(f"{player['credits']:.1f}")
            if cols[4].button("❌", key=f"del_{i}"):
                st.session_state.player_list.pop(i)
                st.rerun()
        
        players = {p['name']: p for p in st.session_state.player_list}
    
    # Save functionality
    if players:
        if st.button("💾 Save Player Data"):
            pd.DataFrame.from_dict(players, orient='index').to_csv("today_players.csv")
            st.success("Saved to today_players.csv")

if __name__ == "__main__":
    main()
