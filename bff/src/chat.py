"""
bff/src/chat.py (Corrected for Session Management)

FastAPI router for the main chat functionality. The endpoint now accepts an
optional context_id to support stateful, multi-turn conversations.
"""
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Query 
from fastapi.responses import StreamingResponse
from .schemas import ChatMessageInput, ChatMessageOutput
from .service import A2AService

router = APIRouter()
logger = logging.getLogger(__name__)

http_client = httpx.AsyncClient(timeout=300.0)
a2a_service = A2AService(http_client)

@router.post("/chats/{agent_id}/messages")
async def send_message_to_agent(
    agent_id: str,
    message: ChatMessageInput,
    context_id: Optional[str] = Query(None, description="The session ID for an ongoing conversation.")
):
    """
    Endpoint to send a user's message to a specified agent and stream the response.
    This is the primary endpoint for a chat frontend.
    """
    logger.info(f"Received message for agent '{agent_id}' in context '{context_id}'")

    async def stream_generator():
        try:
            async for event in a2a_service.stream_message_to_agent(
                agent_id=agent_id,
                message_content=message.content,
                context_id=context_id
            ):
                yield f"data: {event.model_dump_json()}\n\n"
        except Exception as e:
            logger.exception(f"Stream failed for agent '{agent_id}': {e}")
            error_event = ChatMessageOutput(type="error", content=str(e), context_id=context_id)
            yield f"data: {error_event.model_dump_json()}\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")