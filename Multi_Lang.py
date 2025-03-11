import streamlit as st
import json
import os
import asyncio
from datetime import datetime, timedelta
from googletrans import Translator

translator = Translator()

# Available languages
LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de"
}

# Generate a unique filename for each session
if "chat_file" not in st.session_state:
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.chat_file = f"chat_history_{session_id}.json"

# Load JSON data
def load_json():
    with open("temp_data.json", "r") as file:
        return json.load(file)

json_data = load_json()

# Save chat history
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

# Function to translate text (async handling)
async def async_translate(text, target_lang):
    if target_lang == "en":  
        return text  
    try:
        translated = await translator.translate(text, dest=target_lang)
        return translated.text
    except Exception:
        return text  # Return original if translation fails

# Helper function to run async code in Streamlit
def translate_text(text, target_lang):
    return asyncio.run(async_translate(text, target_lang))

# Chatbot UI
def chatbot():
    st.title("Bizowl Chatbot")

    # Language selection (only once)
    if "language" not in st.session_state:
        chosen_lang = st.selectbox("Choose a language:", list(LANGUAGES.keys()))
        if st.button("Confirm Language"):
            st.session_state.language = LANGUAGES[chosen_lang]
            st.session_state.history = []
            st.session_state.current_node = json_data["menu"]["greeting"]
            st.session_state.display_questions = set()
            st.session_state.scheduled_call = None
            st.session_state.call_scheduled_once = False  
            st.rerun()
        return  

    target_lang = st.session_state.language

    # Display chat history (translated)
    for entry in st.session_state.history:
        if "**You:**" in entry:
            st.markdown(f"**You:** {translate_text(entry.replace('**You:** ', ''), target_lang)}")
        else:
            st.markdown(f"**Bizowl:** {translate_text(entry.replace('**Bizowl:** ', ''), target_lang)}")

    # Display chatbot question (translated)
    question_text = st.session_state.current_node["message"]
    translated_question = translate_text(question_text, target_lang)

    if question_text not in st.session_state.display_questions:
        st.session_state.display_questions.add(question_text)
        st.session_state.history.append(f"**Bizowl:** {translated_question}")  
        save_chat_history()
        st.rerun()

    # Show scheduled call message (translated)
    if st.session_state.scheduled_call and not st.session_state.call_scheduled_once:
        translated_message = translate_text(st.session_state.scheduled_call, target_lang)
        st.session_state.history.append(f"**Bizowl:** {translated_message}")
        st.session_state.call_scheduled_once = True  
        save_chat_history()
        st.rerun()

    # Show translated options
    if st.session_state.current_node["options"]:
        for option in st.session_state.current_node["options"]:
            translated_option = translate_text(option, target_lang)
            if st.button(translated_option, key=option):
                st.session_state.history.append(f"**You:** {translated_option}")

                if option == "Schedule a Call" and not st.session_state.scheduled_call:
                    scheduled_time = datetime.now() + timedelta(minutes=15)
                    formatted_time = scheduled_time.strftime("%I:%M %p")
                    st.session_state.scheduled_call = f"Your call is scheduled for {formatted_time}"

                else:
                    st.session_state.current_node = st.session_state.current_node["options"][option]
                    new_question = st.session_state.current_node["message"]
                    translated_new_question = translate_text(new_question, target_lang)

                    if new_question not in st.session_state.display_questions:
                        st.session_state.display_questions.add(new_question)
                        st.session_state.history.append(f"**Bizowl:** {translated_new_question}")

                save_chat_history()
                st.rerun()

chatbot()
