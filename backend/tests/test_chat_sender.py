import unittest
from unittest.mock import MagicMock, patch

import httpx

from attack_engine.multi_turn_sender import send_multi_turn
from attack_engine.sender import (
    response_content,
    send_to_target,
    target_endpoints,
)


class ChatSenderTests(unittest.TestCase):
    def test_root_url_with_trailing_slash_uses_common_chat_paths(self):
        self.assertEqual(
            target_endpoints("https://bot.example.com/"),
            [
                "https://bot.example.com/api/chat",
                "https://bot.example.com/chat",
                "https://bot.example.com/v1/chat/completions",
                "https://bot.example.com",
            ],
        )

    def test_explicit_chat_path_is_preserved(self):
        self.assertEqual(
            target_endpoints("https://bot.example.com/api/chat"),
            ["https://bot.example.com/api/chat"],
        )

    def test_extracts_express_response_field(self):
        response = httpx.Response(200, json={"response": "The bot replied."})
        self.assertEqual(response_content(response), "The bot replied.")

    def test_extracts_openai_response_field(self):
        response = httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": "Safe refusal."}}
                ]
            },
        )
        self.assertEqual(response_content(response), "Safe refusal.")

    @patch("attack_engine.sender.httpx.Client")
    def test_retries_openai_body_after_validation_error(self, client_class):
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.side_effect = [
            httpx.Response(422, json={"detail": "Expected messages"}),
            httpx.Response(
                200,
                json={
                    "choices": [
                        {"message": {"role": "assistant", "content": "Hello back."}}
                    ]
                },
            ),
        ]
        client_class.return_value = client

        result = send_to_target("https://bot.example.com/chat", "Hello")

        self.assertEqual(result, "Hello back.")
        self.assertEqual(client.post.call_count, 2)

    @patch("attack_engine.sender.httpx.Client")
    def test_sends_to_common_chat_path_and_uses_bearer_token(self, client_class):
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = httpx.Response(
            200, json={"response": "Actual chatbot response."}
        )
        client_class.return_value = client

        result = send_to_target(
            "https://bot.example.com/",
            "Hello",
            auth_token="secret-token",
        )

        self.assertEqual(result, "Actual chatbot response.")
        args, kwargs = client.post.call_args
        self.assertEqual(args[0], "https://bot.example.com/api/chat")
        self.assertEqual(kwargs["json"], {"message": "Hello"})
        self.assertEqual(
            kwargs["headers"]["Authorization"], "Bearer secret-token"
        )

    @patch("attack_engine.multi_turn_sender.httpx.Client")
    def test_multi_turn_uses_common_chat_path_and_parses_reply(self, client_class):
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = httpx.Response(
            200, json={"response": "Actual multi-turn response."}
        )
        client_class.return_value = client

        result = send_multi_turn(
            "https://bot.example.com/",
            ["Hello"],
        )

        self.assertEqual(
            result,
            [{"prompt": "Hello", "response": "Actual multi-turn response."}],
        )
        self.assertEqual(
            client.post.call_args.args[0],
            "https://bot.example.com/api/chat",
        )

    @patch("attack_engine.multi_turn_sender.httpx.Client")
    def test_multi_turn_keeps_existing_body_order_for_explicit_endpoint(
        self, client_class
    ):
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.side_effect = [
            httpx.Response(400, json={"error": "Expected message"}),
            httpx.Response(200, json={"response": "Actual response."}),
        ]
        client_class.return_value = client

        result = send_multi_turn(
            "https://bot.example.com/api/chat",
            ["Hello"],
        )

        self.assertEqual(result[0]["response"], "Actual response.")
        first_body = client.post.call_args_list[0].kwargs["json"]
        second_body = client.post.call_args_list[1].kwargs["json"]
        self.assertEqual(
            first_body,
            {"messages": [{"role": "user", "content": "Hello"}], "max_tokens": 500},
        )
        self.assertEqual(second_body, {"message": "Hello"})


if __name__ == "__main__":
    unittest.main()
