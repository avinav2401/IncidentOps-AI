"""SSE stream router for real-time AI pipeline updates.

Clients connect to ``/api/v1/incidents/{id}/stream`` to receive
Server-Sent Events as the multi-agent pipeline processes an incident.
Adapted from IncidentFox's production SSE streaming architecture.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.events import StreamEvent
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(tags=["Stream"])

# ── In-process event bus ──────────────────────────────────────────────
# Maps incident_id → list of asyncio.Queue subscribers.
# In production you'd back this with Redis pub/sub, but for a single-
# process deployment this is perfectly adequate.

_subscribers: dict[str, list[asyncio.Queue[StreamEvent | None]]] = defaultdict(list)


def publish(event: StreamEvent) -> None:
    """Push an event to all subscribers for the given incident."""
    for queue in _subscribers.get(event.incident_id, []):
        queue.put_nowait(event)


def close_stream(incident_id: str) -> None:
    """Signal all subscribers that the stream is done."""
    for queue in _subscribers.get(incident_id, []):
        queue.put_nowait(None)  # Sentinel value


async def _event_generator(
    incident_id: str,
    queue: asyncio.Queue[StreamEvent | None],
) -> AsyncGenerator[str, None]:
    """Yield SSE-formatted events until the stream is closed."""
    try:
        while True:
            event = await asyncio.wait_for(queue.get(), timeout=120.0)
            if event is None:
                # Stream finished
                yield "data: {\"type\": \"done\"}\n\n"
                return
            yield event.to_sse()
    except TimeoutError:
        yield "data: {\"type\": \"keepalive\"}\n\n"
    finally:
        # Unsubscribe
        subs = _subscribers.get(incident_id, [])
        if queue in subs:
            subs.remove(queue)
        if not subs:
            _subscribers.pop(incident_id, None)


@router.get(
    "/incidents/{incident_id}/stream",
    summary="Stream AI pipeline events (SSE)",
    response_class=StreamingResponse,
)
async def stream_pipeline(
    incident_id: str,
    _user: User = Depends(get_current_user),
) -> StreamingResponse:
    """Subscribe to real-time SSE updates for an incident's AI pipeline.

    The client receives structured JSON events as the pipeline runs:
    ``thought``, ``agent_start``, ``agent_end``, ``result``, ``error``,
    ``approval``.
    """
    queue: asyncio.Queue[StreamEvent | None] = asyncio.Queue()
    _subscribers[incident_id].append(queue)

    return StreamingResponse(
        _event_generator(incident_id, queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
