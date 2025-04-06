import streamlit as st
import pandas as pd
import random
import requests

st.set_page_config(page_title="Dream11 Advanced Analyzer", layout="wide")
st.title("🏏 Dream11 T20 Analyzer with Pitch, Roles & Credits")
st.markdown("Upload your lineup Excel/CSV with columns: `Player Name`, `Role`, `Team`")

# Sidebar pitch type selector
st.sidebar.header("Pitch & Ground Conditions")
pitch_type = st.sidebar.selectbox("Select Pitch Type", [
    "Balanced", "Batting-Friendly", "Bowling-Friendly", "Spin-Friendly"
])

# Role-based filters
st.sidebar.header("Role-Based Filters")
selected_roles = st.sidebar.multiselect("Select Roles to Include", ["Batsman", "Bowler", "All-Rounder", "Wicketkeeper"], default=["Batsman", "Bowler", "All-Rounder", "Wicketkeeper"])

# Team Credits Limit
credits_limit = st.sidebar.slider("Max Team Credits", min_value=80.0, max_value=120.0, value=100.0, step=0.5)

uploaded_file = st.file_uploader("📤 Upload Excel or CSV file", type=["xlsx", "csv"])

# Fetch credit value from a mock API (simulated)
def fetch_player_credit(player_name):
    # Placeholder: simulate credit between 7 and 11
    return round(random.uniform(7, 11), 1)

# Simulate T20 stats per player
def generate_fake_stats(role):
    return {
        "Batting Avg": round(random.uniform(20, 60), 2) if role.lower() != "bowler" else round(random.uniform(5, 20), 2),
        "Wickets/Match": round(random.uniform(0, 3), 2) if role.lower() != "batsman" else 0,
        "Fielding": round(random.uniform(1, 10), 2),
    }

# Tag players with pitch-based advantage
def get_pitch_advantage(role):
    if pitch_type == "Batting-Friendly" and role.lower() in ["batsman", "wicketkeeper", "all-rounder"]:
        return "Great for Batting"
    elif pitch_type == "Bowling-Friendly" and role.lower() in ["bowler", "all-rounder"]:
        return "Likely Wicket-Taker"
    elif pitch_type == "Spin-Friendly" and role.lower() == "bowler":
        return "Sharp Spinner"
    elif pitch_type == "Balanced":
        return "Well-Rounded"
    return "-"

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        required_cols = {'Player Name', 'Role', 'Team'}
        if required_cols.issubset(df.columns):
            df['Player Name'] = df['Player Name'].astype(str)
            df['Role'] = df['Role'].astype(str)
            df['Team'] = df['Team'].astype(str)

            st.success("✅ File loaded successfully!")

            # Add stats and credits
            stats = []
            for _, row in df.iterrows():
                credit = fetch_player_credit(row['Player Name'])
                stat = generate_fake_stats(row['Role'])
                stats.append({
                    "Player": row['Player Name'],
                    "Team": row['Team'],
                    "Role": row['Role'],
                    "Credits": credit,
                    **stat
                })

            result_df = pd.DataFrame(stats)

            # Filter by selected roles
            result_df = result_df[result_df["Role"].isin(selected_roles)]

            result_df["Impact Score"] = (
                result_df["Batting Avg"] * 0.4 +
                result_df["Wickets/Match"] * 10 +
                result_df["Fielding"] * 2
            ).round(2)

            result_df["Pitch Advantage"] = result_df["Role"].apply(get_pitch_advantage)

            st.subheader(f"📊 Player Analysis (Pitch: {pitch_type})")
            st.dataframe(result_df.sort_values(by="Impact Score", ascending=False), use_container_width=True)

            st.subheader("🏆 Top 11 Recommendations Within Credit Limit")
            top_players = result_df.sort_values(by="Impact Score", ascending=False)

            selected_team = []
            total_credits = 0

            for _, player in top_players.iterrows():
                if len(selected_team) < 11 and (total_credits + player["Credits"]) <= credits_limit:
                    selected_team.append(player)
                    total_credits += player["Credits"]

            top11_df = pd.DataFrame(selected_team)
            st.markdown(f"**Total Credits Used:** {total_credits:.2f} / {credits_limit}")
            st.dataframe(top11_df.reset_index(drop=True), use_container_width=True)

            csv = top11_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Top XI as CSV", csv, "Top11_CreditsBased.csv", "text/csv")

        else:
            st.error("❌ Your file must contain columns: `Player Name`, `Role`, and `Team`.")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
