import re

def check_before_or_after_comma_is_number(s):
    """Check if there's a number before or after a comma."""
    try:
        pattern = r'\d[,.]|[,.]\d'
        return bool(re.search(pattern, s))
    except Exception as e:
        print(f"[ERROR] Regex check failed: {e}")
        return False

#-----------------------------------------------------------------------------------------------

def append_asst_msg(messages, function_id, function_name, function_args):
    """Appends an assistant message to the conversation, including details of the invoked function call."""
    messages.append(
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": function_id,
                    "function": {"name": function_name, "arguments": function_args},
                    "type": "function",
                }
            ],
        }
    )

#-----------------------------------------------------------------------------------------------
def append_tool_call_message(messages, function_id, function_name, function_returns):
    """Appends a tool call message to the conversation with the function's return value."""
    messages.append(
        {
            "tool_call_id": function_id,
            "role": "tool",
            "name": function_name,
            "content": function_returns,
        }
    )