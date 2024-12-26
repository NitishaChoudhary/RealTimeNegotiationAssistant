import streamlit as st
from sentiment_analysis import analyze_sentiment
from intent_analysis import analyze_intent
from audio_processing import stream_audio
from crm_integration import get_customer_data
from sheet_integration import log_to_sqlite

#### intent labels
CANDIDATE_LABELS = ["agreement", "objection", "inquiry", "complaint", "greeting"]

def process_audio_input(text):
    st.write(f"Recognized Text: {text}")

    sentiment, sentiment_score = analyze_sentiment(text)
    st.write(f"Sentiment: {sentiment} ({sentiment_score:.2f})")

    intent, intent_score = analyze_intent(text, CANDIDATE_LABELS)
    st.write(f"Intent: {intent} ({intent_score:.2f})")

    log_to_sqlite(text="I like the software, but it's a bit pricey.",
              sentiment="NEGATIVE", sentiment_score=0.85,
              intent="OBJECTION", intent_score=0.92)

#### Streamlit interface
st.title("Real-Time AI Sales Intelligence Tool")
customer_id = st.text_input("Enter Customer ID:")
if customer_id:
    customer_data = get_customer_data(customer_id)
    st.write(f"Customer Data: {customer_data}")

if st.button("Start Live Analysis"):
    stream_audio(process_audio_input)
