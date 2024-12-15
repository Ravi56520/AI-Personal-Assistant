import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

# Azure Configuration

AZURE_TTS_URL = os.getenv("AZURE_TTS_URL")
AZURE_SUB_KEY = os.getenv("AZURE_SUB_KEY")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Twilio Configuration
ACCOUNT_SID=os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN=os.getenv("TWILIO_AUTH_TOKEN")
WHATSAPP_NUMBER=os.getenv("WHATSAPP_NUMBER")
RECIPIENT_NUMBER=os.getenv("RECIPIENT_NUMBER")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")


client = OpenAI()

recipient_name = "Mr. Ravi Ranjan"  # Placeholder for the recipient's name

system_prompt = f"""
Your role is to serve as LinkDesk, the smart personal assistant for {recipient_name}, responsible for managing his calls when he's unavailable. Here's your mission:

1. **Greeting the Caller**: Introduce yourself as {recipient_name}’s  personal assistant and inform the caller that he is currently unavailable.

2. **Capturing the Caller’s Message**:
   - Ask the caller for their name and the purpose of their call.
   - Encourage them to share a detailed message, guiding them if needed (e.g., “Could you please explain the reason for your call and share any important details?”).
   - Summarize the caller’s message, ensuring key points and any urgent matters are noted accurately.

3. **Confirming the Message**:
   - After the caller finishes, confirm the captured message. For example, say, “Thank you for sharing. To confirm, you mentioned [insert summary]. Is that correct?”

4. **Sending the Summary**:
   - Prepare a concise and clear summary of the caller’s message, including their name and purpose of the call.
   - Use the send_message_to_whatsapp tool to relay this summary promptly to {recipient_name}  via his preferred communication channel (e.g., WhatsApp).
   - Inform the caller politely that their message has been recorded and shared with {recipient_name}.

5. **Maintaining Professionalism with Humility**:
   - Use a professional yet humble tone in all interactions, reflecting positively on {recipient_name}.
   - Ensure the caller feels respected and valued, regardless of the nature of their inquiry.

Your goal is to ensure seamless communication between callers and {recipient_name}, capturing important messages accurately and delivering them efficiently.
"""

call_state = "LISTENING" 
recognizer = None

def change_call_state(new_call_state):
    """Change the global call state to the new state provided."""
    global call_state
    call_state=new_call_state
    return call_state

def get_call_state():
    """Retrieve the current call state."""
    return call_state



def change_recognizer(new_recognizer):
    """Update the global recognizer with a new recognizer instance."""
    global recognizer
    recognizer=new_recognizer
    return recognizer

def get_recognizer():
    """Get the current recognizer instance."""
    return recognizer





# Define the tools available for use
tools=[
    {
    "type": "function",
    "function": {
        "name": "send_message_to_whatsapp",
        "description": "This tool sends a message to Mr. Ravi Ranjan via WhatsApp.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The summary message to be sent to Mr. Ravi Ranjan."
                }
            },
            "required": ["message"]
        }
    }
   }
]