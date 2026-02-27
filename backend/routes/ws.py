from __future__ import annotations

import json
import asyncio
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

active_connections: Set[WebSocket] = set()


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
            message = json.loads(data)
            msg_type = message.get("type")

            if msg_type == "ping":
                await send_to(ws, {"type": "pong"})
            elif msg_type == "chat_message":
                from agents.orchestrator import handle_chat_message
                asyncio.create_task(
                    handle_chat_message(ws, message)
                )
            else:
                await send_to(ws, {
                    "type": "error",
                    "payload": {"message": f"Unknown message type: {msg_type}"},
                })
    except WebSocketDisconnect:
        active_connections.discard(ws)
    except Exception:
        active_connections.discard(ws)
