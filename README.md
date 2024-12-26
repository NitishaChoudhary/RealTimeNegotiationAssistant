Overview
This project is a cutting-edge AI tool designed to empower sales teams by providing real-time insights, sentiment analysis, and actionable suggestions during live sales calls. By integrating advanced NLP models, CRM data, and audio processing capabilities, it helps optimize negotiations, improve customer engagement, and drive better sales outcomes.


Features
Real-Time Speech-to-Text: Converts live audio input (microphone or system audio) into text using SpeechRecognition.
Sentiment Analysis: Detects customer sentiment (positive, neutral, negative) from recognized speech using Hugging Face transformers.
Intent Analysis: Classifies customer intent (e.g., inquiry, complaint, agreement) to provide actionable insights.
Audio Device Selection: Supports capturing audio from the system (e.g., "Stereo Mix") or an external microphone.
Dynamic Suggestions: Provides live recommendations based on sentiment and intent analysis.
Graceful Stop: Enables users to stop audio streaming with a single command.


Key Technologies
SpeechRecognition: For real-time speech-to-text conversion.
Transformers (Hugging Face): For sentiment and intent analysis using pre-trained language models.
PyAudio: For capturing audio input from various devices.


Future Enhancements
Integration with CRM systems for tailored deal suggestions.
Google Sheets or database integration for storing and analyzing call data.
Adding support for multi-language sentiment and intent analysis.
