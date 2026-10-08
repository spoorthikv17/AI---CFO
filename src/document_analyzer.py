import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=API_KEY)


MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.8-flash",
]


def analyze_document(file_path: str):

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
    }

    mime_type = mime_types.get(path.suffix.lower())

    if not mime_type:
        raise ValueError(
            "Unsupported file type. "
            "Use JPG, JPEG, PNG, WEBP, or PDF."
        )

    with open(path, "rb") as file:
        file_data = file.read()

    if not file_data:
        raise ValueError("The uploaded file is empty.")

    prompt = """
You are a financial document extraction system.

Analyze this receipt, bill, or invoice carefully.

Extract ONLY information that is actually visible.
Do not invent missing information.

Return ONLY valid JSON using exactly this structure:

{
    "vendor": null,
    "date": null,
    "invoice_number": null,
    "category": null,
    "currency": "INR",
    "items": [
        {
            "name": null,
            "quantity": null,
            "unit_price": null,
            "amount": null
        }
    ],
    "subtotal": null,
    "tax": null,
    "discount": null,
    "total": null,
    "payment_method": null,
    "confidence": null,
    "notes": null
}

Rules:

- Use null when information is unavailable.
- Do not guess.
- Preserve actual monetary values.
- Extract GST/tax if visible.
- Total must be the final payable amount when clearly shown.
- Confidence must be between 0 and 1.
- Use simple categories such as:
  Groceries, Food, Office, Utilities, Travel,
  Software, Marketing, Salaries, Equipment, Other.
- Return JSON only.
"""

    last_error = None

    # Try each available model
    for model in MODELS:

        for attempt in range(2):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=[
                        types.Part.from_bytes(
                            data=file_data,
                            mime_type=mime_type
                        ),
                        prompt,
                    ],
                )

                if not response or not response.text:
                    raise ValueError(
                        "Gemini returned an empty response."
                    )

                text = response.text.strip()

                # Remove markdown code blocks
                if text.startswith("```json"):
                    text = text[7:]

                elif text.startswith("```"):
                    text = text[3:]

                if text.endswith("```"):
                    text = text[:-3]

                text = text.strip()

                result = json.loads(text)

                # Ensure expected fields exist
                defaults = {
                    "vendor": None,
                    "date": None,
                    "invoice_number": None,
                    "category": None,
                    "currency": "INR",
                    "items": [],
                    "subtotal": None,
                    "tax": None,
                    "discount": None,
                    "total": None,
                    "payment_method": None,
                    "confidence": None,
                    "notes": None,
                }

                for key, value in defaults.items():
                    if key not in result:
                        result[key] = value

                return result

            except Exception as error:

                last_error = error
                error_text = str(error)

                is_capacity_error = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "high demand" in error_text.lower()
                )

                if is_capacity_error:

                    # Short retry on same model
                    if attempt == 0:
                        time.sleep(3)
                        continue

                    # Move to next model
                    break

                # Don't hide other errors
                raise

    # All models failed
    raise RuntimeError(
        "Gemini is temporarily unavailable on all configured "
        "Flash models. Please try the receipt again in a few "
        "minutes.\n\n"
        f"Last error: {last_error}"
    )