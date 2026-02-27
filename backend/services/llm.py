"""
LLM client wrappers for Claude (Anthropic) and GPT-4o (OpenAI).
Claude: orchestration, empathy, context analysis, draft messages, compliance.
GPT-4o: quantitative analysis, Python code generation, math reasoning.
"""
from __future__ import annotations

import json
import asyncio
from functools import lru_cache
from typing import Optional

from config import ANTHROPIC_API_KEY, OPENAI_API_KEY


@lru_cache()
def _get_anthropic_client():
    from anthropic import Anthropic
    return Anthropic(api_key=ANTHROPIC_API_KEY)


@lru_cache()
def _get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY)


async def call_claude(
    system: str,
    user_message: str,
    model: str = "claude-sonnet-4-20250514",
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
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 2048,
    temperature: float = 0.2,
) -> dict:
    """Call Claude and parse the response as JSON."""
    raw = await call_claude(system, user_message, model, max_tokens, temperature)
    # Strip markdown code fences if present
    text = raw.strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        last_fence = text.rfind("```")
        text = text[first_newline + 1:last_fence].strip()
    return json.loads(text)


async def call_gpt4o(
    system: str,
    user_message: str,
    model: str = "gpt-4o",
    max_tokens: int = 2048,
    temperature: float = 0.2,
) -> str:
    """Call GPT-4o and return the text response."""
    client = _get_openai_client()
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


async def call_gpt4o_json(
    system: str,
    user_message: str,
    model: str = "gpt-4o",
    max_tokens: int = 2048,
    temperature: float = 0.2,
) -> dict:
    """Call GPT-4o and parse the response as JSON."""
    client = _get_openai_client()
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
    )
    return json.loads(response.choices[0].message.content)
