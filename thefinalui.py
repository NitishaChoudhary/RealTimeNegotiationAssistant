import streamlit as st
import pandas as pd
from thefinal import (
    initialize_google_sheets,
    record_audio_chunk,
    transcribe_audio,
    analyze_sentiment,
    extract_laptop_name,
    get_deal_recommendations,
    negotiation_coach,
    get_previous_interaction,
    summarize_conversation,
    find_customer_row,
    append_to_existing_customer_row,
    append_new_customer_row,
)
laptop_data = pd.read_csv("laptop_dataset_updated.csv")  # Path to the dataset
laptop_data = laptop_data.apply(lambda x: x.str.lower() if x.dtype == "object" else x)
# Helper functions
def extract_bigrams_from_text(text):
    words = text.lower().split()
    return [" ".join(words[i:i + 2]) for i in range(len(words) - 1)]

def extract_laptop_name(user_input, dataset):
    words = user_input.lower().split()
    bigrams = extract_bigrams_from_text(user_input)

    for bigram in bigrams:
        matching_rows = dataset[dataset["Product Name"].str.contains(bigram, case=False, na=False)]
        if not matching_rows.empty:
            return bigram, matching_rows.iloc[0]

    return None, None

import streamlit as st
import pandas as pd
import time

def main():
    st.set_page_config(page_title="AI-based Laptop Recommendation and Negotiation Assistant", page_icon="💻", layout="wide")
    
    # Set header with custom styling
    st.markdown(
        """
        <style>
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #0073e6;
            text-align: center;
        }
        .section-header {
            font-size: 24px;
            font-weight: bold;
            color: #444;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
        .box {
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            background-color: #fff;
            color: #333;
        }
        .red-box {
            background-color: #f44336;
            color: white;
        }
        .green-box {
            background-color: #4caf50;
            color: white;
        }
        .dark-blue-box {
            background-color: #1e3d58;
            color: white;
        }
        .sky-blue-box {
            background-color: #87ceeb;
            color: white;
        }
        .yellow-box {
            background-color: #ffeb3b;
            color: #444;
        }
        .record-button {
            background-color: #0073e6;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True
    )
    
    st.markdown('<div class="title">AI-based Laptop Recommendation and Negotiation Assistant</div>', unsafe_allow_html=True)

    credentials_path = "credentials2.json"
    spreadsheet_id = "1BQRX513_GAiLKokObbJoA30foTKzLC_BFS48LD5MMTM"
    customer_history_path = "dataset_preparation - Sheet1.csv"

    sheet = initialize_google_sheets(credentials_path, spreadsheet_id)
    customer_history = pd.read_csv(customer_history_path)

    customer_name = st.text_input("Enter Customer Name:", key="customer_name")
    
    # Create a section for user input
    st.markdown('<div class="section-header">Customer Interaction</div>', unsafe_allow_html=True)
    
    conversation = []
    focused_laptops = []
    if customer_name:
        previous_summary, deal_status = get_previous_interaction(customer_name, customer_history)
        if previous_summary:
            st.markdown(f"<div class='box sky-blue-box'>{previous_summary}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='box sky-blue-box'>{deal_status}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='box sky-blue-box'>No previous conversation found for this customer.</div>", unsafe_allow_html=True)
    # User View Section
    record_button = st.button("Record Customer Audio", key="record_button", help="Click to record audio", use_container_width=True)
    is_recorded = False
    while True:
        if record_button:
            st.write("Recording customer input for 6 seconds...")
            audio_file = record_audio_chunk(duration=6)
            text = transcribe_audio(audio_file)
            if text:
                conversation.append(text)

                # If "end" is detected, stop processing immediately
                if "end" in text.lower():
                    st.write("Ending the conversation as per the buyer's request.")
                    summary = summarize_conversation(conversation)
                    
                    # Determine sentiment of the last input for deal status
                    sentiment = analyze_sentiment(conversation[-1])  
                    final_deal_status = "closed" if sentiment == "Positive" else "not closed"

                    st.markdown(f"<div class='box sky-blue-box'><strong>Summary of Interaction</strong></div>", unsafe_allow_html=True)
                    st.write(f"Summary: {summary}")
                    st.write(f"Final Deal Status: {final_deal_status}")
                    
                    row_index = find_customer_row(sheet, customer_name)
                    if row_index:
                        append_to_existing_customer_row(sheet, row_index, conversation, summary, sentiment, final_deal_status)
                    else:
                        append_new_customer_row(sheet, customer_name, conversation, summary, sentiment, final_deal_status)
                    
                    st.write("Customer interaction logged successfully.")
                    break

                st.write(f"Customer Input: {text}")
            
                sentiment = analyze_sentiment(text)
                if sentiment == "Positive":
                    sentiment_box_class = "green-box"
                elif sentiment == "Negative":
                    sentiment_box_class = "red-box"
                else:
                    sentiment_box_class = "dark-blue-box"
                st.markdown(f"<div class='box {sentiment_box_class}'>Sentiment: {sentiment}</div>", unsafe_allow_html=True)

                laptop_name, laptop_row = extract_laptop_name(text, laptop_data)
                if laptop_name:
                    st.write(f"Matched Laptop: {laptop_name}")
                    if "discount" in text.lower() or "over my budget" in text.lower():
                        if sentiment in ["Neutral", "Negative"]:
                            discounted_price = laptop_row["Discounted Price"]
                            st.write(f"Discounted Price for {laptop_name}: ₹{discounted_price:.2f}")
                    else:
                        st.write(f"No discount applicable as sentiment is {sentiment}.")              
                intent = "purchase" if "buy" in text.lower() else "inquiry"
                answer, recommendations, focused_laptops = get_deal_recommendations(text, customer_name, laptop_data, focused_laptops)
                st.markdown(f"<div class='box dark-blue-box'>Answer: {answer}</div>", unsafe_allow_html=True)
                if recommendations:
                    st.write("**Laptop Recommendations**: ")
                    for rec in recommendations:
                        st.markdown(f"<div class='box red-box'>- {rec['Product Name']}, {rec['RAM']}, {rec['SSD']}, {rec['Battery Life']}, {rec['OS']}, {rec['Final Price']}</div>", unsafe_allow_html=True)
                if "Neutral" in sentiment or "Negative" in sentiment:
                    negotiation_tips = negotiation_coach(conversation)
                    st.markdown(f"<div class='box yellow-box'>Negotiation Tips: {negotiation_tips}</div>", unsafe_allow_html=True)

            is_recorded = True

            # Wait for 4 seconds before starting the next recording
            st.write("Waiting for 4 seconds before next recording...")
            time.sleep(4)
    
    st.markdown('</div>', unsafe_allow_html=True)
if __name__ == "__main__":
    main()