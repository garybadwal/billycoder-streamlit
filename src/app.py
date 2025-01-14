import json
import os

from typing import List, Dict
from datetime import datetime

import streamlit as st
from huggingface_hub import InferenceClient

from configs.constants import MESSAGES
from configs.cred import HUGGING_FACE_TOKEN as TOKEN

TMP_DIR = '/tmp'

def get_messages() -> List[Dict[str, str]]:
    """
    Retrieves the conversation history from a JSON file.

    Returns:
        list: A list of conversation messages.
    """
    if os.path.exists(os.path.join(TMP_DIR,'conversations.json')):
        with open(os.path.join(TMP_DIR,'conversations.json'), 'r') as file:
            try:
                messages = json.load(file)
            except json.JSONDecodeError:
                messages = MESSAGES
            return messages
    else:
        return MESSAGES

def set_messages(messages: List[Dict[str, str]]):
    """
    Saves the conversation history to a JSON file.

    Args:
        messages (list): A list of conversation messages.
    """
    with open(os.path.join(TMP_DIR,'conversations.json'), 'w') as file:
        json.dump(messages, file)

def get_content(response) -> dict:
    """
    Extracts content from a ChatCompletion response.

    Args:
        response (ChatCompletion): The response object containing the chat completion.

    Returns:
        dict: A dictionary containing the parsed content.
    """

    # Initialize an empty dictionary to hold the result
    result = ""

    try:
        # Get the choices from the response
        choices = response.choices

        # Check if there are any choices available
        if len(choices) > 0:
            # Select the first choice
            choice = choices[0]

            # Extract the message from the choice
            message = choice.message

            # Get the content from the message
            content = message.content

            # Parse the content as JSON and store it in the result dictionary
            result = content

    except Exception as e:
        # Print an error message if parsing fails
        print('Error parsing response: ', str(e))

    # Return the extracted result
    return result

def reset_daily_count():
    today = datetime.now().date()
    if "last_reset" not in st.session_state or st.session_state.last_reset < today:
        st.session_state.last_reset = today
        st.session_state.message_count = 0

def clear_chat():
    # Clear the conversations.json file and reinitialize messages in session state
    open(os.path.join(TMP_DIR,'conversations.json'), 'w').close()  # Empty the file
    st.session_state.messages = get_messages()  # Reinitialize messages

st.title("BillyCoder")
st.caption("Your AI code assistant.")

# Clear Chat Button
if st.button("Clear Chat", key="clear_chat_button"):
    clear_chat()
    st.success("Chat cleared!")

with st.expander("ℹ️ Disclaimer"):
    st.caption(
        """We appreciate your engagement! Please note, this demo is designed to
        process a maximum of 999 interactions per day. Thank you for your understanding.
        """
    )

client = InferenceClient(api_key=TOKEN)

if "messages" not in st.session_state:
    st.session_state.messages = get_messages()

reset_daily_count()

if len(st.session_state.messages) >= 999:
    st.info("Notice: The maximum message limit for today has been reached.")
else:
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] != 'system':
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
            
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                completion = client.chat.completions.create(
                    model="Qwen/Qwen2.5-Coder-32B-Instruct",
                    messages=st.session_state.messages,
                    temperature=0.3,
                    max_tokens=15000,
                    top_p=0.7
                )
                message = get_content(completion)
                response = st.write(get_content(completion))
                st.session_state.messages.append(
                    {"role": "assistant", "content": message}
                )
                st.session_state.message_count += 1
                set_messages(st.session_state.messages)
            except:
                rate_limit_message = """
                    Oops! Sorry, I can't talk now. Too many people have used
                    this service recently.
                """
                st.session_state.messages.append(
                    {"role": "assistant", "content": rate_limit_message}
                )
                st.rerun()