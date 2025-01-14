import streamlit as st

# Access environment variables
HUGGING_FACE_TOKEN = st.secrets.get("HUGGING_FACE_TOKEN", "")