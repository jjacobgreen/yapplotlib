"""
Tests for rendering common OpenAI message and response shapes.
"""

import matplotlib.text as mtext

import yapplotlib
from yapplotlib._messages import normalize_messages


def _rendered_texts(ax):
    return [artist.get_text() for artist in ax.get_children() if isinstance(artist, mtext.Text)]


class TestOpenAIChatCompletions:
    def test_assistant_tool_calls_render_as_tool_call_bubbles(self):
        messages = [
            {"role": "user", "content": "What is the weather in Paris?"},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_123",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": '{"location":"Paris","unit":"celsius"}',
                        },
                    }
                ],
            },
        ]

        normalized = normalize_messages(messages)

        assert normalized[-1]["role"] == "tool_call"
        assert normalized[-1]["name"] == "Tool call: get_weather"
        assert "arguments:" in normalized[-1]["content"]
        assert '"location":"Paris"' in normalized[-1]["content"]

    def test_tool_role_messages_render_as_tool_result_bubbles(self):
        messages = [
            {
                "role": "tool",
                "tool_call_id": "call_123",
                "content": '{"temperature": 18, "condition": "cloudy"}',
            }
        ]

        normalized = normalize_messages(messages)

        assert normalized == [
            {
                "role": "tool_result",
                "name": "Tool result: call_123",
                "content": '{"temperature": 18, "condition": "cloudy"}',
            }
        ]


class TestOpenAIResponses:
    def test_response_output_items_render_reasoning_and_function_calls(self):
        response = {
            "output": [
                {
                    "type": "reasoning",
                    "summary": [{"type": "summary_text", "text": "Need current weather."}],
                },
                {
                    "type": "function_call",
                    "call_id": "call_abc",
                    "name": "get_weather",
                    "arguments": '{"location":"Paris"}',
                },
                {
                    "type": "function_call_output",
                    "call_id": "call_abc",
                    "output": '{"temperature": 18}',
                },
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "It is 18 C in Paris."}],
                },
            ]
        }

        normalized = normalize_messages(response)

        assert [message["role"] for message in normalized] == [
            "reasoning",
            "tool_call",
            "tool_result",
            "assistant",
        ]
        assert normalized[0]["content"] == "Need current weather."
        assert normalized[1]["name"] == "Tool call: get_weather"
        assert normalized[2]["content"] == '{"temperature": 18}'
        assert normalized[3]["content"] == "It is 18 C in Paris."

    def test_chatplot_accepts_openai_response_objects(self):
        response = {
            "output": [
                {
                    "type": "reasoning",
                    "summary": [{"type": "summary_text", "text": "Use arithmetic."}],
                },
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "2 + 2 = 4."}],
                },
            ]
        }

        fig, ax = yapplotlib.chatplot(response)
        texts = _rendered_texts(ax)

        assert "Reasoning" in texts
        assert "Use arithmetic." in texts
        assert "2 + 2 = 4." in texts

    def test_chat_completions_response_choices_are_supported(self):
        response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Calling a tool.",
                        "tool_calls": [
                            {
                                "type": "function",
                                "function": {"name": "lookup", "arguments": '{"q":"weather"}'},
                            }
                        ],
                    }
                }
            ]
        }

        normalized = normalize_messages(response)

        assert normalized[0]["role"] == "assistant"
        assert normalized[1]["role"] == "tool_call"
        assert normalized[1]["name"] == "Tool call: lookup"

    def test_reasoning_role_messages_can_be_rendered_explicitly(self):
        fig, ax = yapplotlib.chatplot(
            [
                {"role": "reasoning", "name": "Reasoning", "content": "Use arithmetic."},
                {"role": "assistant", "content": "2 + 2 = 4."},
            ]
        )
        texts = _rendered_texts(ax)

        assert "Reasoning" in texts
        assert "Use arithmetic." in texts
