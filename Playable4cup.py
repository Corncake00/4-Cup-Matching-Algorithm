import streamlit as st
import random
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- PAGE CONFIG ---
st.set_page_config(page_title="4-Cup Matcher", page_icon="🥤")

# --- GOOGLE SHEETS CONNECTION ---
# 1. Initialize the connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Hardcode the URL here as a backup constant
SHEET_URL = "https://docs.google.com/spreadsheets/d/1l13XqlPBrBo9UfsKEWo0aoJ6s4knYdc4skyMXSqtHU4/edit#gid=0"

# --- INITIALIZE SESSION STATE ---
if 'secret' not in st.session_state:
    cups = ['a', 'b', 'c', 'd']
    st.session_state.secret = random.sample(cups, len(cups))
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.history = []
    st.session_state.recorded = False

# --- UI HEADER ---
st.title("🥤 4-Cup Matching Game")
st.write("I've hidden letters **a, b, c, and d** in a secret order. Can you find it?")

# --- SIDEBAR (Reset & Instructions) ---
with st.sidebar:
    st.header("Game Controls")
    if st.button("New Game / Reset"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.info("Enter a sequence like 'abcd' or 'dcba'.")

# --- GAMEPLAY AREA ---
if not st.session_state.game_over:
    user_input = st.text_input("Enter your 4-letter guess:", max_chars=4).lower().strip()
    
    if st.button("Submit Guess"):
        if len(user_input) != 4 or set(user_input) != {'a', 'b', 'c', 'd'}:
            st.error("Please enter exactly 4 letters: a, b, c, and d.")
        else:
            st.session_state.attempts += 1
            guess = list(user_input)
            
            # Logic: Check for matches
            correct_count = sum(1 for i in range(4) if guess[i] == st.session_state.secret[i])
            
            # Save to history for display
            st.session_state.history.insert(0, f"Guess: {user_input.upper()} | Result: {correct_count} correct")
            
            if correct_count == 4:
                st.session_state.game_over = True
                st.balloons()
            else:
                st.info(f"Result: {correct_count} correct. Keep going!")

# --- POST-GAME: DATA RECORDING ---
if st.session_state.game_over:
    st.success(f"🎯 Bullseye! You matched all 4 cups in {st.session_state.attempts} guesses.")
    
    if not st.session_state.recorded:
        # We use a form to prevent the page from refreshing and losing the name input
        with st.form("score_form"):
            player_name = st.text_input("Enter your name for the record:", value="Anonymous")
            submit_score = st.form_submit_button("Save Score")
            
            if submit_score:
                try:
                    # Explicitly passing the 'spreadsheet' parameter solves the "must be specified" error
                    existing_df = conn.read(spreadsheet=SHEET_URL)
                    
                    # Create the new row - Make sure your Sheet headers match these exactly!
                    new_row = pd.DataFrame([{
                        "Name": player_name,
                        "Attempts": int(st.session_state.attempts),
                        "Date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    }])
                    
                    # Combine with existing data (or just use new_row if sheet is empty)
                    if existing_df is not None and not existing_df.empty:
                        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                    else:
                        updated_df = new_row
                    
                    # Update the sheet - Explicitly passing the 'spreadsheet' here too
                    conn.update(spreadsheet=SHEET_URL, data=updated_df)
                    
                    st.session_state.recorded = True
                    st.success("Result saved to Google Sheets!")
                    st.rerun()
                    
                except Exception as e:
                    # This will catch and display the exact technical error
                    st.error(f"Save failed: {e}")
    else:
        st.info("Result has been recorded. Press 'New Game' to play again.")

# --- DISPLAY HISTORY ---
st.divider()
st.subheader("Current Game History")
if not st.session_state.history:
    st.write("No guesses yet.")
else:
    for entry in st.session_state.history:
        st.write(entry)

# --- RECENT RECORDS (Optional Display) ---
st.subheader("📊 Recent Attempts")
try:
    # Explicitly passing the URL again
    history_df = conn.read(spreadsheet=SHEET_URL)
    if not history_df.empty:
        st.dataframe(history_df.tail(5))
except:
    st.write("Connect to your Google Sheet to see all-time records.")
