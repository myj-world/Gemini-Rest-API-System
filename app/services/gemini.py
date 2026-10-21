import json
import os
import time

import requests

from app.config import GEMINI_API_URL, GEMINI_TIMEOUT_SECONDS, GEMINI_MAX_RETRIES


class GeminiError(Exception):
    """Raised when the Gemini REST API cannot produce a valid response."""


class GeminiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def generate(self, prompt: str, response_format: str = "text"):
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }
        if response_format == "json":
            payload["generationConfig"]["responseMimeType"] = "application/json"

        last_error = "Gemini request failed"
        for attempt in range(GEMINI_MAX_RETRIES + 1):
            try:
                response = self.session.post(
                    GEMINI_API_URL,
                    params={"key": self.api_key},
                    json=payload,
                    timeout=GEMINI_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                text = _extract_text(response.json())
                if response_format == "json":
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError as exc:
                        raise GeminiError(f"Gemini returned invalid JSON: {exc.msg}") from exc
                return text
            except requests.Timeout:
                last_error = f"Gemini request timed out (attempt {attempt + 1})"
            except requests.RequestException as exc:
                status = exc.response.status_code if exc.response is not None else None
                last_error = (
                    f"Gemini API returned HTTP {status}"
                    if status is not None
                    else "Gemini API request failed"
                )
            except ValueError as exc:
                raise GeminiError(f"Gemini returned an invalid API response: {exc}") from exc

            if attempt < GEMINI_MAX_RETRIES:
                time.sleep(2 ** attempt)

        raise GeminiError(last_error or "Gemini review failed")


def _extract_text(payload: dict) -> str:
    try:
        parts = payload["candidates"][0]["content"]["parts"]
        text = "".join(part["text"] for part in parts if "text" in part).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiError("Gemini returned an empty or malformed response") from exc
    if not text:
        raise GeminiError("Gemini returned an empty response")
    return text


def get_gemini_client() -> GeminiClient:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise GeminiError("GEMINI_API_KEY is not configured")
    return GeminiClient(key)
