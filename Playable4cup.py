import streamlit as st
import random
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Setup page config
st.set_page_config(page_title="Sequence Matcher", page_icon="🧩")

# Establish connection
# Ensure your secrets.toml has [connections.gsheets]
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INITIALIZE GAME STATE ---
if 'target' not in st.session_state:
    letters = ['A', 'B', 'C', 'D']
    target = letters.copy()
    random.shuffle(target)
    st.session_state.target = target
    st.session_state.attempts = 0
    st.session_state.history = []
    st.session_state.game_over = False
    st.session_state.data_sent = False  # To ensure we only record once per win

def check_guess(guess):
    """Calculates how many items are in the correct position."""
    return sum(1 for g, t in zip(guess, st.session_state.target) if g == t)

# UI Header
st.title("🧩 Sequence Matching Game")
st.write("I have shuffled the letters **A, B, C, and D**. Can you guess the correct order?")

with st.sidebar:
    st.header("Settings")
    if st.button("Reset Game"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- GAME LOGIC ---
if not st.session_state.game_over:
    cols = st.columns(4)
    choice_1 = cols[0].selectbox("Pos 1", ['A', 'B', 'C', 'D'], key="p1")
    choice_2 = cols[1].selectbox("Pos 2", ['A', 'B', 'C', 'D'], key="p2", index=1)
    choice_3 = cols[2].selectbox("Pos 3", ['A', 'B', 'C', 'D'], key="p3", index=2)
    choice_4 = cols[3].selectbox("Pos 4", ['A', 'B', 'C', 'D'], key="p4", index=3)

    current_guess = [choice_1, choice_2, choice_3, choice_4]

    if st.button("Submit Guess", use_container_width=True):
        if len(set(current_guess)) < 4:
            st.warning("Please use each letter (A, B, C, D) exactly once!")
        else:
            st.session_state.attempts += 1
            correct_count = check_guess(current_guess)
            
            st.session_state.history.insert(0, {
                "Attempt": st.session_state.attempts,
                "Guess": " ".join(current_guess),
                "Correct Positions": correct_count
            })

            if correct_count == 4:
                st.session_state.game_over = True
                st.balloons()

# --- DATA RECORDING ---
if st.session_state.game_over:
    st.success(f"Perfect! You solved it in {st.session_state.attempts} attempts.")

    # Record data to Google Sheets automatically upon winning
    if not st.session_state.data_sent:
        try:
            # Create the row to add to your sheet
            new_entry = pd.DataFrame([{
                "Attempts": st.session_state.attempts,
                "Completion_Time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }])

            # This appends the new_entry to your existing Google Sheet
            conn.create(data=new_entry) 
            
            st.session_state.data_sent = True
            st.info("Results autonomously recorded to Google Sheet.")
        except Exception as e:
            st.error(f"Data recording failed: {e}")
