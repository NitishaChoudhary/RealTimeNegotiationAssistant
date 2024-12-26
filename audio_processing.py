# import speech_recognition as sr
# import pyaudio

# def stream_audio(callback):
#     """Stream audio and process speech in real-time using SpeechRecognition."""
#     recognizer = sr.Recognizer()
#     microphone = sr.Microphone()

#     print("Listening for audio...")

#     with microphone as source:
#         recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
#         while True:
#             try:
#                 # Capture audio from the microphone
#                 print("Listening...")
#                 audio = recognizer.listen(source, timeout=5)

#                 # Recognize speech using Google Web Speech API
#                 text = recognizer.recognize_google(audio)
#                 print(f"Recognized: {text}")

#                 # Process the recognized text with the callback
#                 callback(text)
#             except sr.WaitTimeoutError:
#                 print("Timed out listening.")
#                 continue
#             except sr.UnknownValueError:
#                 print("Could not understand audio.")
#                 continue
#             except sr.RequestError as e:
#                 print(f"Error with speech recognition request: {e}")
#                 break

import speech_recognition as sr
import threading
import sys
listening = True

def stop_listening():
    """Stop the audio streaming."""
    global listening
    listening = False
    print("Stopping audio stream...")

def stream_audio(callback):
    """
    Stream audio and process speech in real-time using SpeechRecognition.
    
    :param callback: Function to process recognized text
    """
    global listening
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Listening for audio. Press 'Ctrl+C' or use the stop function to exit.")

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)  
        while listening:
            try:
                print("Listening...")
                audio = recognizer.listen(source, timeout=5)

                #### using Google Web Speech API
                text = recognizer.recognize_google(audio)
                print(f"Recognized: {text}")

                callback(text)
            except sr.WaitTimeoutError:
                print("Timed out listening. Waiting for new input...")
                continue
            except sr.UnknownValueError:
                print("Could not understand audio. Please try again.")
                continue
            except sr.RequestError as e:
                print(f"Error with speech recognition request: {e}")
                break
            except KeyboardInterrupt:
                stop_listening()
                break
def process_recognized_text(text):
    """Process recognized text (e.g., sentiment or intent analysis)."""
    print(f"Processing text: {text}")

def start_streaming():
    stream_thread = threading.Thread(target=stream_audio, args=(process_recognized_text,))
    stream_thread.start()
    return stream_thread

if __name__ == "__main__":
    try:
        stream_thread = start_streaming()

        input("Press Enter to stop the audio streaming...\n")
        stop_listening()
        stream_thread.join()

    except KeyboardInterrupt:
        print("Exiting...")
        stop_listening()
        sys.exit(0)

# import speech_recognition as sr
# import threading
# import sys
# import pyaudio

# listening = True

# def stop_listening():
#     """Stop the audio streaming."""
#     global listening
#     listening = False
#     print("Stopping audio stream...")

# def stream_audio(callback, input_device_index=None):
#     """
#     Stream audio and process speech in real-time using SpeechRecognition.
    
#     :param callback: Function to process recognized text
#     :param input_device_index: Index of the audio input device
#     """
#     global listening
#     recognizer = sr.Recognizer()

#     if input_device_index is not None:
#         microphone = sr.Microphone(device_index=input_device_index)
#     else:
#         microphone = sr.Microphone()

#     print(f"Listening for audio on device {input_device_index or 'default'}. Press 'Ctrl+C' or use the stop function to exit.")

#     with microphone as source:
#         recognizer.adjust_for_ambient_noise(source)  
#         while listening:
#             try:
#                 print("Listening...")
#                 audio = recognizer.listen(source, timeout=5)

#                 # Recognize speech using Google Web Speech API
#                 text = recognizer.recognize_google(audio)
#                 print(f"Recognized: {text}")

#                 callback(text)
#             except sr.WaitTimeoutError:
#                 print("Timed out listening. Waiting for new input...")
#                 continue
#             except sr.UnknownValueError:
#                 print("Could not understand audio. Please try again.")
#                 continue
#             except sr.RequestError as e:
#                 print(f"Error with speech recognition request: {e}")
#                 break
#             except KeyboardInterrupt:
#                 stop_listening()
#                 break

# def list_audio_devices():
#     """List available audio input devices."""
#     p = pyaudio.PyAudio()
#     print("Available audio devices:")
#     for i in range(p.get_device_count()):
#         device_info = p.get_device_info_by_index(i)
#         print(f"Index {i}: {device_info['name']}")
#     p.terminate()

# def process_recognized_text(text):
#     """Process recognized text (e.g., sentiment or intent analysis)."""
#     print(f"Processing text: {text}")

# def start_streaming(input_device_index=None):
#     """Start the audio streaming in a separate thread."""
#     stream_thread = threading.Thread(target=stream_audio, args=(process_recognized_text, input_device_index))
#     stream_thread.start()
#     return stream_thread

# if __name__ == "__main__":
#     try:
#         print("List of available audio devices:")
#         list_audio_devices()

#         device_index = input("Enter the index of the audio device to use (or press Enter to use default): ")
#         device_index = int(device_index) if device_index.strip() else None

#         # Start streaming from the selected device
#         stream_thread = start_streaming(device_index)

#         input("Press Enter to stop the audio streaming...\n")
#         stop_listening()
#         stream_thread.join()

#     except KeyboardInterrupt:
#         print("Exiting...")
#         stop_listening()
#         sys.exit(0)
