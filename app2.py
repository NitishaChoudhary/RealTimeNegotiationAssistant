import streamlit as st
import pandas as pd
import cohere
import speech_recognition as sr
import re

# Initialize Cohere API
COHERE_API_KEY = "wnDl2gFhkWSgehGd193dsPfVMKIJlDaSooLiXJrp"
co = cohere.Client(COHERE_API_KEY)

# Load dataset
dataset_path = "C:\\Users\\choud\\Downloads\\laptop_dataset_updated.csv"
laptop_data = pd.read_csv(dataset_path)

# Preprocess dataset
laptop_data = laptop_data.apply(lambda x: x.str.lower() if x.dtype == "object" else x)
columns_to_extract = ["RAM", "SSD (GB)", "HDD (GB)", "Battery Life (hrs)"]
for col in columns_to_extract:
    laptop_data[col] = laptop_data[col].astype(str).str.extract(r"(\d+\.?\d*)").astype(float)

laptop_data["Final Price"] = pd.to_numeric(laptop_data["Final Price"], errors="coerce")

# Function to convert textual numbers to numeric
def words_to_numbers(word):
    word = word.lower().replace(",", "").replace("rs", "").strip()
    multiplier = {"lakh": 100000, "thousand": 1000, "hundred": 100}
    total = 0
    temp_number = 0

    for part in word.split():
        if part.isdigit():
            temp_number = int(part)
        elif part in multiplier:
            total += temp_number * multiplier[part]
            temp_number = 0
        else:
            try:
                temp_number = int(part)
            except ValueError:
                pass

    total += temp_number
    return total if total > 0 else None

# Function to check for general queries
def is_general_query(user_input):
    general_keywords = ["best laptop", "latest laptops", "best selling laptops", "top laptops"]
    return any(keyword in user_input.lower() for keyword in general_keywords)

# Function to get general laptop recommendations
def get_general_recommendations():
    brand_model_pairs = laptop_data["Product Name"].str.extract(r"(\b\w+\b)(.*)", expand=True)
    recommendations = brand_model_pairs.dropna().apply(lambda x: f"Brand: {x[0].capitalize()}, Model: {x[1].strip()}", axis=1)
    return "\n".join(recommendations.unique())

# Function to filter laptops based on user input
def filter_laptops(user_input):
    user_input_lower = user_input.lower()
    budget, ram, brand, os = None, None, None, None
    budget_direction = None

    # Extract budget
    if "under" in user_input_lower or "below" in user_input_lower:
        budget_direction = "below"
        budget_matches = re.findall(r"under|below\s+([\w\s]+)", user_input_lower)
        if budget_matches:
            budget = words_to_numbers(budget_matches[0])
    elif "above" in user_input_lower or "over" in user_input_lower:
        budget_direction = "above"
        budget_matches = re.findall(r"above|over\s+([\w\s]+)", user_input_lower)
        if budget_matches:
            budget = words_to_numbers(budget_matches[0])

    # Extract RAM
    if "ram" in user_input_lower:
        try:
            ram = float(re.search(r"(\d+)\s*gb\s*ram", user_input_lower).group(1))
        except (ValueError, AttributeError):
            ram = None

    # Extract brand
    for dataset_brand in laptop_data["Product Name"].str.extract(r"(\b\w+\b)", expand=False).unique():
        if dataset_brand in user_input_lower:
            brand = dataset_brand
            break

    # Extract OS
    for dataset_os in laptop_data["OS"].unique():
        if dataset_os in user_input_lower:
            os = dataset_os
            break

# Function to filter laptops based on user input
def filter_laptops(user_input):
    user_input_lower = user_input.lower()
    budget, ram, brand, os = None, None, None, None
    budget_direction = None

    # Extract budget
    if "under" in user_input_lower or "below" in user_input_lower:
        budget_direction = "below"
        budget_matches = re.findall(r"under|below\s+([\w\s]+)", user_input_lower)
        if budget_matches:
            budget = words_to_numbers(budget_matches[0])
    elif "above" in user_input_lower or "over" in user_input_lower:
        budget_direction = "above"
        budget_matches = re.findall(r"above|over\s+([\w\s]+)", user_input_lower)
        if budget_matches:
            budget = words_to_numbers(budget_matches[0])

    # Extract RAM
    if "ram" in user_input_lower:
        try:
            ram = float(re.search(r"(\d+)\s*gb\s*ram", user_input_lower).group(1))
        except (ValueError, AttributeError):
            ram = None

    # Extract brand
    for dataset_brand in laptop_data["Product Name"].str.extract(r"(\b\w+\b)", expand=False).unique():
        if dataset_brand.lower() in user_input_lower:
            brand = dataset_brand
            break

    # Extract OS
    for dataset_os in laptop_data["OS"].unique():
        if dataset_os.lower() in user_input_lower:
            os = dataset_os
            break

    # Filter data
    filtered_data = laptop_data.copy()
    if budget:
        if budget_direction == "below":
            filtered_data = filtered_data[filtered_data["Final Price"] <= budget]
        elif budget_direction == "above":
            filtered_data = filtered_data[filtered_data["Final Price"] >= budget]
    if ram:
        filtered_data = filtered_data[filtered_data["RAM"] == ram]  # Match exact RAM
    if brand:
        filtered_data = filtered_data[filtered_data["Product Name"].str.contains(brand, case=False)]
    if os:
        filtered_data = filtered_data[filtered_data["OS"].str.contains(os, case=False)]

    return filtered_data

# Function to generate laptop recommendations
def get_deal_recommendations(user_input):
    try:
        if is_general_query(user_input):
            return get_general_recommendations()

        filtered_laptops = filter_laptops(user_input)

        if filtered_laptops.empty:
            return "No laptops match your criteria. Please refine your preferences."

        # Sort by price ascending for better deals
        dataset_recommendations = filtered_laptops.sort_values("Final Price").head(3)

        dataset_recommendations_text = "\n".join(
            dataset_recommendations.apply(lambda row: f"{row['Product Name']} - ${row['Final Price']}\n" +
                f"RAM: {row['RAM']}GB, SSD: {row['SSD (GB)']}GB, HDD: {row['HDD (GB)']}GB\n" +
                f"Battery Life: {row['Battery Life (hrs)']}hrs, Graphics Card: {row['Graphics Card']}\n" +
                f"CPU: {row['CPU']}, OS: {row['OS']}, Screen: {row['Screen Size (inches)']} inches\n" +
                f"Screen Technology: {row['Screen Technology']}, Resolution: {row['Resolution']}\n" +
                f"Discount: {row['Discount (%)']}%, Deals: {row['Deals']}\n", axis=1).tolist()
        )

        response = co.generate(
            model="command-xlarge",
            prompt=(
                "You are an assistant providing personalized laptop recommendations based on user preferences.\n\n" +
                f"User Input: {user_input}\n" +
                f"Laptops from the dataset:\n{dataset_recommendations_text}\n\n" +
                "Generate a concise and helpful recommendation in bullet points:"),
            max_tokens=100,
            temperature=0.7,
        )

        enriched_recommendations = response.generations[0].text.strip()
        # Format suggestions into bullet points
        formatted_suggestions = "\n".join([f"- {line.strip()}" for line in enriched_recommendations.splitlines() if line.strip()])

        return f"Dataset Recommendations:\n{dataset_recommendations_text}\n\nLLM Suggestions:\n{formatted_suggestions}"

    except Exception as e:
        return f"An error occurred: {e}"



# Streamlit UI
st.title("Laptop Recommendation System")
user_name = st.text_input("Enter your name:")
user_input = st.text_input("Enter your laptop requirements:")

if st.button("Get Recommendations"):
    if user_input:
        recommendations = get_deal_recommendations(user_input)  # Your recommendation function
        st.text(recommendations)
    else:
        st.warning("Please enter some requirements.")


if 'listening' not in st.session_state:
    st.session_state.listening = False
    st.session_state.voice_input = ""

if st.button("Use Speech Input"):
    st.session_state.listening = True
    st.session_state.voice_input = ""  

if st.button("Stop Listening"):
    st.session_state.listening = False

if st.session_state.listening:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening for your requirements... Speak now.")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            st.session_state.voice_input = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand your speech. Please try again.")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")

if st.session_state.voice_input:
    st.success(f"You said: {st.session_state.voice_input}")
    recommendations = get_deal_recommendations(st.session_state.voice_input)
    st.text(recommendations)