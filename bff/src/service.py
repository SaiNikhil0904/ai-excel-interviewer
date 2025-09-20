"""
bff/src/service.py (Corrected for Session Management)

Contains the client-side logic for communicating with A2A agents. This version
is updated to use the correct A2AClient initialization and message construction
patterns to ensure stateful conversations are maintained.
"""
import asyncio
import logging
from typing import AsyncGenerator, Dict, Optional
from uuid import uuid4

import httpx
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    SendMessageRequest, MessageSendParams, GetTaskRequest, TaskQueryParams,
    TaskState, TextPart, Message, Part 
)
from shared_src.config import settings
from .schemas import ChatMessageOutput

logger = logging.getLogger(__name__)

class A2AService:
    """A service for managing communication with A2A agents."""
    
    _http_client: httpx.AsyncClient
    _agent_clients: Dict[str, A2AClient] = {}

    def __init__(self, http_client: httpx.AsyncClient):
        self._http_client = http_client

    async def get_agent_client(self, agent_id: str) -> A2AClient:
        """Lazily initializes and caches A2AClient instances."""
        if agent_id in self._agent_clients:
            return self._agent_clients[agent_id]

        agent_url_map = {
            "ai_excel_interviewer": f"http://127.0.0.1:{settings.AI_EXCEL_INTERVIEWER_A2A_INTERNAL_PORT}"
        }

        agent_url = agent_url_map.get(agent_id)
        if not agent_url:
            raise ValueError(f"Unknown agent_id: {agent_id}")

        logger.info(f"Initializing A2A client for '{agent_id}' at {agent_url}")
        
        resolver = A2ACardResolver(httpx_client=self._http_client, base_url=agent_url)
        agent_card = await resolver.get_agent_card()
        client = A2AClient(httpx_client=self._http_client, agent_card=agent_card)

        self._agent_clients[agent_id] = client
        return client

    async def stream_message_to_agent(
        self,
        agent_id: str,
        message_content: str,
        context_id: Optional[str] = None
    ) -> AsyncGenerator[ChatMessageOutput, None]:
        """Sends a message to an agent and streams back the 'thoughts' and final response."""
        
        if not context_id:
            context_id = uuid4().hex
            logger.info(f"BFF: Starting new conversation with context_id: {context_id}")

        try:
            agent_client = await self.get_agent_client(agent_id)
            message_to_send = Message(
                role="user",
                parts=[Part(root=TextPart(text=message_content))],
                messageId=uuid4().hex,
                contextId=context_id, 
                metadata={"user_id": "bff-web"} 
            )
            params = MessageSendParams(message=message_to_send)
            send_response = await agent_client.send_message(SendMessageRequest(id=uuid4().hex, params=params))
            task_id = send_response.root.result.id

            last_thought = ""
            for _ in range(180): 
                await asyncio.sleep(1)
                task_response = await agent_client.get_task(GetTaskRequest(id=uuid4().hex, params=TaskQueryParams(id=task_id)))
                task = task_response.root.result

                if task.status.state in {TaskState.completed, TaskState.failed, TaskState.canceled}:
                    final_content = "The interview has concluded."
                    if task.status.message and task.status.message.parts:
                        final_content = task.status.message.parts[0].root.text
                    yield ChatMessageOutput(type="final", content=final_content, context_id=context_id)
                    return

                if task.status.state == TaskState.working and task.status.message:
                    thought = task.status.message.parts[0].root.text
                    if thought != last_thought:
                        yield ChatMessageOutput(type="thought", content=thought, context_id=context_id)
                        last_thought = thought

            yield ChatMessageOutput(type="error", content="The agent timed out.", context_id=context_id)

        except Exception as e:
            logger.exception(f"BFF: Error communicating with agent '{agent_id}': {e}")
            yield ChatMessageOutput(type="error", content=f"An error occurred communicating with the agent.", context_id=context_id)