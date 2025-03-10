import streamlit as st
import json

# Load chatbot menu JSON
try:
    with open("chatbot_menu.json", "r") as f:
        chatbot_data = json.load(f)
except FileNotFoundError:
    st.error("⚠️ chatbot_menu.json not found!")
    chatbot_data = {"menu": {}}

# Initialize session state for chatbot navigation
if "history" not in st.session_state:
    st.session_state.history = ["greeting"]
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

def get_current_menu(path):
    """Retrieve the current menu based on the path in session state."""
    menu = chatbot_data.get("menu", {})
    for key in path:
        menu = menu.get("options", {}).get(key, {})
    return menu

# Ensure chatbot starts with a valid menu
if "greeting" not in chatbot_data.get("menu", {}):
    st.error("⚠️ No valid starting point found in chatbot_menu.json.")
    st.stop()

# Streamlit UI
st.title("🤖 Bizowl Chatbot")
st.sidebar.header("Chatbot Navigation")

# Display breadcrumb navigation
st.sidebar.write("**Navigation Path:**")
breadcrumb = " > ".join(st.session_state.history)
st.sidebar.write(f"📍 {breadcrumb}")

# Get current menu options
current_menu = get_current_menu(st.session_state.history)
st.write(f"**{current_menu.get('message', 'How can I assist you?')}**")

# Display options
options = list(current_menu.get("options", {}).keys())

if options:  # Ensure there are actual options
    # Set correct default selection
    if st.session_state.selected_option not in options:
        st.session_state.selected_option = None  # Reset selection if invalid

    selected_option = st.radio("Choose an option:", options, key="selected_option")

    # Next button
    if st.button("Next"):
        if selected_option:
            st.session_state.history.append(selected_option)
            st.session_state.selected_option = None  # Reset for next selection
            st.rerun()
        else:
            st.warning("⚠️ Please select an option before proceeding.")

# Back button for navigation
if len(st.session_state.history) > 1:
    if st.button("⬅️ Back"):
        st.session_state.history.pop()
        st.session_state.selected_option = None  # Reset selection
        st.rerun()

# Restart conversation
if st.button("🔄 Restart"):
    st.session_state.history = ["greeting"]
    st.session_state.selected_option = None
    st.rerun()
