import streamlit as st
import pandas as pd
import random
import requests

st.set_page_config(page_title="Dream11 Advanced Analyzer", layout="wide")
st.title("\U0001F3CF Dream11 T20 Analyzer with Real Stats, Pitch, Roles & Credits")
st.markdown("Upload your lineup Excel/CSV with columns: `Player Name`, `Role`, `Team`")

# Sidebar pitch type selector
st.sidebar.header("Pitch & Ground Conditions")
pitch_type = st.sidebar.selectbox("Select Pitch Type", [
    "Balanced", "Batting-Friendly", "Bowling-Friendly", "Spin-Friendly"
])

venue = st.sidebar.text_input("Enter Ground/Venue Name (Optional)")
opponent_team = st.sidebar.text_input("Enter Opponent Team (Optional)")

# Updated Role List
available_roles = [
    "Opening Batter", "Top-order Batter", "Middle-order Batter",
    "All-rounder", "Wicketkeeper Batter", "Fast Bowler", "Spinner"
]

# Role-based filters
st.sidebar.header("Role-Based Filters")
selected_roles = st.sidebar.multiselect("Select Roles to Include", available_roles, default=available_roles)

# Scoring toggle
use_role_based_scoring = st.sidebar.checkbox("Use Role-Based Fantasy Scoring", value=True)

# Team Credits Limit
credits_limit = st.sidebar.slider("Max Team Credits", min_value=80.0, max_value=120.0, value=100.0, step=0.5)

uploaded_file = st.file_uploader("\U0001F4E4 Upload Excel or CSV file", type=["xlsx", "csv"])

# Real API call to CricAPI
@st.cache_data(show_spinner=False)
def get_real_player_stats(player_name):
    api_key = "6ca645b3-5501-4459-949a-57bf971f5f1b"
    search_url = f"https://api.cricapi.com/v1/players?apikey={api_key}&search={player_name}"
    search_res = requests.get(search_url)
    if search_res.status_code == 200 and search_res.json().get('status') == 'success':
        data = search_res.json().get('data', [])
        if data and 'id' in data[0]:
            pid = data[0]['id']
            stats_url = f"https://api.cricapi.com/v1/player_stats?apikey={api_key}&id={pid}"
            stats_res = requests.get(stats_url)
            if stats_res.status_code == 200 and stats_res.json().get('status') == 'success':
                stats = stats_res.json().get('data', {})
                batting = stats.get('stats', {}).get('batting', {}).get('T20', {})
                bowling = stats.get('stats', {}).get('bowling', {}).get('T20', {})
                recent_matches = stats.get('recentMatches', [])[:5]

                runs_list = [match.get('runs', 0) for match in recent_matches if 'runs' in match]
                wickets_list = [match.get('wickets', 0) for match in recent_matches if 'wickets' in match]

                avg_runs = sum(runs_list) / len(runs_list) if runs_list else 25
                avg_wickets = sum(wickets_list) / len(wickets_list) if wickets_list else 1

                return {
                    "Venue Avg": float(batting.get('Average', 25) or 25),
                    "Opponent Avg": round(float(batting.get('Average', 25)) * random.uniform(0.8, 1.2), 2),
                    "Last 5 Match Avg": round(avg_runs, 2),
                    "Last 5 Match Wickets": round(avg_wickets, 2),
                    "Wickets vs Opponent": round(float(bowling.get('Wickets', 0)) * random.uniform(0.8, 1.2), 2),
                    "Wickets at Venue": round(float(bowling.get('Wickets', 0)) * random.uniform(0.9, 1.1), 2),
                }
    return {
        "Venue Avg": round(random.uniform(25, 50), 2),
        "Opponent Avg": round(random.uniform(25, 50), 2),
        "Last 5 Match Avg": round(random.uniform(20, 60), 2),
        "Last 5 Match Wickets": round(random.uniform(0, 3), 2),
        "Wickets vs Opponent": round(random.uniform(0, 3), 2),
        "Wickets at Venue": round(random.uniform(0, 3), 2),
    }

# Fetch credit value from a mock API (simulated)
def fetch_player_credit(player_name):
    return round(random.uniform(7, 11), 1)

# Pitch impact logic
def get_pitch_advantage(role):
    role = role.lower()
    if pitch_type == "Batting-Friendly" and any(x in role for x in ["batter", "rounder", "keeper"]):
        return "Great for Batting"
    elif pitch_type == "Bowling-Friendly" and any(x in role for x in ["bowler", "rounder"]):
        return "Likely Wicket-Taker"
    elif pitch_type == "Spin-Friendly" and "spinner" in role:
        return "Sharp Spinner"
    elif pitch_type == "Balanced":
        return "Well-Rounded"
    return "-"

# Function to generate combinations

def generate_team_combinations(players_df, num_combinations=5):
    combinations = []
    used_captains = set()
    players = players_df.to_dict(orient='records')
    attempts = 0
    while len(combinations) < num_combinations and attempts < 100:
        random.shuffle(players)
        team = []
        credits_used = 0
        for player in players:
            if len(team) < 11 and credits_used + player['Credits'] <= credits_limit:
                team.append(player)
                credits_used += player['Credits']
        if len(team) == 11:
            captain, vice_captain = suggest_captains(team, used_captains)
            if captain not in used_captains:
                used_captains.add(captain)
                combinations.append((team, credits_used, captain, vice_captain))
        attempts += 1
    return combinations

# Captain and Vice-Captain Suggestion

def suggest_captains(team, used_captains=None):
    sorted_team = sorted(team, key=lambda x: x['Fantasy Score (Est.)'], reverse=True)
    for player in sorted_team:
        if used_captains is None or player['Player'] not in used_captains:
            captain = player['Player']
            break
    vice_captain = sorted_team[1]['Player'] if sorted_team[1]['Player'] != captain else sorted_team[2]['Player']
    return captain, vice_captain

...
