import os
from pyngrok import ngrok
from dotenv import load_dotenv
import time

# Load API keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")

ngrok.set_auth_token("2s90dKNY0wM3zgl2Bz0X0yh6ak2_6TkQDxcSy98sqjVGT3T64")

# Start Streamlit in the backgrsound
os.system("streamlit run app.py --server.port 8501 --server.headless true &")

# Give Streamlit a few seconds to start
time.sleep(5)

# Start ngrok tunnel
public_url = ngrok.connect(8501)
print(f"Your app is now live! Open this on your phone (cellular or Wi-Fi): {public_url}")
