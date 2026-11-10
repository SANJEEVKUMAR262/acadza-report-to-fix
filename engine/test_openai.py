
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

if not api_key or api_key == "PASTE_YOUR_ACTUAL_API_KEY_HERE":
    raise RuntimeError("OPENAI_API_KEY is missing from .env")

client = OpenAI(api_key=api_key, timeout=30.0, max_retries=0)

print("API key loaded securely.")
print("Testing model:", model)

try:
    response = client.responses.create(
        model=model,
        input="Reply with exactly: ACADZA API CONNECTED",
        max_output_tokens=30,
        store=False,
    )

    print("Model response:", response.output_text)
    print("API CONNECTION TEST PASSED")


except Exception as exc:
    print("API CONNECTION TEST FAILED")
    print("Error type:", type(exc).__name__)

    body = getattr(exc, "body", None)

    if isinstance(body, dict):
        details = body.get("error", body)

        if isinstance(details, dict):
            print("Error code:", details.get("code"))
            print("Error type detail:", details.get("type"))
        else:
            print("No structured error details available")
    else:
        print("No structured error details available")
