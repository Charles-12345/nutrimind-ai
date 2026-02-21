"""
session.py
Initialises Streamlit session_state with default values.
"""
import streamlit as st


def init_session():
    """Call once at app startup to set defaults."""
    defaults = {
        "profile": {
            "name":     "Friend",
            "age":      25,
            "weight":   70,
            "height":   170,
            "goal":     "Maintenance",
            "activity": "Lightly Active",
        },
        "food_log":    [],   # list of meal dicts
        "weight_log":  [],   # list of {date, weight}
        "hf_token":    "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
