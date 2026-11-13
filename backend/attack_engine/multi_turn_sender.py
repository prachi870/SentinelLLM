"""Send multi-turn conversations to chatbot endpoints."""

from typing import Dict, List
from urllib.parse import urlsplit

import httpx

from attack_engine.sender import (
    request_headers,
    response_content,
    target_endpoints,
)


def send_multi_turn(
    url: str,
    turns: List[str],
    auth_token: str = None,
    timeout: int = 30,
) -> List[Dict[str, str]]:
    """
    Send conversation turns and return each prompt with the response received.

    Base URLs are routed through the same common chat-path selection as
    single-turn scans. Non-OpenAI endpoints receive a `message` body first;
    OpenAI-compatible endpoints receive the accumulated `messages` history.
    """
    headers = request_headers(auth_token)
    has_explicit_path = bool(urlsplit(url.strip()).path.rstrip("/"))
    history: List[Dict[str, str]] = []
    results: List[Dict[str, str]] = []

    for turn_prompt in turns:
        history.append({"role": "user", "content": turn_prompt})
        messages_body = {"messages": list(history), "max_tokens": 500}
        content = "[ERROR: No endpoint responded successfully]"

        for endpoint in target_endpoints(url):
            stop_after_endpoint = False
            if has_explicit_path or endpoint.rstrip("/").endswith(
                "/v1/chat/completions"
            ):
                bodies = [messages_body, {"message": turn_prompt}]
            else:
                bodies = [{"message": turn_prompt}, messages_body]

            for body in bodies:
                try:
                    with httpx.Client(
                        timeout=timeout, follow_redirects=True
                    ) as client:
                        response = client.post(endpoint, headers=headers, json=body)
                    content = response_content(response)
                except httpx.TimeoutException:
                    content = "[ERROR: Request timed out]"
                    stop_after_endpoint = True
                    break
                except httpx.ConnectError:
                    content = "[ERROR: Connection refused]"
                    stop_after_endpoint = True
                    break
                except httpx.RequestError as exc:
                    content = f"[ERROR: {type(exc).__name__}]"
                    stop_after_endpoint = True
                    break

                if not content.startswith("[ERROR:"):
                    break
                if response.status_code in (401, 403, 429) or response.status_code >= 500:
                    stop_after_endpoint = True
                    break
                if response.status_code in (404, 405):
                    break

            if not content.startswith("[ERROR:"):
                break
            if stop_after_endpoint:
                break

        results.append({"prompt": turn_prompt, "response": content})
        if content.startswith("[ERROR:"):
            break
        history.append({"role": "assistant", "content": content})

    return results
