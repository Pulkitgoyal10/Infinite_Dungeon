import os
from dotenv import load_dotenv
import google.generativeai as genai

print("🚀 Starting Gemini Test...")

# Load .env
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("❌ GOOGLE_API_KEY not found in .env file")
    exit()

print("🔑 API Key Loaded Successfully")

# Configure Gemini
genai.configure(api_key=API_KEY)

try:
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content("Say OK if you are working.")

    print("✅ Gemini Response:")
    print(response.text)

except Exception as e:
    print("❌ Gemini Error:")
    print(e)