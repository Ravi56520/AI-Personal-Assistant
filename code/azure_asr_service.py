import azure.cognitiveservices.speech as speechsdk
import requests
import time
import traceback
import base64
import os
from config import AZURE_API_KEY, AZURE_REGION, client, tools, change_recognizer, get_call_state, change_call_state
from llm_service import initiate_conversation_with_llm, process_chunk,get_message_array
from whatspp_service import send_message_to_whatsapp
from utils_funtions import append_asst_msg, append_tool_call_message

# Declare call_state as a global variable
call_state = get_call_state()  # Initialize it with the initial state
messages = get_message_array()

#-------------------------------------------------------------------------------------------------------
def initialize_speech_recognizer():
    """Initialize the Azure speech recognizer."""
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_API_KEY, region=AZURE_REGION)
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    return recognizer


#-------------------------------------------------------------------------------------------------------
def start_recognition_if_listening(recognizer):
    """Start continuous recognition if the call state is LISTENING."""
    global call_state  # Access the global call_state variable
    if call_state == "LISTENING":
        recognizer.start_continuous_recognition()
        print("[DEBUG] ASR started and is now listening...")
    else:
        print("[DEBUG] ASR is not in the LISTENING state.")

#-------------------------------------------------------------------------------------------------------
def process_recognized_text(recognized_text, recognizer):
    """Process the recognized text and interact with the LLM."""
    global call_state  # Access the global call_state variable
    change_call_state("SPEAKING")
    recognizer.stop_continuous_recognition()  # Stop ASR during response processing
    print("[DEBUG] ASR stopped for LLM response processing.")


#-------------------------------------------------------------------------------------------------------
def log_llm_response(llm_response, function_name, function_arguments, function_id, first_chunk_time, error_occurred):
    """Log details of the LLM response."""
    print(f"[DEBUG] LLM Response: {llm_response}")
    print(f"[DEBUG] Function Name: {function_name}")
    print(f"[DEBUG] Function Arguments: {function_arguments}")
    print(f"[DEBUG] Function ID: {function_id}")
    print(f"[DEBUG] First Chunk Time: {first_chunk_time} ms")
    print(f"[DEBUG] Error Occurred: {error_occurred}")


#-------------------------------------------------------------------------------------------------------
def handle_llm_response(llm_response, function_name, function_arguments, function_id):
    """Handle the LLM response appropriately."""
    global call_state  # Access the global call_state variable
    if llm_response:
        messages.append({"role": "assistant", "content": llm_response})
    elif function_name:
        append_asst_msg(messages=messages, function_id=function_id, function_name=function_name,
                        function_args=function_arguments)
        print(f"[DEBUG] Calling function '{function_name}' with arguments: {function_arguments}")
        # Call the WhatsApp sending function
        function_returns = send_message_to_whatsapp(function_arguments)
        append_tool_call_message(messages=messages, function_id=function_id, function_name=function_name,
                                 function_returns=function_returns)
        llm_response, _, _, _, _, _ = process_chunk(None, client, messages, tools)
        print(f"LLM Response after function call: {llm_response}")
        messages.append({"role": "assistant", "content": llm_response})
    
    change_call_state("LISTENING")


#-------------------------------------------------------------------------------------------------------
def handle_recognition_result(evt, recognizer):
    """Handle the recognition result from the speech recognizer."""
    global call_state  # Access the global call_state variable

    if call_state != "LISTENING":
        print("[DEBUG] ASR ignored input since call_state is not LISTENING.")
        return

    print("[DEBUG] LISTENING AGAIN")
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        recognized_text = evt.result.text.strip()
        if recognized_text:
            print(f"[DEBUG] ASR recognized text: {recognized_text}")
            process_recognized_text(recognized_text, recognizer)
    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
        print("[DEBUG] No speech could be recognized.")
    elif evt.result.reason == speechsdk.ResultReason.Canceled:
        print(f"[DEBUG] Recognition canceled: {evt.result.cancellation_details.reason}")



    # Process the recognized text with process_chunk
    llm_response, function_name, function_arguments, function_id, first_chunk_time, error_occurred = process_chunk(recognized_text, client, messages, tools)
    
    # Log the results
    log_llm_response(llm_response, function_name, function_arguments, function_id, first_chunk_time, error_occurred)

    # Handle the LLM response
    handle_llm_response(llm_response, function_name, function_arguments, function_id)
    recognizer.start_continuous_recognition()


#-------------------------------------------------------------------------------------------------------
def recognize_speech_continuously():
    """Continuously recognize speech using Azure Speech Service."""
    global call_state  # Access the global call_state variable
    call_state = get_call_state()  # Refresh call_state if needed
    
    recognizer = initialize_speech_recognizer()
    change_recognizer(recognizer)  # Ensure the recognizer is set globally
    print("[DEBUG] ASR started and is now listening...")
    print("[DEBUG] ASR initialized. Waiting to start recognition...")
    
    initiate_conversation_with_llm()
    print("Listening... Speak into your microphone.")
    
    recognizer.recognized.connect(lambda evt: handle_recognition_result(evt, recognizer))
    
    # Start ASR only if it's in the correct state
    start_recognition_if_listening(recognizer)
    
    try:
        while True:
            call_state = get_call_state()
            if call_state == "STOP":
                recognizer.stop_continuous_recognition()
                print("[DEBUG] ASR is now STOPPING")
                break 
    except KeyboardInterrupt:
        print("[DEBUG] Stopping recognition...")
        print(f"traceback in recognize_speech_continuously: {traceback.format_exc()}")
        recognizer.stop_continuous_recognition()
