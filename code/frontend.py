import streamlit as st
import time
from azure_asr_service import recognize_speech_continuously,get_call_state,change_call_state

# Page configuration
st.set_page_config(page_title="Phone Call Interface", page_icon="📞", layout="centered")

# Custom styles
st.markdown(
    """
    <style>
    .main-container {
        background-color: #f1f1f1;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .status-container {
        padding: 15px;
        margin: 20px 0;
        border-radius: 5px;
        color: white;
        font-size: 1.2em;
        font-weight: bold;
    }
    .status-started {
        background-color: #28a745;
    }
    .status-ended {
        background-color: #dc3545;
    }
    .timer {
        font-size: 2em;
        font-weight: bold;
        margin: 20px 0;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state initialization
if "call_status" not in st.session_state:
    st.session_state.call_status = "No call in progress"
if "call_start_time" not in st.session_state:
    st.session_state.call_start_time = None
if "elapsed_time" not in st.session_state:
    st.session_state.elapsed_time = 0
if "messages" not in st.session_state:
    st.session_state.messages = []  # List to store messages       

# Helper function to format the call duration
def format_duration(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"




# # Function to add messages to the chat
# def add_message():
#     message=get_message_array()
#     st.session_state.messages=message

# Function to be triggered when the call starts
def on_call_connected():
    st.write("🎉 The call has been connected! Performing actions...")
    change_call_state("LISTENING")
    recognize_speech_continuously()  # This function handles speech recognition


# Function to be triggered when the call ends
def on_call_ended():
    st.write("❌ The call has ended. Performing cleanup actions...")
    change_call_state("STOP")
    

# Call timer logic
if st.session_state.call_status == "Call is started":
    st.session_state.elapsed_time = int(time.time() - st.session_state.call_start_time)
else:
    st.session_state.elapsed_time = 0

# Page title
st.title("📞 Phone Call Interface")

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Status container
def set_markdown(status_message):
    st.markdown(
        f"""
        <div class="status-container {status_class}">
            {status_message}
        </div>
        """,
        unsafe_allow_html=True,
    )


# Display call status with dynamic styling
if st.session_state.call_status == "Call is started":
    status_class = "status-started"
    status_message = "✅ Call is currently in progress."
elif st.session_state.call_status == "Call is ended":
    status_class = "status-ended"
    status_message = "❌ Call has ended."
else:
    status_class = ""
    status_message = "📞 No call in progress."
set_markdown(status_message)



# Display call timer
if st.session_state.call_status == "Call is started":
    timer_display = format_duration(st.session_state.elapsed_time)
    st.markdown(f'<div class="timer">{timer_display}</div>', unsafe_allow_html=True)

# Buttons to manage call status
col1, col2 = st.columns(2)

with col1:
    if st.button("📞 Start Call", use_container_width=True):
        if st.session_state.call_status != "Call is started":
            st.session_state.call_status = "Call is started"
            status_class = "status-started"
            status_message = "✅ Call is currently in progress."
            st.session_state.call_start_time = time.time()  # Record the start time
            set_markdown(status_message)
            on_call_connected()  # Call the function when the call starts

with col2:
    if st.button("🔴 End Call", use_container_width=True):
        if st.session_state.call_status == "Call is started":
            st.session_state.call_status = "Call is ended"
            status_class = "status-ended"
            status_message = "❌ Call has ended."
            set_markdown(status_message)
            on_call_ended()  # Call the function when the call ends

if st.session_state.messages:
    for message in st.session_state.messages:
        message_class = "assistant" if message["role"] == "assistant" else "user"
        st.markdown(
            f'<div class="message {message_class}">{message["content"]}</div>',
            unsafe_allow_html=True
        )
else:
    st.write("No messages yet.")            

# Main container closing
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")

