import streamlit as st
import pandas as pd
import random
import requests

st.set_page_config(page_title="Dream11 Advanced Analyzer", layout="wide")
st.title("🏏 Dream11 T20 Analyzer with Real Stats, Pitch, Roles & Credits")
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

# Team Credits Limit
credits_limit = st.sidebar.slider("Max Team Credits", min_value=80.0, max_value=120.0, value=100.0, step=0.5)

uploaded_file = st.file_uploader("📤 Upload Excel or CSV file", type=["xlsx", "csv"])

# Simulated API call for real stats
@st.cache_data(show_spinner=False)
def get_real_player_stats(player_name):
    # This should be replaced with a real API call
    return {
        "Venue Avg": round(random.uniform(25, 50), 2),
        "Opponent Avg": round(random.uniform(25, 50), 2),
        "Last 5 Match Avg": round(random.uniform(20, 60), 2),
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
    players = players_df.to_dict(orient='records')
    for _ in range(num_combinations):
        random.shuffle(players)
        team = []
        credits_used = 0
        for player in players:
            if len(team) < 11 and credits_used + player['Credits'] <= credits_limit:
                team.append(player)
                credits_used += player['Credits']
        combinations.append((team, credits_used))
    return combinations

# Captain and Vice-Captain Suggestion
def suggest_captains(team):
    sorted_team = sorted(team, key=lambda x: x['Impact Score'], reverse=True)
    captain = sorted_team[0]['Player']
    vice_captain = sorted_team[1]['Player']
    return captain, vice_captain

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        required_cols = {'Player Name', 'Role', 'Team'}
        if required_cols.issubset(df.columns):
            df['Player Name'] = df['Player Name'].astype(str).str.strip()
            df['Role'] = df['Role'].astype(str).str.strip()
            df['Team'] = df['Team'].astype(str).str.strip()

            st.success("✅ File loaded successfully!")
            st.markdown("### Raw Input Preview")
            st.dataframe(df, use_container_width=True)

            stats = []
            for _, row in df.iterrows():
                credit = fetch_player_credit(row['Player Name'])
                real_stats = get_real_player_stats(row['Player Name'])
                pitch_boost = get_pitch_advantage(row['Role'])

                impact = (
                    real_stats["Last 5 Match Avg"] * 0.4 +
                    real_stats["Wickets vs Opponent"] * 10 +
                    real_stats["Wickets at Venue"] * 5 +
                    real_stats["Venue Avg"] * 0.2 +
                    real_stats["Opponent Avg"] * 0.2
                )

                stats.append({
                    "Player": row['Player Name'],
                    "Team": row['Team'],
                    "Role": row['Role'],
                    "Credits": credit,
                    **real_stats,
                    "Impact Score": round(impact, 2),
                    "Pitch Advantage": pitch_boost
                })

            result_df = pd.DataFrame(stats)
            result_df = result_df[result_df["Role"].isin(selected_roles)]

            st.subheader(f"📊 Player Analysis (Pitch: {pitch_type})")
            st.dataframe(result_df.sort_values(by="Impact Score", ascending=False), use_container_width=True)

            st.subheader("🏆 Top 5 Team Combinations Within Credit Limit")
            team_combos = generate_team_combinations(result_df)

            for i, (team, credits_used) in enumerate(team_combos, 1):
                st.markdown(f"#### Combination #{i} (Total Credits: {credits_used:.2f})")
                combo_df = pd.DataFrame(team)
                captain, vice_captain = suggest_captains(team)

                st.write(f"⭐ **Captain:** {captain}")
                st.write(f"⭐ **Vice-Captain:** {vice_captain}")

                st.dataframe(combo_df.reset_index(drop=True), use_container_width=True)

                csv = combo_df.to_csv(index=False).encode('utf-8')
                st.download_button(f"📥 Download Combo #{i} as CSV", csv, f"Combo_{i}.csv", "text/csv")

        else:
            st.error("❌ Your file must contain columns: `Player Name`, `Role`, and `Team`.")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
