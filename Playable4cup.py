# Generated from: Playable4cup.ipynb
# Converted at: 2026-02-12T18:49:52.732Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

# <a href="https://colab.research.google.com/github/Corncake00/4-Cup-Matching-Algorithm/blob/main/Playable4cup.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>


import streamlit as st
import random
import pandas as pd

# Setup page config
st.set_page_config(page_title="Cup Matching Game", page_icon="cup_with_straw")

# Initialize session state for tracking attempts and the ball position
if 'ball_pos' not in st.session_state:
    st.session_state.ball_pos = random.randint(1, 4)
if 'attempts' not in st.session_state:
    st.session_state.attempts = 0
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

def record_data(attempts):
    # This is where you'd connect to a Google Sheet or Database
    # For now, it prints to your console
    print(f"Game logged: {attempts} attempts")

st.title("🥤 The 4-Cup Matching Game")
st.write("The ball is hidden under one of the four cups. Can you find it?")

# Create four columns for the cups
cols = st.columns(4)

for i in range(1, 5):
    with cols[i-1]:
        if st.button(f"Cup {i}", disabled=st.session_state.game_over):
            st.session_state.attempts += 1
            if i == st.session_state.ball_pos:
                st.success(f"Found it! 🎯")
                st.session_state.game_over = True
                record_data(st.session_state.attempts)
            else:
                st.error("Empty!")

# Results and Reset
if st.session_state.game_over:
    st.write(f"### Total Attempts: {st.session_state.attempts}")
    if st.button("Play Again"):
        st.session_state.ball_pos = random.randint(1, 4)
        st.session_state.attempts = 0
        st.session_state.game_over = False
        st.rerun()