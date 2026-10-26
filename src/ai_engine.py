import os
import logging

from dotenv import load_dotenv
from google import genai
from google.genai import types

# ==================================================
# CONFIGURATION
# ==================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

MODEL_NAME = "gemini-3.5-flash-lite"

REQUEST_TIMEOUT_MS = 60000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = None


# ==================================================
# INITIALIZE CLIENT
# ==================================================

if API_KEY:
    try:
        client = genai.Client(
            api_key=API_KEY,
            http_options=types.HttpOptions(
                timeout=REQUEST_TIMEOUT_MS
            )
        )
        logger.info("Gemini client initialized successfully.")

    except Exception:
        logger.exception("Gemini client initialization failed.")

else:
    logger.error("GEMINI_API_KEY is missing from .env.")


# ==================================================
# GEMINI RESPONSE
# ==================================================

def ask_gemini(prompt: str) -> str:
    """Generate a text response from Gemini."""

    if not isinstance(prompt, str) or not prompt.strip():
        return "Please enter a question."

    if client is None:
        return (
            "Gemini is not configured. "
            "Please check the API key in your .env file."
        )

    try:
        logger.info("Sending prompt to Gemini using %s", MODEL_NAME)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=700,
                thinking_config=types.ThinkingConfig(
                    thinking_level="low"
                )
            )
        )

        answer = response.text

        if answer and answer.strip():
            logger.info("Gemini generated a response.")
            return answer.strip()

        logger.warning("Gemini returned no text. Response: %r", response)

        return (
            "Gemini did not return a text answer. "
            "Please try again."
        )

    except Exception as error:
        logger.exception("Gemini request failed.")

        error_message = str(error).lower()

        if "timeout" in error_message or "timed out" in error_message:
            return (
                "The AI response timed out. "
                "Please try again."
            )

        if "429" in error_message or "quota" in error_message:
            return (
                "Gemini API quota reached. "
                "Please check your API usage."
            )

        if "503" in error_message or "unavailable" in error_message:
            return (
                "Gemini is temporarily unavailable. "
                "Please try again shortly."
            )

        if "api key" in error_message or "401" in error_message:
            return (
                "Gemini authentication failed. "
                "Please verify your API key."
            )

        return (
            f"Gemini request failed: {type(error).__name__}. "
            "Check the terminal for details."
        )


# ==================================================
# TEST CONNECTION
# ==================================================

def test_gemini_connection() -> bool:
    """Verify that Gemini can return generated text."""

    print("\nTesting Gemini connection...\n")

    answer = ask_gemini(
        "Reply with exactly these words: GEMINI WORKING"
    )

    print("Gemini response:", answer)

    if answer.strip() == "GEMINI WORKING":
        print("\nSUCCESS: Gemini is responding correctly.")
        return True

    print("\nFAILED: Gemini did not return the expected response.")
    return False


# ==================================================
# RUN TEST
# ==================================================

if __name__ == "__main__":
    test_gemini_connection()
