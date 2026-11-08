print("DEBUG: Script started...")
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
print("DEBUG: Environment loaded, building client...")
client = genai.Client(api_key=os.getenv("apiKey"))
print("DEBUG: Client ready, calling Gemini 3.8 Flash...")

try:
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents="Hello, test connection."
    )
    print("Connection successful:", response.text)
except Exception as e:
    print("Connection failed:", e)