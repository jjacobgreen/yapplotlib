"""
Message normalization for common chat transcript formats.
"""

import json


def normalize_messages(messages):
    """
    Normalize yapplotlib and OpenAI message shapes into renderable messages.

    Supports the native yapplotlib ``list[dict]`` format, OpenAI Chat
    Completions messages/responses, and OpenAI Responses API objects.
    """
    if isinstance(messages, dict):
        if "output" in messages:
            return _normalize_sequence(messages["output"])
        if "choices" in messages:
            return _normalize_sequence(_messages_from_choices(messages["choices"]))
        return _normalize_sequence([messages])
    return _normalize_sequence(messages)


def _normalize_sequence(messages):
    normalized = []
    for message in messages:
        normalized.extend(_normalize_one(message))
    return normalized


def _normalize_one(message):
    if not isinstance(message, dict):
        return [{"role": "other", "content": str(message)}]

    role = message.get("role")
    item_type = message.get("type")
    if item_type == "reasoning":
        return _normalize_reasoning_item(message)
    if item_type == "function_call":
        return [_tool_call_message(message)]
    if item_type == "function_call_output":
        return [_tool_result_message(message)]
    if item_type == "message":
        return [_plain_message(message)]

    if role == "tool":
        return [_tool_result_message(message)]
    if role == "function":
        return [_legacy_function_result_message(message)]

    result = []
    content = _content_to_text(message.get("content", ""))
    if content:
        result.append({**message, "content": content})
    elif not message.get("tool_calls"):
        result.append({**message, "content": ""})

    for call in message.get("tool_calls", []) or []:
        result.append(_tool_call_message(call))
    return result


def _plain_message(message):
    return {
        **message,
        "content": _content_to_text(message.get("content", "")),
    }


def _normalize_reasoning_item(message):
    summary = _content_to_text(message.get("summary", ""))
    content = _content_to_text(message.get("content", ""))
    visible = summary or content
    if not visible:
        return []
    return [{"role": "reasoning", "name": "Reasoning", "content": visible}]


def _tool_call_message(call):
    function = call.get("function", {}) if isinstance(call.get("function"), dict) else {}
    name = call.get("name") or function.get("name") or call.get("type", "tool")
    arguments = call.get("arguments", function.get("arguments", ""))
    content = _format_payload("arguments", arguments)
    return {"role": "tool_call", "name": f"Tool call: {name}", "content": content}


def _tool_result_message(message):
    call_id = message.get("call_id") or message.get("tool_call_id") or message.get("id")
    label = f"Tool result: {call_id}" if call_id else "Tool result"
    output = message.get("output", message.get("content", ""))
    return {"role": "tool_result", "name": label, "content": _content_to_text(output)}


def _legacy_function_result_message(message):
    name = message.get("name")
    label = f"Function result: {name}" if name else "Function result"
    return {"role": "tool_result", "name": label, "content": _content_to_text(message.get("content", ""))}


def _messages_from_choices(choices):
    messages = []
    for choice in choices:
        if isinstance(choice, dict) and isinstance(choice.get("message"), dict):
            messages.append(choice["message"])
    return messages


def _content_to_text(content):
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [_content_part_to_text(part) for part in content]
        return "\n".join(part for part in parts if part)
    return _json_or_str(content)


def _content_part_to_text(part):
    if isinstance(part, str):
        return part
    if not isinstance(part, dict):
        return _json_or_str(part)
    if "text" in part:
        return str(part["text"])
    if "output" in part:
        return _content_to_text(part["output"])
    return ""


def _format_payload(label, value):
    text = _content_to_text(value)
    return f"{label}: {text}" if text else f"{label}:"


def _json_or_str(value):
    try:
        return json.dumps(value, ensure_ascii=False)
    except TypeError:
        return str(value)
