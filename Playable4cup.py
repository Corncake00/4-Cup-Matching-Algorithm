import streamlit as st
import random
from streamlit_gsheets import GSheetsConnection
import pandas as pd


# Setup page config
conn = st.connection("gsheets", type=GSheetsConnection)
st.set_page_config(page_title="Sequence Matcher", page_icon="🧩")

# --- INITIALIZE GAME STATE ---
if 'target' not in st.session_state:
    letters = ['A', 'B', 'C', 'D']
    target = letters.copy()
    random.shuffle(target)
    st.session_state.target = target
    st.session_state.attempts = 0
    st.session_state.history = []
    st.session_state.game_over = False

def check_guess(guess):
    """Calculates how many items are in the correct position."""
    return sum(1 for g, t in zip(guess, st.session_state.target) if g == t)

#UI
st.title("🧩 Sequence Matching Game")
st.write("I have shuffled the letters **A, B, C, and D**. Can you guess the correct order?")
with st.sidebar:
    st.header("How to Play")
    st.write("1. Arrange the letters in the dropdowns.")
    st.write("2. Click 'Submit Guess'.")
    st.write("3. Use the feedback to narrow down the order.")
    
    if st.button("Reset Game"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

#Logic
if not st.session_state.game_over:
    cols = st.columns(4)
    choice_1 = cols[0].selectbox("Pos 1", ['A', 'B', 'C', 'D'], key="p1")
    choice_2 = cols[1].selectbox("Pos 2", ['A', 'B', 'C', 'D'], key="p2", index=1)
    choice_3 = cols[2].selectbox("Pos 3", ['A', 'B', 'C', 'D'], key="p3", index=2)
    choice_4 = cols[3].selectbox("Pos 4", ['A', 'B', 'C', 'D'], key="p4", index=3)

    current_guess = [choice_1, choice_2, choice_3, choice_4]

    if st.button("Submit Guess", use_container_width=True):
        # Validation: Check for duplicates
        if len(set(current_guess)) < 4:
            st.warning("Please use each letter (A, B, C, D) exactly once!")
        else:
            st.session_state.attempts += 1
            correct_count = check_guess(current_guess)
            
            # Record result
            st.session_state.history.insert(0, {
                "Attempt": st.session_state.attempts,
                "Guess": " ".join(current_guess),
                "Correct Positions": correct_count
            })

            if correct_count == 4:
                st.session_state.game_over = True
                st.balloons()
                st.success(f"Perfect! You solved it in {st.session_state.attempts} attempts.")

#Data recording
if st.session_state.game_over:
    # Keep your current display code
    st.write(f"Total attempts: {st.session_state.attempts}")
    
    # ADD THIS: Prepare the data row
    new_entry = pd.DataFrame([{
        "User": "Anonymous", # You could add an input for their name
        "Attempts": st.session_state.attempts,
        "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

    # ADD THIS: Push to Google Sheets
    # Note: 'worksheet' is the name of the tab in your Sheet
    conn.create(data=new_entry) 
    st.success("Data recorded")

if st.button("Play Again", type="primary"):
    # Reset only the game-specific variables
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.ball_pos = random.randint(1, 4)
    st.session_state.history = [] # Clear the table for the next round
    st.rerun()

