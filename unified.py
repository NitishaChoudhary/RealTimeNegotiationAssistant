import time
import pyaudio
import wave
import speech_recognition as sr
from transformers import pipeline
from groq import Groq
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import re
import streamlit as st
import cohere

# Initialize APIs and clients
COHERE_API_KEY = "wnDl2gFhkWSgehGd193dsPfVMKIJlDaSooLiXJrp"
co = cohere.Client(COHERE_API_KEY)
client = Groq(api_key="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")
sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
summarizer = pipeline("summarization")

# Load datasets
laptop_data = pd.read_csv("C:\\Users\\choud\\Downloads\\laptop_dataset_updated.csv")
customer_history_path = "C:\\Users\\choud\\Downloads\\dataset_preparation - Sheet1.csv"
customer_history = pd.read_csv(customer_history_path)

# Google Sheets setup
def initialize_google_sheets(credentials_path):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    return gspread.authorize(credentials)

# Sentiment analysis
def analyze_sentiment(text):
    result = sentiment_analyzer(text)
    sentiment = result[0]["label"]
    return "Positive" if sentiment == "LABEL_2" else ("Neutral" if sentiment == "LABEL_1" else "Negative")

# Summarize conversation
def summarize_conversation(conversation):
    summary = summarizer(conversation, max_length=50, min_length=10, do_sample=False)
    return summary[0]['summary_text']

# Find customer row
def find_customer_row(sheet, customer_name):
    data = sheet.get_all_values()
    for index, row in enumerate(data):
        if row and row[0].strip().lower() == customer_name.strip().lower():
            return index + 1
    return None

# Add customer interaction
def append_customer_interaction(sheet, customer_name, interaction, summary, sentiment, deal_status):
    row_index = find_customer_row(sheet, customer_name)
    column_headers = sheet.row_values(1)

    if row_index:
        existing_row = sheet.row_values(row_index)
        num_interactions = (len(existing_row) - 1) // 4
        next_column_start = 2 + num_interactions * 4

        headers_to_add = [
            f"Interaction {num_interactions + 1}",
            f"Summary {num_interactions + 1}",
            f"Sentiment {num_interactions + 1}",
            f"Deal Status {num_interactions + 1}"
        ]

        for i, header in enumerate(headers_to_add):
            if len(column_headers) < next_column_start + i:
                sheet.update_cell(1, next_column_start + i, header)

        new_data = [interaction, summary, sentiment, deal_status]
        for i, value in enumerate(new_data):
            sheet.update_cell(row_index, next_column_start + i, value)
    else:
        new_row = [customer_name, interaction, summary, sentiment, deal_status]
        sheet.append_row(new_row)

# Generate LLM-based suggestions
def generate_llm_recommendations(user_input):
    # Generate LLM-based suggestions
    response = co.generate(
        model="command-xlarge",
        prompt=(
            "You are an assistant providing personalized laptop recommendations based on user preferences.\n\n"
            f"User Input: {user_input}\n\n"
            "Generate two concise, complete and helpful recommendations for laptops like this example:\n\n"
            "Example:\n"
            "- Brand & Model: Dell Inspiron 3501\n"
            "- Price: Rs.45000\n"
            "- Specifications: 8GB RAM, 256GB SSD, 6 hours battery life\n"
            "- Additional Info: 15.6-inch screen, Windows 10, 20% discount\n"
            "- Why Recommend: Affordable price with balanced specs for everyday use.\n\n"
            "do not ask any further questions and give the specific information only"
            "Your Output:"
        ),
        max_tokens=200,
        temperature=0.7,
    )

    llm_recommendations = response.generations[0].text.strip()
    return llm_recommendations

# Streamlit UI
def main():
    st.title("Recommendation System")

    credentials_path = "credentials1.json"
    spreadsheet_id = "1UPPDEfSS8QMuFzPYPuVvTs2Ai3ffu1W49n-1ROqvPhA"

    try:
        sheets_client = initialize_google_sheets(credentials_path)
        sheet = sheets_client.open_by_key(spreadsheet_id).sheet1
        st.success("Hello👋 Welcome!")
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return

    user_name = st.text_input("Enter your name:", placeholder="Your name please")

    # Input method: Text or Voice
    input_method = st.radio("Choose your input method:", ("Text Input", "Voice Input"))

    # To retain the captured input across button clicks
    user_input = st.session_state.get("user_input", "")

    if input_method == "Text Input":
        user_input = st.text_input("Enter your laptop requirements:", value=user_input, placeholder="Your preferences")
    else:
        if st.button("Start Voice Input"):
            st.info("Recording... Please speak now.")
            try:
                recognizer = sr.Recognizer()
                microphone = sr.Microphone()
                with microphone as source:
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source)
                user_input = recognizer.recognize_google(audio)
                st.session_state["user_input"] = user_input
                st.success(f"Captured Voice Input: {user_input}")
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand your speech. Please try again.")
            except sr.RequestError as e:
                st.error(f"Could not request results; {e}")

    if st.button("Get Recommendations"):
        if user_name and user_input:
            # Check for existing customer
            customer_row_index = find_customer_row(sheet, user_name)

            if customer_row_index:
                st.markdown(f"Welcome back {user_name}")
                previous_summary = sheet.row_values(customer_row_index)[2]
                st.markdown(f"Previous Interaction: {previous_summary}")

            else:
                st.markdown(f"Great to have you here {user_name}")

            recommendations = generate_llm_recommendations(user_input)
            if recommendations:
                st.markdown("Recommendations:")
                st.text(recommendations)
            else:
                st.warning("No recommendations could be generated. Please refine your input.")

            sentiment = analyze_sentiment(user_input)
            conversation_summary = summarize_conversation(user_input)

            summary = f"The customer asked for {conversation_summary}"

            if sentiment == "Positive":
                deal_status = "closed"
            elif sentiment == "Neutral":
                deal_status = "not closed"
            else:
                deal_status = "not closed"

            append_customer_interaction(sheet, user_name, user_input, summary, sentiment, deal_status)
            st.success("Happy to help😊")
        elif not user_name:
            st.warning("Please provide your name to proceed.")
        else:
            st.warning("Please fill in all fields.")

if __name__ == "__main__":
    main()
