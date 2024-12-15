
import requests
import base64
from config import AZURE_TTS_URL, AZURE_SUB_KEY

def generate_audio_azure(text, lang="en-US", voice_name="en-US-AvaNeural", tts_style="chat", retry=True): #en-US-AvaMultilingualNeural
    """
    Convert text to audio using Azure Text-to-Speech.

    Args:
        text (str): Text to convert into speech.
        lang (str, optional): Language code (default is "en-US").
        voice_name (str, optional): Voice to use (default is "en-US-AvaNeural").
        tts_style (str, optional): Style of the speech (default is "chat").
        retry (bool, optional): Flag to retry on failure (default is True).

    Returns:
        str: Base64-encoded audio data if successful; otherwise, an empty string.
    """
    
    text = text.replace("&", " and ").replace("<", " ").replace(">", " ")
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SUB_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
        "User-Agent": "curl",
    }

    data = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang='{lang}'>
        <voice name='{voice_name}'>
            <mstts:express-as style='{tts_style}' styledegree="1.5">
                {text}
            </mstts:express-as>
        </voice>
    </speak>
    """

    # print(f"Azure Request Data - {data}")
    encoded_data = data.encode("utf-8")
    try:
        response = requests.post(AZURE_TTS_URL, headers=headers, data=encoded_data)
        if response.status_code == 200:
            audio_data = response.content
            return base64.b64encode(audio_data).decode("utf-8")
        else:
            print(f"Error: {response.status_code}")
            raise Exception("Failed to generate speech.")
    except Exception as e:
        print(f"Error in generating audio via Azure: {e}")
        return ""



