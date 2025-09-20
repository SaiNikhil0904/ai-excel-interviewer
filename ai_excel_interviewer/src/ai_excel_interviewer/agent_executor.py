"""
ai_excel_interviewer/src/ai_excel_interviewer/agent_executor.py

Bridges A2A protocol requests to the ADK-based ExcelInterviewerAgent.
"""
import logging
from uuid import uuid4
from typing import Optional
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Task, TaskState, UnsupportedOperationError
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError
from google.adk.events import Event as ADKEvent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.genai import types as genai_types

from .agent import excel_interviewer_agent
from shared_src.config import settings

logger = logging.getLogger(__name__)

class ExcelInterviewerAgentExecutor(AgentExecutor):
    """A2A Executor for the Excel Interviewer Agent, handling streaming."""

    def __init__(self) -> None:
        super().__init__()
        db_url_sync = (
            f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
        self.adk_agent_instance = excel_interviewer_agent
        # self.session_service = InMemorySessionService()
        self.session_service = DatabaseSessionService(db_url=db_url_sync)
        self._runner = Runner(
            agent=self.adk_agent_instance,
            app_name=self.adk_agent_instance.name,
            session_service=self.session_service,
            memory_service=InMemoryMemoryService(),
            artifact_service=InMemoryArtifactService(),
        )
        logger.info("ExcelInterviewerAgentExecutor initialized with persistent ADK Runner.")

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.get_user_input() or "User provided empty input."
        a2a_task = context.current_task
        user_meta = context.message.metadata or {}
        user_id = str(user_meta.get("user_id", f"user_{uuid4().hex[:6]}"))

        adk_session_id = context.message.contextId or uuid4().hex
        context.message.contextId = adk_session_id

        if not a2a_task:
            a2a_task = new_task(context.message)
            await event_queue.enqueue_event(a2a_task)

        updater = TaskUpdater(event_queue, a2a_task.id, adk_session_id)

        try:
            session = await self._runner.session_service.get_session(
                app_name=self.adk_agent_instance.name,
                user_id=user_id,
                session_id=adk_session_id
            )
            if not session:
                await self._runner.session_service.create_session(
                    app_name=self.adk_agent_instance.name,
                    user_id=user_id,
                    session_id=adk_session_id,
                    state={}
                )

            genai_user_message = genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=query)]
            )
            final_adk_event: Optional[ADKEvent] = None

            async for adk_event in self._runner.run_async(
                user_id=user_id,
                session_id=adk_session_id,
                new_message=genai_user_message
            ):
                if adk_event.is_final_response():
                    final_adk_event = adk_event
                    continue

                if adk_event.content and adk_event.content.parts:
                    part = adk_event.content.parts[0]
                    thought = ""
                    if part.function_call:
                        thought = f"Calling tool: `{part.function_call.name}`..."
                    elif part.function_response:
                        thought = f"Tool `{part.function_response.name}` completed."

                    if thought:
                        await updater.update_status(
                            TaskState.working,
                            new_agent_text_message(thought, adk_session_id, a2a_task.id)
                        )

            if not final_adk_event or not final_adk_event.content:
                raise RuntimeError("Agent workflow completed without a final response.")

            final_text = final_adk_event.content.parts[0].text
            await updater.update_status(
                TaskState.completed,
                new_agent_text_message(final_text, adk_session_id, a2a_task.id),
                final=True
            )

        except Exception as e:
            logger.exception(f"Excel Interviewer workflow failed: {e}")
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(f"I encountered an error: {str(e)}", adk_session_id, a2a_task.id),
                final=True
            )

    async def cancel(self, request: RequestContext, event_queue: EventQueue) -> Optional[Task]:
        """Handles A2A task cancellation requests."""
        task_to_cancel = request.current_task
        if not task_to_cancel:
            raise ServerError(UnsupportedOperationError("No active task to cancel."))

        logger.info(f"Cancelling A2A Task {task_to_cancel.id} for Excel Interviewer.")
        updater = TaskUpdater(event_queue, task_to_cancel.id, task_to_cancel.context_id)
        await updater.update_status(
            TaskState.canceled,
            new_agent_text_message("The Excel Interviewer task has been canceled.", task_to_cancel.context_id, task_to_cancel.id),
            final=True
        )

        return task_to_cancel
