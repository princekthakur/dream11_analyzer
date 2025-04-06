import pandas as pd
from itertools import combinations
import tkinter as tk
from tkinter import filedialog

# ----------------------------
# 1. FILE UPLOADER FUNCTION
# ----------------------------
def upload_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    return file_path

# ----------------------------
# 2. DATA PROCESSING
# ----------------------------
def process_data(file_path):
    df = pd.read_excel(file_path)
    players = []
    
    for _, row in df.iterrows():
        players.append({
            "name": row["Player Name"],
            "role": classify_role(row["Role"]),
            "is_captain": row["Captain"] == "Yes",
            "is_wicketkeeper": row["Wicketkeeper"] == "Yes",
            "is_impact": row["Impact Player"] == "Yes",
            "team": row["Team"],
            # Mock performance data (replace with real stats if available)
            "bat_avg": 35 if "Batter" in row["Role"] else 15,
            "strike_rate": 130 if "Batter" in row["Role"] else 100,
            "bowl_avg": 20 if "Bowler" in row["Role"] else 30,
            "credits": assign_credits(row["Role"])
        })
    return players

def classify_role(role_str):
    """Convert role string to standardized categories"""
    if "Wicketkeeper" in role_str: return "WK"
    elif "Batter" in role_str: return "BAT"
    elif "Bowler" in role_str: return "BOWL"
    elif "All-rounder" in role_str: return "AR"
    return "UNK"

def assign_credits(role_str):
    """Dynamic credit assignment based on role"""
    if "All-rounder" in role_str: return 9.0
    elif "Batter" in role_str: return 8.5
    elif "Bowler" in role_str: return 8.0
    return 7.5

# ----------------------------
# 3. PITCH ADJUSTMENT LOGIC
# ----------------------------
def apply_pitch_effects(players, pitch_type="neutral"):
    """Modify player scores based on pitch conditions"""
    multipliers = {
        "batting": {"BAT": 1.2, "AR": 1.1, "BOWL": 0.8},
        "bowling": {"BOWL": 1.3, "AR": 1.1, "BAT": 0.7},
        "neutral": {"BAT": 1.0, "BOWL": 1.0, "AR": 1.0}
    }
    
    for player in players:
        role = player["role"]
        if pitch_type == "batting":
            player["score"] *= multipliers["batting"].get(role, 1.0)
        elif pitch_type == "bowling":
            player["score"] *= multipliers["bowling"].get(role, 1.0)

# ----------------------------
# 4. PLAYER SCORING SYSTEM
# ----------------------------
def calculate_scores(players):
    """Comprehensive performance scoring"""
    for player in players:
        # Base score
        bat_score = (player["bat_avg"] * 0.5) + (player["strike_rate"] * 0.3)
        bowl_score = (25 - player["bowl_avg"]) * 0.6  # Lower avg = better
        
        # Role-specific weighting
        if player["role"] == "BAT":
            player["score"] = bat_score * 1.3
        elif player["role"] == "BOWL":
            player["score"] = bowl_score * 1.4
        else:  # AR/WK
            player["score"] = (bat_score * 0.7) + (bowl_score * 0.7)
        
        # Captaincy boost (handled later)
        player["base_score"] = player["score"]

# ----------------------------
# 5. TEAM OPTIMIZATION ENGINE
# ----------------------------
def optimize_team(players, pitch_type="neutral"):
    # Apply pitch effects first
    apply_pitch_effects(players, pitch_type)
    
    valid_teams = []
    all_combos = combinations(players, 11)
    
    for team in all_combos:
        # Check basic constraints
        if sum(p["credits"] for p in team) > 100:
            continue
            
        # Role balance check
        role_counts = {"WK": 0, "BAT": 0, "BOWL": 0, "AR": 0}
        for p in team:
            role_counts[p["role"]] += 1
            
        if not (role_counts["WK"] >= 1 and 3 <= role_counts["BAT"] <= 5 and 
                3 <= role_counts["BOWL"] <= 5 and 1 <= role_counts["AR"] <= 4):
            continue
            
        # Calculate team score (top 2 players as C/VC)
        sorted_team = sorted(team, key=lambda x: x["score"], reverse=True)
        total_score = sum(p["score"] for p in team)
        total_score += sorted_team[0]["score"] * 1.5  # Captain (1.5x)
        total_score += sorted_team[1]["score"] * 1.25  # Vice-captain (1.25x)
        
        valid_teams.append({
            "players": team,
            "total_score": total_score,
            "captain": sorted_team[0],
            "vice_captain": sorted_team[1]
        })
    
    # Return top 3 teams
    return sorted(valid_teams, key=lambda x: x["total_score"], reverse=True)[:3]

# ----------------------------
# 6. DIFFERENTIAL PLAYER ID
# ----------------------------
def identify_differentials(players, top_teams):
    """Find low-ownership high-value players"""
    # Get players not in top suggested teams
    common_players = set()
    for team in top_teams:
        common_players.update(p["name"] for p in team["players"])
    
    differentials = [p for p in players if p["name"] not in common_players]
    
    # Sort by value (score/credit ratio)
    return sorted(differentials, key=lambda x: x["score"]/x["credits"], reverse=True)[:5]

# ----------------------------
# 7. MAIN EXECUTION
# ----------------------------
if __name__ == "__main__":
    # Step 1: Upload file
    print("Please upload the Playing XI Excel file...")
    file_path = upload_file()
    
    # Step 2: Process data
    players = process_data(file_path)
    calculate_scores(players)
    
    # Step 3: Get user inputs
    pitch_type = input("Enter pitch type (batting/bowling/neutral): ").lower()
    contest_type = input("Enter contest type (small/grand): ").lower()
    
    # Step 4: Optimize teams
    top_teams = optimize_team(players, pitch_type)
    
    # Step 5: Display results
    print("\n=== TOP 3 DREAM11 TEAMS ===")
    for i, team in enumerate(top_teams, 1):
        print(f"\nTeam #{i} | Total Score: {team['total_score']:.2f}")
        print(f"Captain: {team['captain']['name']} | VC: {team['vice_captain']['name']}")
        for player in sorted(team["players"], key=lambda x: x["role"]):
            print(f"{player['role']:4} | {player['name']:20} | Score: {player['score']:.1f} | Credits: {player['credits']}")
    
    # Step 6: Show differential picks
    differentials = identify_differentials(players, top_teams)
    print("\n=== TOP 5 DIFFERENTIAL PICKS ===")
    for p in differentials:
        print(f"{p['role']:4} | {p['name']:20} | Value: {p['score']/p['credits']:.2f}")

    # Save results for next time
    pd.DataFrame(players).to_csv("player_database.csv", index=False)
    print("\nPlayer database saved for future reference!")
