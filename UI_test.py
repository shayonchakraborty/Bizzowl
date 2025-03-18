import streamlit as st
import json
import os
from datetime import datetime, timedelta

# Generate a unique filename for each session (new file on each run)
if "chat_file" not in st.session_state:
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.chat_file = f"chat_history_{session_id}.json"

# Load JSON data for chatbot
def load_json():
    with open("temp_data.json", "r") as file:
        return json.load(file)

json_data = load_json()

# Save chat history to file (updates the same file during the session)
def save_chat_history():
    chat_data = []
    for i in range(1, len(st.session_state.history), 2):
        if i + 1 < len(st.session_state.history):
            chat_data.append({
                "question": st.session_state.history[i - 1].replace("**Bizowl:** ", ""),
                "option_chosen": st.session_state.history[i].replace("**You:** ", ""),
                "answer": st.session_state.history[i + 1].replace("**Bizowl:** ", "")
            })

    with open(st.session_state.chat_file, "w") as file:
        json.dump(chat_data, file, indent=4)

# Chatbot UI
def chatbot():
    st.markdown(
        """
        <style>
            .chat-container {
                max-width: 600px;
                margin: auto;
            }
            .user-message {
                text-align: right;
                margin: 5px;
                max-width: 70%;
                float: right;
                clear: both;
            }
            .bot-message {
                text-align: left;
                margin: 5px;
                max-width: 70%;
                float: left;
                clear: both;
            }
            .option-button {
                text-align: left;
                display: block;
                margin-bottom: 5px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Bizzowl Chatbot")
    
    if "history" not in st.session_state:
        st.session_state.history = []
        st.session_state.current_node = json_data["menu"]["greeting"]
        st.session_state.display_questions = set()
        st.session_state.scheduled_call = None
        st.session_state.call_scheduled_once = False  

    # Display chat history
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for entry in st.session_state.history:
        if "**You:**" in entry:
            st.markdown(f'<div class="user-message">{entry.replace("**You:** ", "")}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{entry.replace("**Bizowl:** ", "")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Handle chatbot question display
    question_text = st.session_state.current_node["message"]
    if question_text not in st.session_state.display_questions:
        st.session_state.display_questions.add(question_text)
        st.session_state.history.append(f"**Bizowl:** {question_text}")
        save_chat_history()
        st.rerun()

    # Display scheduled call message only once
    if st.session_state.scheduled_call and not st.session_state.call_scheduled_once:
        st.session_state.history.append(f"**Bizowl:** {st.session_state.scheduled_call}")
        st.session_state.call_scheduled_once = True  
        save_chat_history()
        st.rerun()

    # Display options aligned to the left
    if st.session_state.current_node["options"]:
        options = list(st.session_state.current_node["options"].keys())

        for option in options:
            if st.button(option, key=option, help="Click to proceed"):
                st.session_state.history.append(f"**You:** {option}")

                if option == "Schedule a Call" and not st.session_state.scheduled_call:
                    scheduled_time = datetime.now() + timedelta(minutes=15)
                    formatted_time = scheduled_time.strftime("%I:%M %p")
                    st.session_state.scheduled_call = f"Your call is scheduled for {formatted_time}"

                else:
                    st.session_state.current_node = st.session_state.current_node["options"][option]
                    new_question = st.session_state.current_node["message"]
                    if new_question not in st.session_state.display_questions:
                        st.session_state.display_questions.add(new_question)
                        st.session_state.history.append(f"**Bizowl:** {new_question}")

                save_chat_history()
                st.rerun()

chatbot()
