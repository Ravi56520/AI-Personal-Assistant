import base64
from playsound import playsound
from config import change_call_state




def play_audio(audio_base64):
    """
    Play audio from a base64-encoded string.

    This function decodes a base64-encoded audio string, writes it to an 
    output file, and plays the audio using the playsound library. 
    It also manages the call state for automatic speech recognition (ASR) 
    by changing the state to "SPEAKING" before playback and reverting 
    it to "LISTENING" afterward.

    Args:
        audio_base64 (str): A base64-encoded string representing the audio data.

    Returns:
        None
    """

    audio_data = base64.b64decode(audio_base64)
    audio_file_path = "output.mp3"  

    with open(audio_file_path, "wb") as audio_file:
        audio_file.write(audio_data)
    
    # Stop ASR before playing audio
    change_call_state("SPEAKING")
    print("[DEBUG] Playing audio and pausing ASR...")
    playsound(audio_file_path)  # This will play the audio file

    change_call_state("LISTENING")
    print("[DEBUG] Audio playback finished. Restarting ASR...")
