from transformers import pipeline

sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    """Analyze the sentiment of a given text."""
    result = sentiment_analyzer(text)[0]
    return result["label"], result["score"]
