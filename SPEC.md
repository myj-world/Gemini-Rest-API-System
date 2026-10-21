# Gemini REST API System specification

## Purpose

Provide a simple browser interface and REST endpoint for sending a user's prompt to the Gemini API and displaying the generated result as text or JSON.

## Web interface

- Display the system name, existing project icon, prompt input, response-format selector, and generate action.
- Support regular text and JSON output.
- Display the complete result without interpreting model-generated HTML.
- Display request errors and a loading state; allow copying the response.
- Never send the Gemini API key to the browser.

## REST API

### `POST /api/generate`

Request body:

```json
{
  "prompt": "A prompt for Gemini",
  "response_format": "text"
}
```

`prompt` must be a non-empty string. `response_format` may be `text` or `json`; if omitted it defaults to `text`.

Successful response:

```json
{
  "response_format": "text",
  "response": "Generated text"
}
```

For `json`, `response` is the decoded JSON value returned by Gemini. Invalid input returns HTTP 400. Missing API configuration or Gemini failures return HTTP 503 with an `error` string.

### `GET /api/health`

Returns service status and whether `GEMINI_API_KEY` is configured. It does not return the key itself.

## Configuration and runtime

- `GEMINI_API_KEY` is required and server-only.
- `GEMINI_MODEL`, `GEMINI_TIMEOUT_SECONDS`, `GEMINI_MAX_RETRIES`, `PORT`, and `GUNICORN_TIMEOUT` are optional.
- Flask serves the UI and API. Gunicorn is the production WSGI server.
