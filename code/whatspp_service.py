from twilio.rest import Client
from config import ACCOUNT_SID, AUTH_TOKEN, WHATSAPP_NUMBER, RECIPIENT_NUMBER

def send_message_to_whatsapp(message):
    """
    Sends a message to a specified WhatsApp number using Twilio's API.

    Parameters:
        message (str): The content of the message to be sent.

    Returns:
        str: A message indicating the success or failure of the send operation.
    """
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    try:
        msg = client.messages.create(
            from_=WHATSAPP_NUMBER,
            body=message,
            to=f'whatsapp:{RECIPIENT_NUMBER}'
        )
        print(f"[INFO] WhatsApp message sent. SID: {msg.sid}")
        return "Message sent successfully"
    except Exception as e:
        print(f"[ERROR] Failed to send WhatsApp message: {e}")
        return "Error in sending message."

