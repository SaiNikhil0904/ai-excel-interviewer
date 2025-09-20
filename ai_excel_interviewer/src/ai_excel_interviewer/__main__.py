"""
ai_excel_interviewer/src/ai_excel_interviewer/__main__.py

Main entrypoint for the AI Excel Interviewer A2A Server.

This server exposes the Excel Interviewer Agent over the A2A protocol,
allowing orchestrators or clients to interact with it in a structured,
stateful way.
"""
import logging
from typing import List
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities, AgentProvider
from fastapi.responses import JSONResponse

from .agent_executor import ExcelInterviewerAgentExecutor
from shared_src.config import settings  
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

logger = logging.getLogger(__name__)

app = FastAPI()

def create_agent_card() -> AgentCard:
    """Create the A2A AgentCard for the Excel Interviewer Agent."""
    skill = AgentSkill(
        id="conduct_excel_interview",
        name="Adaptive Excel Skills Interview",
        description=(
            "Conducts a dynamic, conversational mock interview to assess a "
            "candidate's Excel proficiency, adjusting difficulty based on performance."
        ),
        tags=["excel", "interview", "assessment", "hr", "recruiting"],
        examples=[
            "Start my Excel interview",
            "I'm ready to begin the assessment."
        ],
    )
    return AgentCard(
        name="AI Excel Interviewer",
        description="An adaptive agent that conducts technical interviews for Excel skills.",
        url=f"http://127.0.0.1:{settings.AI_EXCEL_INTERVIEWER_A2A_INTERNAL_PORT}",
        version="1.0.0",
        provider=AgentProvider(
            organization="Coding Ninjas",
            url="https://your-website.com",
        ),
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/markdown"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )


async def health_check(request):
    """Simple health check endpoint."""
    return JSONResponse({"status": "ok"})


def main() -> None:
    """Entrypoint for running the A2A server."""
    server_app = A2AStarletteApplication(
        agent_card=create_agent_card(),
        http_handler=DefaultRequestHandler(
            agent_executor=ExcelInterviewerAgentExecutor(),
            task_store=InMemoryTaskStore(),
        ),
    )
    # app = FastAPI(title="AI Excel Interviewer A2A Server")
    app = server_app.build()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"], 
        allow_headers=["*"], 
    )
    app.add_route("/health", health_check, methods=["GET"])

    host = "127.0.0.1"
    port = settings.AI_EXCEL_INTERVIEWER_A2A_INTERNAL_PORT

    logger.info(f"Starting AI Excel Interviewer A2A server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()