import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")