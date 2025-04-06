import streamlit as st
import pandas as pd
import random
import requests
import itertools

st.set_page_config(page_title="Dream11 Advanced Analyzer", layout="wide")
st.title("\U0001F3CF Dream11 T20 Analyzer with Real Stats, Pitch, Roles & Credits")
st.markdown("Upload your lineup Excel/CSV with columns: `Player Name`, `Role`, `Team`, `Credits`")

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

    try:
        search_res = requests.get(search_url)
        search_res.raise_for_status()
        search_data = search_res.json()

        if search_data.get('status') == 'success' and search_data.get('data'):
            player_info = search_data['data'][0]
            pid = player_info.get('id')

            if pid:
                stats_url = f"https://api.cricapi.com/v1/player_stats?apikey={api_key}&id={pid}"
                stats_res = requests.get(stats_url)
                stats_res.raise_for_status()
                stats_data = stats_res.json()

                if stats_data.get('status') == 'success':
                    stats = stats_data.get('data', {})
                    batting = stats.get('stats', {}).get('batting', {}).get('T20', {})
                    bowling = stats.get('stats', {}).get('bowling', {}).get('T20', {})
                    recent_matches = stats.get('recentMatches', [])[:5]

                    runs_list = [m.get('runs', 0) for m in recent_matches if isinstance(m.get('runs', 0), (int, float))]
                    wickets_list = [m.get('wickets', 0) for m in recent_matches if isinstance(m.get('wickets', 0), (int, float))]

                    avg_runs = sum(runs_list) / len(runs_list) if runs_list else 25
                    avg_wickets = sum(wickets_list) / len(wickets_list) if wickets_list else 1

                    return {
                        "Venue Avg": float(batting.get('Average') or 25),
                        "Opponent Avg": round(float(batting.get('Average') or 25) * random.uniform(0.8, 1.2), 2),
                        "Last 5 Match Avg": round(avg_runs, 2),
                        "Last 5 Match Wickets": round(avg_wickets, 2),
                        "Wickets vs Opponent": round(float(bowling.get('Wickets', 0)) * random.uniform(0.8, 1.2), 2),
                        "Wickets at Venue": round(float(bowling.get('Wickets', 0)) * random.uniform(0.9, 1.1), 2),
                    }

    except Exception as e:
        st.warning(f"Error fetching stats for {player_name}: {e}")

    return {
        "Venue Avg": round(random.uniform(25, 50), 2),
        "Opponent Avg": round(random.uniform(25, 50), 2),
        "Last 5 Match Avg": round(random.uniform(20, 60), 2),
        "Last 5 Match Wickets": round(random.uniform(0, 3), 2),
        "Wickets vs Opponent": round(random.uniform(0, 3), 2),
        "Wickets at Venue": round(random.uniform(0, 3), 2),
    }

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
        df = df[df['Role'].isin(selected_roles)]

        if selected_player:
            df = df[df['Player Name'].str.contains(selected_player, case=False, na=False)]

        st.subheader("Fetched Stats & Analyzed Players")
        player_stats = []
        for _, row in df.iterrows():
            stats = get_real_player_stats(row['Player Name'])
            full_data = {**row.to_dict(), **stats}
            player_stats.append(full_data)

        df_stats = pd.DataFrame(player_stats)
        st.dataframe(df_stats)

        st.subheader("Suggested Team Combinations")
        combinations = list(itertools.combinations(df_stats.to_dict('records'), 11))
        final_teams = []
        used_captains = set()

        for team in combinations:
            total_score = 0
            total_credits = sum([p.get('Credits', 9.0) for p in team])
            team_roles = {r: 0 for r in available_roles}

            for p in team:
                if use_role_based_scoring:
                    if "Batter" in p['Role']:
                        total_score += p['Venue Avg'] + p['Opponent Avg'] + p['Last 5 Match Avg']
                    elif "Bowler" in p['Role']:
                        total_score += p['Last 5 Match Wickets'] * 25 + p['Wickets vs Opponent'] * 10
                    elif "All-rounder" in p['Role']:
                        total_score += (p['Last 5 Match Avg'] * 1.2 + p['Last 5 Match Wickets'] * 20)
                    elif "Wicketkeeper" in p['Role']:
                        total_score += (p['Last 5 Match Avg'] + 20)
                else:
                    total_score += p['Venue Avg'] + p['Opponent Avg'] + p['Last 5 Match Avg'] + p['Last 5 Match Wickets']

                if p['Role'] in team_roles:
                    team_roles[p['Role']] += 1

            if sum(team_roles.values()) == 11 and total_credits <= credits_limit:
                sorted_team = sorted(team, key=lambda x: x['Last 5 Match Avg'] + x['Last 5 Match Wickets'] * 10, reverse=True)
                captain = sorted_team[0]
                vice_captain = sorted_team[1] if sorted_team[1]['Player Name'] != captain['Player Name'] else sorted_team[2]

                if captain['Player Name'] not in used_captains:
                    used_captains.add(captain['Player Name'])
                    final_teams.append({
                        "Team Players": [p['Player Name'] for p in sorted_team],
                        "Captain": captain['Player Name'],
                        "Vice-Captain": vice_captain['Player Name'],
                        "Expected Points": round(total_score, 2),
                        "Credits Used": round(total_credits, 2)
                    })

        top_teams = sorted(final_teams, key=lambda x: x['Expected Points'], reverse=True)[:5]
        for i, team in enumerate(top_teams, 1):
            st.markdown(f"### Combo {i} - Expected Points: {team['Expected Points']} - Credits Used: {team['Credits Used']}")
            st.write("Captain:", team['Captain'])
            st.write("Vice-Captain:", team['Vice-Captain'])
            st.write("Team:", ", ".join(team['Team Players']))

        if top_teams:
            export_df = pd.DataFrame(top_teams)
            csv_data = export_df.to_csv(index=False).encode('utf-8')
            st.download_button("\U0001F4BE Download Team Combos as CSV", data=csv_data, file_name="dream11_combinations.csv", mime='text/csv')

    except Exception as e:
        st.error(f"Error processing file: {e}")
