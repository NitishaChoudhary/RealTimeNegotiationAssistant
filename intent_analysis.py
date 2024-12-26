from transformers import pipeline

intent_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def analyze_intent(text, candidate_labels):
    """Analyze the intent of a given text."""
    result = intent_classifier(text, candidate_labels)
    return result["labels"][0], result["scores"][0]
