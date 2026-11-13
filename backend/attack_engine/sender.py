"""Send prompts to chatbot endpoints and extract their response text."""

import json
from urllib.parse import urlsplit, urlunsplit

import httpx


def target_endpoints(url: str):
    """Use an explicit API path as-is, or try common paths for a site origin."""
    parsed = urlsplit(url.strip())
    path = parsed.path.rstrip("/")
    if path:
        return [url.rstrip("/")]

    origin = urlunsplit((parsed.scheme, parsed.netloc, "", parsed.query, ""))
    return [
        f"{origin}/api/chat",
        f"{origin}/chat",
        f"{origin}/v1/chat/completions",
        origin,
    ]


def response_content(response: httpx.Response) -> str:
    """Extract common chatbot response formats while preserving unknown JSON."""
    if not 200 <= response.status_code < 300:
        return f"[ERROR: HTTP {response.status_code}]"

    try:
        data = response.json()
    except ValueError:
        return response.text.strip()

    if isinstance(data, str):
        return data.strip()

    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            choice = choices[0]
            message = choice.get("message")
            if isinstance(message, dict) and message.get("content") is not None:
                content = message["content"]
                if isinstance(content, list):
                    text_parts = [
                        part.get("text", "")
                        for part in content
                        if isinstance(part, dict) and part.get("type") == "text"
                    ]
                    return "\n".join(part for part in text_parts if part).strip()
                return str(content).strip()
            if choice.get("text") is not None:
                return str(choice["text"]).strip()

        for key in ("reply", "response", "message", "text", "answer", "output"):
            value = data.get(key)
            if value is not None and not isinstance(value, (dict, list)):
                return str(value).strip()
        for key in ("data", "result"):
            nested = data.get(key)
            if isinstance(nested, dict):
                nested_response = response_content(
                    httpx.Response(200, json=nested)
                )
                if nested_response != json.dumps(nested, ensure_ascii=False):
                    return nested_response

    return json.dumps(data, ensure_ascii=False)


def request_headers(auth_token: str = None):
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = (
            auth_token
            if auth_token.lower().startswith("bearer ")
            else f"Bearer {auth_token}"
        )
    return headers


def send_to_target(
    url: str, payload: str, auth_token: str = None, timeout: int = 30
) -> str:
    """
    Send one message to the configured endpoint.

    A URL with an API path is used as provided. For a bare origin (including one
    ending in `/`), common chat paths are tried. A 400/422 on an explicit
    endpoint also triggers one retry with the OpenAI-compatible request shape.
    """
    headers = request_headers(auth_token)
    endpoints = target_endpoints(url)
    last_error = "[ERROR: No endpoint responded successfully]"

    for endpoint in endpoints:
        bodies = [
            {"message": payload},
            {
                "messages": [{"role": "user", "content": payload}],
                "max_tokens": 500,
            },
        ]
        for body_index, body in enumerate(bodies):
            try:
                with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                    response = client.post(endpoint, headers=headers, json=body)
                result = response_content(response)
                if not result.startswith("[ERROR:"):
                    return result
                last_error = result
                if response.status_code in (401, 403, 429) or response.status_code >= 500:
                    return result
                if response.status_code in (404, 405):
                    break
                if body_index == 1:
                    break
            except httpx.TimeoutException:
                last_error = "[ERROR: Request timed out]"
                break
            except httpx.ConnectError:
                last_error = "[ERROR: Connection refused]"
                break
            except httpx.RequestError as exc:
                last_error = f"[ERROR: {type(exc).__name__}]"
                break

    return last_error
