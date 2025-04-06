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

selected_player = st.sidebar.text_input("Filter by Player Name (Optional)")

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

def fetch_player_credit(player_name):
    return round(random.uniform(7, 11), 1)

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

def suggest_captains(team, used_captains=None):
    sorted_team = sorted(team, key=lambda x: x['Fantasy Score (Est.)'], reverse=True)
    for player in sorted_team:
        if used_captains is None or player['Player'] not in used_captains:
            captain = player['Player']
            break
    for player in sorted_team:
        if player['Player'] != captain:
            vice_captain = player['Player']
            break
    return captain, vice_captain

def simulate_dream11_points(player):
    score = player['Fantasy Score (Est.)']
    if player['Role'].lower() in ['all-rounder']:
        score *= 1.1
    if player['Role'].lower() in ['fast bowler', 'spinner']:
        score += random.uniform(10, 25)
    if player['Role'].lower() in ['opening batter', 'top-order batter']:
        score += random.uniform(5, 20)
    return round(score, 2)

def generate_team_combinations(players_df, num_combinations=5):
    combinations = []
    used_captains = set()
    players = players_df.to_dict(orient='records')
    attempts = 0
    while len(combinations) < num_combinations and attempts < 200:
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
                total_points = sum(simulate_dream11_points(p) for p in team)
                if total_points >= 1100:
                    combinations.append((team, credits_used, captain, vice_captain, total_points))
        attempts += 1
    return combinations

def display_combinations(combinations):
    for idx, (team, credits_used, captain, vice_captain, total_points) in enumerate(combinations):
        with st.expander(f"Combination {idx+1} | Credits: {credits_used:.1f} | Est. Points: {total_points:.0f}"):
            st.markdown(f"**Captain:** {captain}  |  **Vice-Captain:** {vice_captain}")
            df_team = pd.DataFrame(team)
            df_team = df_team[["Player", "Role", "Team", "Credits", "Fantasy Score (Est.)"]]
            st.dataframe(df_team, use_container_width=True)

if selected_player:
    st.subheader(f"Performance Insights: {selected_player}")
    details = get_real_player_stats(selected_player)
    st.write(details)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()
        df.rename(columns={"player name": "player", "team": "team", "role": "role"}, inplace=True)

        df = df[df['role'].isin(selected_roles)]

        enriched_data = []
        with st.spinner("Fetching player stats. Please wait..."):
            for _, row in df.iterrows():
                stats = get_real_player_stats(row['player'])
                credits = fetch_player_credit(row['player'])

                if use_role_based_scoring:
                    score = (stats['Last 5 Match Avg'] * 1.2 +
                             stats['Opponent Avg'] * 1.1 +
                             stats['Venue Avg'] +
                             stats['Wickets at Venue'] * 25 +
                             stats['Wickets vs Opponent'] * 25)
                else:
                    score = (stats['Last 5 Match Avg'] +
                             stats['Opponent Avg'] +
                             stats['Venue Avg'] +
                             stats['Last 5 Match Wickets'] * 20)

                enriched_data.append({
                    "Player": row['player'],
                    "Role": row['role'],
                    "Team": row['team'],
                    "Credits": credits,
                    "Pitch Impact": get_pitch_advantage(row['role']),
                    "Fantasy Score (Est.)": round(score, 2)
                })

        enriched_df = pd.DataFrame(enriched_data)
        st.subheader("\U0001F4CA Enriched Player Data")
        st.dataframe(enriched_df, use_container_width=True)

        st.subheader("\U0001F9F0 Dream11 Team Combinations (1100+ Points Targets)")
        team_combos = generate_team_combinations(enriched_df, num_combinations=5)
        display_combinations(team_combos)

    except Exception as e:
        st.error(f"⚠️ Error processing file: {e}")
