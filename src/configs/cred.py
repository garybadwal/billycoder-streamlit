from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN", "")