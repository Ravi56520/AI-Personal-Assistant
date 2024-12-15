
from config import OPENAI_API_KEY,client,tools,get_call_state,change_call_state,system_prompt
from utils_funtions import check_before_or_after_comma_is_number
from azure_tts import generate_audio_azure
from audio_service import play_audio
import time,os,traceback



messages = [{"role": "system", "content": system_prompt}]
call_state=get_call_state()

#-----------------------------------------------------------------------------------------------------
def get_message_array():
    """Returns the current array of messages."""
    return messages

#-----------------------------------------------------------------------------------------------------
def append_user_message(messages, request):
    """Appends a user's message to the messages array if the request is not empty."""
    if request:
        messages.append({"role": "user", "content": request})

#-----------------------------------------------------------------------------------------------------
def create_chat_completion(client, messages, tools):
    """Creates a chat completion using the specified client and messages."""
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        stream=True
    )

#-----------------------------------------------------------------------------------------------------
def determine_break_punctuation(count):
    """Returns punctuation marks used for breaking continuous speech based on the count of processed chunks."""
    if count <= 2:
        return [',', '!', ':', '.', '?', '|', '।', '፧', '፨', '،', '؛', '؟']
    else:
        return ['.', '?', '।', '፧', '፨', '؛', '؟']

#-----------------------------------------------------------------------------------------------------
def check_punctuation_split(continious_string, current_gpt_chunk):
    """Checks if the continuous string can be split based on punctuation rules."""
    words = continious_string.split()
    if not words:
        return False, "", ""

    last_word = words[-1]
    if last_word in ["Mr.", "Dr.", "Ms.", "Mrs."]:
        return False, continious_string, ""

    discarded_string = ""
    if current_gpt_chunk in [",", "."]:
        if check_before_or_after_comma_is_number(last_word):
            discarded_string = " " + last_word
            continious_string = ' '.join(words[:-1])
    
    return True, continious_string, discarded_string

#-----------------------------------------------------------------------------------------------------
def generate_and_play_audio(text):
    """Generates audio from text and plays it if the text is not empty."""
    if text:
        print("chunk:->", text)
        audio_base64 = generate_audio_azure(text)
        if audio_base64:
            play_audio(audio_base64)  # Implement play_audio for playback
        else:
            print("[ERROR] Failed to generate audio.")


#-----------------------------------------------------------------------------------------------------
def extract_function_calls(chunk):
    """Extracts function calls from a chunk of response data."""
    function_name = None
    function_id = None
    function_arguments = ''
    
    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.tool_calls:
        tool_call = chunk.choices[0].delta.tool_calls[0]
        if tool_call.function:
            function_name = tool_call.function.name
            function_id = tool_call.id
            print(f"function_name: {function_name}")
            if tool_call.function.arguments:
                function_arguments += tool_call.function.arguments
                print(f"function_arguments :{function_arguments}")
    
    return function_name, function_arguments, function_id


#-----------------------------------------------------------------------------------------------------
def process_streaming_response(response, initial_timestamp):
    """
    Processes the streaming response from the language model, accumulating generated text and managing audio playback.

    It tracks the time taken for the first chunk, detects function calls, and generates audio output as needed.

    Args:
        response: The streaming response object containing generated text chunks.
        initial_timestamp: The timestamp when the streaming started.

    Returns:
        A tuple with the complete response string, function name, function arguments, function ID, and time for the first chunk.
    """

    complete_string = ""
    continious_string = ""
    first_chunk_time = 0
    count = 1
    function_id = None
    function_name = None
    function_arguments = ''
    chunk_timestamp = initial_timestamp
    
    for chunk in response:
        current_gpt_chunk = chunk.choices[0].delta.content if chunk.choices else ""
        
        if current_gpt_chunk and chunk.choices and chunk.choices[0].delta:
            break_punctuation = determine_break_punctuation(count)
            
            if any(punc in current_gpt_chunk for punc in break_punctuation):
                continious_string += current_gpt_chunk
                complete_string += current_gpt_chunk

                if count == 1:
                    first_chunk_time = (time.time() - chunk_timestamp) * 1000
                    print(f"[DEBUG] Time taken to generate 1st chunk: {first_chunk_time} ms")

                should_split, continious_string, discarded_string = check_punctuation_split(continious_string, current_gpt_chunk)
                if should_split:
                    chunk_timestamp = time.time()
                    continious_string = continious_string.strip()
                    generate_and_play_audio(continious_string)
                    continious_string = discarded_string
                    count += 1
            else:
                continious_string += current_gpt_chunk
                complete_string += current_gpt_chunk

        # Extract function calls if any
        fn_name, fn_args, fn_id = extract_function_calls(chunk)
        if fn_name:
            function_name = fn_name
        if fn_args:
            function_arguments += fn_args
        if fn_id:
            function_id = fn_id

    if continious_string:
            print("chunk:->", continious_string)
            audio_base64 = generate_audio_azure(continious_string)

            if audio_base64:
                play_audio(audio_base64) 
            else:
                print("[ERROR] Failed to generate final audio.")

    return complete_string, function_name, function_arguments, function_id, first_chunk_time


#-----------------------------------------------------------------------------------------------------
def process_chunk(request, client, messages, tools):
    """
    Handles a user request by appending the message and generating a response from the chat client.

    Captures exceptions during processing and manages the overall flow of information.

    Args:
        request: The user's message to process.
        client: The chat client for interaction with the language model.
        messages: The conversation context.
        tools: The available tools for processing.

    Returns:
        A tuple containing the complete response string, function name, function arguments, function ID, first chunk time, and an error flag.
    """
    try:
        append_user_message(messages, request)
        response = create_chat_completion(client, messages, tools)
        
        initial_timestamp = time.time()
        (complete_string, function_name, 
         function_arguments, function_id, 
         first_chunk_time) = process_streaming_response(response, initial_timestamp)
        
        return complete_string, function_name, function_arguments, function_id, first_chunk_time, False

    except Exception as e:
        print(f"[ERROR] An error occurred while processing the chunk: {e}")
        print(f"traceback in process chunk : {traceback.format_exc()}")
        return None, None, None, None, None, True


#-----------------------------------------------------------------------------------------------------
# Function to initiate the conversation using LLM
def initiate_conversation_with_llm():
    """
    Initiates a conversation with the language model by sending a greeting message to the caller.

    Sends an initial query to generate an introductory message and appends the response to the conversation context.

    Returns:
        None
    """
    global messages
    if call_state == "LISTENING":
        initial_query = "Please introduce yourself to the caller as Mr. Ravi Ranjan’s assistant and ask for their name and the purpose of their call."
        print("[DEBUG] Sending initial query to LLM...")

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream= True
            )
            llm_response, _, _, _, _, _ = process_chunk(initial_query,client,messages,tools)
            messages.append({"role":"assistant","content":llm_response})

            print(f"LLM Generated Greeting: {llm_response}")
        except Exception as e:
            print(f"[ERROR] An error occurred while initiating the conversation: {e}")
            print(f"traceback in intitial  chunk : {traceback.format_exc()}")

