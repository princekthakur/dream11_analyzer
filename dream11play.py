import streamlit as st
import pandas as pd
import random
import requests

st.set_page_config(page_title="Dream11 Advanced Analyzer", layout="wide")
st.title("\U0001F3CF Dream11 T20 Analyzer - Final XI Selector")

# Fixed playing XI data with Why Pick column
srh_players = [
    {"Player Name": "Travis Head", "Team": "SRH", "Role": "Opening Batter", "Why Pick": "Explosive starter, recent form"},
    {"Player Name": "Abhishek Sharma", "Team": "SRH", "Role": "Opening Batter", "Why Pick": "Powerplay damage potential"},
    {"Player Name": "Ishan Kishan", "Team": "SRH", "Role": "Wicketkeeper Batter", "Why Pick": "Impact + possible wicketkeeping points"},
    {"Player Name": "Nitish Kumar Reddy", "Team": "SRH", "Role": "Middle-order Batter", "Why Pick": "Stabilizer role in middle"},
    {"Player Name": "Kamindu Mendis", "Team": "SRH", "Role": "All-rounder", "Why Pick": "Differentiator pick"},
    {"Player Name": "Heinrich Klaasen", "Team": "SRH", "Role": "Wicketkeeper Batter", "Why Pick": "Reliable + 360 hitter"},
    {"Player Name": "Aniket Verma", "Team": "SRH", "Role": "Middle-order Batter", "Why Pick": "Low ownership value pick"},
    {"Player Name": "Pat Cummins", "Team": "SRH", "Role": "Fast Bowler", "Why Pick": "Wickets in powerplay/death"},
    {"Player Name": "Zeeshan Ansari", "Team": "SRH", "Role": "Spinner", "Why Pick": "Hidden pick for Grand League diff"},
    {"Player Name": "Jaydev Unadkat", "Team": "SRH", "Role": "Fast Bowler", "Why Pick": "Experienced death overs option"},
    {"Player Name": "Mohammed Shami", "Team": "SRH", "Role": "Fast Bowler", "Why Pick": "Powerplay/Death strike bowler"}
]

gt_players = [
    {"Player Name": "Sai Sudharsan", "Team": "GT", "Role": "Top-order Batter", "Why Pick": "Consistent scorer at #3"},
    {"Player Name": "Shubman Gill", "Team": "GT", "Role": "Opening Batter", "Why Pick": "Sheet anchor with big innings potential"},
    {"Player Name": "Jos Buttler", "Team": "GT", "Role": "Wicketkeeper Batter", "Why Pick": "Explosive impact player"},
    {"Player Name": "Shahrukh Khan", "Team": "GT", "Role": "Middle-order Batter", "Why Pick": "Quick scoring potential late"},
    {"Player Name": "Rahul Tewatia", "Team": "GT", "Role": "All-rounder", "Why Pick": "Finisher + surprise overs"},
    {"Player Name": "Washington Sundar", "Team": "GT", "Role": "All-rounder", "Why Pick": "Dual utility with spin and runs"},
    {"Player Name": "Rashid Khan", "Team": "GT", "Role": "Spinner", "Why Pick": "Wickets + economy + fielding"},
    {"Player Name": "Ravisrinivasan Sai Kishore", "Team": "GT", "Role": "Spinner", "Why Pick": "Spin-friendly pitch + value pick"},
    {"Player Name": "Mohammed Siraj", "Team": "GT", "Role": "Fast Bowler", "Why Pick": "Early breakthroughs"},
    {"Player Name": "Prasidh Krishna", "Team": "GT", "Role": "Fast Bowler", "Why Pick": "Death overs + bounce advantage"},
    {"Player Name": "Ishant Sharma", "Team": "GT", "Role": "Fast Bowler", "Why Pick": "Experienced pacer"}
]

combined_players = srh_players + gt_players

@st.cache_data(show_spinner=False)
def get_player_stats(player_name):
    api_key = "6ca645b3-5501-4459-949a-57bf971f5f1b"
    search_url = f"https://api.cricapi.com/v1/players?apikey={api_key}&search={player_name}"

    try:
        res = requests.get(search_url).json()
        if res.get('status') == 'success' and res.get('data'):
            pid = res['data'][0]['id']
            stats_url = f"https://api.cricapi.com/v1/player_stats?apikey={api_key}&id={pid}"
            stats = requests.get(stats_url).json()
            if stats.get('status') == 'success':
                recent = stats['data'].get('recentMatches', [])[:5]
                runs = [m.get('runs', 0) for m in recent if isinstance(m.get('runs', 0), (int, float))]
                wickets = [m.get('wickets', 0) for m in recent if isinstance(m.get('wickets', 0), (int, float))]

                return {
                    "Avg Runs": round(sum(runs)/len(runs), 2) if runs else 25,
                    "Avg Wickets": round(sum(wickets)/len(wickets), 2) if wickets else 1,
                    "Matches": len(recent)
                }
    except:
        pass

    return {"Avg Runs": round(random.uniform(20, 40), 2), "Avg Wickets": round(random.uniform(0, 2), 2), "Matches": 5}

# Fetch stats
st.subheader("Analyzing Confirmed Playing XI")
player_data = []
for player in combined_players:
    stats = get_player_stats(player['Player Name'])
    player_data.append({**player, **stats})

stats_df = pd.DataFrame(player_data)
st.dataframe(stats_df)

# Scoring logic
for p in player_data:
    if "Batter" in p['Role']:
        p['Score'] = p['Avg Runs'] * 1.1
    elif "Bowler" in p['Role']:
        p['Score'] = p['Avg Wickets'] * 25
    elif "All-rounder" in p['Role']:
        p['Score'] = p['Avg Runs'] * 0.7 + p['Avg Wickets'] * 20
    elif "Wicketkeeper" in p['Role']:
        p['Score'] = p['Avg Runs'] * 1.2 + 10
    else:
        p['Score'] = 30

sorted_team = sorted(player_data, key=lambda x: x['Score'], reverse=True)[:11]
captain = sorted_team[0]
vice_captain = next(p for p in sorted_team if p['Player Name'] != captain['Player Name'])

st.subheader("\U0001F451 Best Dream11 Team")
st.markdown(f"**Captain:** {captain['Player Name']} ({captain['Team']})")
st.markdown(f"**Vice-Captain:** {vice_captain['Player Name']} ({vice_captain['Team']})")
st.markdown("**Team:** " + ", ".join([p['Player Name'] for p in sorted_team]))

st.markdown(f"**Expected Points:** {round(sum(p['Score'] for p in sorted_team), 2)}")
