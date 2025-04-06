import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import streamlit as st

def load_data():
    """Loads player data with error handling"""
    try:
        df = pd.read_csv("today_players.csv", index_col=0)
        return df.to_dict(orient='index')
    except FileNotFoundError:
        st.error("No player data found. Run data_fetcher.py first!")
        st.stop()

def predict_team(players):
    """Prediction logic would go here"""
    st.write("## Optimal Team Prediction")
    st.dataframe(pd.DataFrame.from_dict(players, orient='index'))

def main():
    st.title("🎯 Dream11 Predictor")
    players = load_data()
    
    # Display loaded data
    with st.expander("View Player Data"):
        st.dataframe(pd.DataFrame.from_dict(players, orient='index'))
    
    # Prediction UI
    pitch = st.selectbox("Pitch Condition", ["Batting", "Bowling", "Neutral"])
    if st.button("Generate Dream11 Team"):
        predict_team(players)

if __name__ == "__main__":
    main()
