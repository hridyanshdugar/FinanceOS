"""
LLM client wrapper for Claude (Anthropic).
Haiku 4.5 handles fast routing and classification tasks.
Sonnet 5 handles substantive agent work and user-facing output.
"""
from __future__ import annotations

import json
import asyncio
from functools import lru_cache

from config import ANTHROPIC_API_KEY

MODEL_HAIKU = "claude-haiku-4-5-20251001"
MODEL_SONNET = "claude-sonnet-5"


@lru_cache()
def _get_anthropic_client():
    from anthropic import Anthropic
    return Anthropic(api_key=ANTHROPIC_API_KEY)


def _extract_text(response) -> str:
    """Extract concatenated text from a response that may contain mixed content blocks.

    Sonnet 5+ may return ThinkingBlock(s) before TextBlock(s); only text blocks
    are included.
    """
    parts = []
    for block in response.content:
        block_type = getattr(block, "type", None)
        if block_type == "text" or (block_type is None and hasattr(block, "text")):
            parts.append(block.text)
        elif isinstance(block, dict) and block.get("type", "text") == "text" and "text" in block:
            parts.append(block["text"])
    return "\n".join(parts)


def _parse_json(raw: str) -> dict:
    """Strip markdown fences if present and parse JSON."""
    text = raw.strip()
    if not text:
        raise ValueError("Empty response from LLM — no JSON to parse")
    if text.startswith("```"):
        first_newline = text.index("\n")
        last_fence = text.rfind("```")
        text = text[first_newline + 1:last_fence].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]
    return json.loads(text)


def _sonnet_request_kwargs(model: str) -> dict:
    """Sonnet 5 enables adaptive thinking by default; thinking tokens count against
    max_tokens and often starve short/JSON responses. Disable for our agent use case.
    """
    if (
        model.startswith("claude-sonnet-5")
        or model.startswith("claude-fable")
        or model.startswith("claude-opus-4-8")
        or model.startswith("claude-opus-4-7")
    ):
        return {"thinking": {"type": "disabled"}}
    return {}


async def call_claude(
    system: str,
    user_message: str,
    model: str = MODEL_SONNET,
    max_tokens: int = 4096,
) -> str:
    """Call Claude and return the text response.

    Sampling params (temperature/top_p/top_k) are omitted — Sonnet 5 and
    newer Opus models reject them; prompt for style instead.
    """
    client = _get_anthropic_client()
    response = await asyncio.to_thread(
        client.messages.create,
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_message}],
        **_sonnet_request_kwargs(model),
    )
    text = _extract_text(response)
    if not text.strip():
        raise ValueError(
            f"Empty text from {model} (stop_reason={getattr(response, 'stop_reason', None)})"
        )
    return text


async def call_claude_json(
    system: str,
    user_message: str,
    model: str = MODEL_SONNET,
    max_tokens: int = 4096,
) -> dict:
    """Call Claude and parse the response as JSON."""
    raw = await call_claude(system, user_message, model, max_tokens)
    return _parse_json(raw)
