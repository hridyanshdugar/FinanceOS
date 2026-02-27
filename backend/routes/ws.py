from __future__ import annotations

import json
import asyncio
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

active_connections: Set[WebSocket] = set()

MAX_MESSAGE_SIZE = 10_000
VALID_TYPES = {"ping", "chat_message"}


async def broadcast(message: dict):
    """Send a message to all connected WebSocket clients."""
    dead = set()
    for ws in active_connections:
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(ws)
    active_connections.difference_update(dead)


async def send_to(ws: WebSocket, message: dict):
    """Send a message to a specific WebSocket client."""
    try:
        await ws.send_json(message)
    except Exception:
        active_connections.discard(ws)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    active_connections.add(ws)
    try:
        while True:
            data = await ws.receive_text()

            if len(data) > MAX_MESSAGE_SIZE:
                await send_to(ws, {
                    "type": "error",
                    "payload": {"message": "Message too large"},
                })
                continue

            try:
                message = json.loads(data)
            except (json.JSONDecodeError, ValueError):
                await send_to(ws, {
                    "type": "error",
                    "payload": {"message": "Invalid JSON"},
                })
                continue

            if not isinstance(message, dict):
                await send_to(ws, {
                    "type": "error",
                    "payload": {"message": "Message must be a JSON object"},
                })
                continue

            msg_type = message.get("type")

            if msg_type not in VALID_TYPES:
                await send_to(ws, {
                    "type": "error",
                    "payload": {"message": f"Unknown message type: {msg_type}"},
                })
                continue

            if msg_type == "ping":
                await send_to(ws, {"type": "pong"})
            elif msg_type == "chat_message":
                client_id = message.get("client_id")
                content = message.get("content", "")

                if not isinstance(client_id, str) or not client_id.strip():
                    await send_to(ws, {
                        "type": "error",
                        "payload": {"message": "Missing or invalid client_id"},
                    })
                    continue

                if not isinstance(content, str) or not content.strip():
                    await send_to(ws, {
                        "type": "error",
                        "payload": {"message": "Missing or empty content"},
                    })
                    continue

                if len(content) > 5000:
                    await send_to(ws, {
                        "type": "error",
                        "payload": {"message": "Message content too long (max 5000 chars)"},
                    })
                    continue

                from agents.orchestrator import handle_chat_message
                asyncio.create_task(handle_chat_message(ws, message))

    except WebSocketDisconnect:
        active_connections.discard(ws)
    except Exception:
        active_connections.discard(ws)
