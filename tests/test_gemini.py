import json

import pytest
import requests

from app.services.gemini import GeminiClient, GeminiError, get_gemini_client


class FakeResponse:
    def __init__(self, text):
        self.text = text
        self.request_arguments = None

    def json(self):
        return {
            "candidates": [
                {"content": {"parts": [{"text": self.text}]}}
            ]
        }

    def raise_for_status(self):
        pass


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.request_arguments = None

    def post(self, *args, **kwargs):
        self.request_arguments = (args, kwargs)
        return self.response


def test_generate_text_sends_prompt_and_api_key():
    session = FakeSession(FakeResponse("Gemini says hello."))
    client = GeminiClient("test-key")
    client.session = session

    result = client.generate("Say hello")

    assert result == "Gemini says hello."
    args, kwargs = session.request_arguments
    assert args[0].endswith(":generateContent")
    assert kwargs["params"] == {"key": "test-key"}
    assert kwargs["json"]["contents"][0]["parts"][0]["text"] == "Say hello"
    assert "responseMimeType" not in kwargs["json"]["generationConfig"]


def test_generate_json_requests_json_and_decodes_result():
    expected = {"answer": 42}
    session = FakeSession(FakeResponse(json.dumps(expected)))
    client = GeminiClient("test-key")
    client.session = session

    result = client.generate("Return an answer", "json")

    assert result == expected
    assert (
        session.request_arguments[1]["json"]["generationConfig"]["responseMimeType"]
        == "application/json"
    )


def test_generate_rejects_invalid_json():
    client = GeminiClient("test-key")
    client.session = FakeSession(FakeResponse("not json"))

    with pytest.raises(GeminiError, match="invalid JSON"):
        client.generate("Return JSON", "json")


def test_generate_rejects_empty_gemini_response():
    client = GeminiClient("test-key")
    client.session = FakeSession(FakeResponse(""))

    with pytest.raises(GeminiError, match="empty response"):
        client.generate("Say hello")


def test_missing_api_key_is_reported(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(GeminiError, match="GEMINI_API_KEY is not configured"):
        get_gemini_client()


def test_gemini_request_errors_are_reported_without_retrying_in_test(monkeypatch):
    monkeypatch.setattr("app.services.gemini.GEMINI_MAX_RETRIES", 0)

    class FailingSession:
        def post(self, *args, **kwargs):
            raise requests.Timeout()

    client = GeminiClient("test-key")
    client.session = FailingSession()

    with pytest.raises(GeminiError, match="timed out"):
        client.generate("Say hello")
