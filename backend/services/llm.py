"""
LLM client wrapper for Claude (Anthropic).
Haiku 3.5 handles fast routing and classification tasks.
Sonnet 4 handles substantive agent work and user-facing output.
Web-search-enabled variants let Claude autonomously search the web.
"""
from __future__ import annotations

import json
import asyncio
from functools import lru_cache

from config import ANTHROPIC_API_KEY

MODEL_HAIKU = "claude-haiku-3-5-20241022"
MODEL_SONNET = "claude-sonnet-4-20250514"

WEB_SEARCH_TOOL = {"type": "web_search_20250305", "name": "web_search"}


@lru_cache()
def _get_anthropic_client():
    from anthropic import Anthropic
    return Anthropic(api_key=ANTHROPIC_API_KEY)


def _extract_text(response) -> str:
    """Extract concatenated text from a response that may contain mixed content blocks."""
    parts = [block.text for block in response.content if hasattr(block, "text")]
    return "\n".join(parts)


def _parse_json(raw: str) -> dict:
    """Strip markdown fences if present and parse JSON."""
    text = raw.strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        last_fence = text.rfind("```")
        text = text[first_newline + 1:last_fence].strip()
    return json.loads(text)


async def call_claude(
    system: str,
    user_message: str,
    model: str = MODEL_SONNET,
    max_tokens: int = 2048,
    temperature: float = 0.3,
) -> str:
    """Call Claude and return the text response."""
    client = _get_anthropic_client()
    response = await asyncio.to_thread(
        client.messages.create,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


async def call_claude_json(
    system: str,
    user_message: str,
    model: str = MODEL_SONNET,
    max_tokens: int = 2048,
    temperature: float = 0.2,
) -> dict:
    """Call Claude and parse the response as JSON."""
    raw = await call_claude(system, user_message, model, max_tokens, temperature)
    return _parse_json(raw)


async def call_claude_with_search(
    system: str,
    user_message: str,
    model: str = MODEL_SONNET,
    max_tokens: int = 4096,
    temperature: float = 0.3,
) -> str:
    """Call Claude with web search enabled. Claude decides when to search."""
    client = _get_anthropic_client()
    response = await asyncio.to_thread(
        client.messages.create,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user_message}],
        tools=[WEB_SEARCH_TOOL],
    )
    return _extract_text(response)


async def call_claude_json_with_search(
    system: str,
    user_message: str,
    model: str = MODEL_SONNET,
    max_tokens: int = 4096,
    temperature: float = 0.2,
) -> dict:
    """Call Claude with web search enabled and parse the response as JSON."""
    raw = await call_claude_with_search(system, user_message, model, max_tokens, temperature)
    return _parse_json(raw)
