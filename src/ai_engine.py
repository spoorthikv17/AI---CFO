import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.8-flash"


def ask_gemini(prompt: str) -> str:
    """
    Send a text prompt to Gemini and return the AI response.
    """

    try:
        response = client.interactions.create(
            model=MODEL_NAME,
            input=prompt,
        )

        return response.output_text

    except Exception as error:
        print(f"Gemini request failed: {error}")
        return (
            "Gemini is temporarily unavailable. "
            "Please try again shortly."
        )