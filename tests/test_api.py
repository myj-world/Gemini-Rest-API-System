def test_homepage_shows_gemini_system(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Gemini REST API System" in response.data


def test_icon_is_served(client):
    response = client.get("/icon.png")

    assert response.status_code == 200
    assert response.mimetype == "image/png"


def test_health_reports_service_and_key_status(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json == {
        "status": "ok",
        "service": "Gemini REST API System",
        "gemini_api_key_configured": True,
    }


def test_generate_text(client, monkeypatch):
    class FakeGeminiClient:
        def generate(self, prompt, response_format):
            assert prompt == "Say hello"
            assert response_format == "text"
            return "Hello!"

    monkeypatch.setattr(
        "app.routes.generate.get_gemini_client", lambda: FakeGeminiClient()
    )

    response = client.post(
        "/api/generate",
        json={"prompt": "Say hello"},
    )

    assert response.status_code == 200
    assert response.json == {
        "response_format": "text",
        "response": "Hello!",
    }


def test_generate_json(client, monkeypatch):
    class FakeGeminiClient:
        def generate(self, prompt, response_format):
            assert response_format == "json"
            return {"greeting": "Hello"}

    monkeypatch.setattr(
        "app.routes.generate.get_gemini_client", lambda: FakeGeminiClient()
    )

    response = client.post(
        "/api/generate",
        json={"prompt": "Return a greeting", "response_format": "json"},
    )

    assert response.status_code == 200
    assert response.json == {
        "response_format": "json",
        "response": {"greeting": "Hello"},
    }


def test_generate_rejects_invalid_requests(client):
    cases = [
        ([], "Request body must be a JSON object"),
        ({"prompt": "   "}, "prompt must be a non-empty string"),
        (
            {"prompt": "Hello", "response_format": "xml"},
            "response_format must be 'text' or 'json'",
        ),
    ]

    for body, message in cases:
        response = client.post("/api/generate", json=body)
        assert response.status_code == 400
        assert response.json["error"] == message
