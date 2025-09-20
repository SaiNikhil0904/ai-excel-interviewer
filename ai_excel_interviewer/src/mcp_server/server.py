"""
ai_excel_interviewer/src/mcp_server/server.py

MCP Server for the AI Excel Interviewer Agent.

- Acts as a thin facade that exposes the backend’s capabilities
  as a clean set of MCP tools callable by an A2A agent.
- Delegates all core logic to the backend API service.
- Uses centralized configuration from shared_src/config.py.
"""

import logging, os
from typing import Dict, Any
from uuid import UUID

import httpx
from fastapi.responses import JSONResponse
from fastmcp import FastMCP
from pydantic import Field
from shared_src.config import settings  

logger = logging.getLogger(__name__)
mcp = FastMCP("excel_interviewer_tools")

async def _call_backend(method: str, endpoint: str, payload: Dict = None) -> Dict[str, Any]:
    backend_url = f"http://127.0.0.1:{settings.AI_EXCEL_INTERVIEWER_INTERNAL_PORT}"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            if method.upper() == "POST":
                response = await client.post(f"{backend_url}{endpoint}", json=payload)
            elif method.upper() == "GET":
                response = await client.get(f"{backend_url}{endpoint}")
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        error_detail = e.response.json().get("detail", e.response.text)
        logger.error(f"Backend API error: {e.response.status_code} - {error_detail}")
        raise RuntimeError(f"The interview service returned an error: {error_detail}")
    except httpx.RequestError as e:
        logger.error(f"MCP->Backend connection error: {e}")
        raise RuntimeError("Could not connect to the interview service backend.")

# --- MCP Tool Definitions ---
@mcp.tool()
async def start_interview(
    user_id: str = Field(..., description="A unique identifier for the candidate.")
) -> Dict[str, Any]:
    """Initializes a new interview session for a user and returns the session ID."""
    return await _call_backend("POST", "/interviews", payload={"user_id": user_id})

@mcp.tool()
async def get_next_question(
    session_id: UUID = Field(..., description="The unique ID for the current interview session.")
) -> Dict[str, Any]:
    """Fetches the next adaptive question for the given interview session."""
    return await _call_backend("POST", f"/questions/generate?session_id={session_id}")

@mcp.tool()
async def evaluate_answer(
    session_id: UUID = Field(..., description="The ID of the current interview session."),
    user_answer: str = Field(..., description="The candidate's full answer to the question.")
) -> Dict[str, Any]:
    """Submits a candidate's answer to the backend for evaluation and feedback."""
    payload = {"session_id": str(session_id), "answer": user_answer}
    return await _call_backend("POST", "/answers/evaluate", payload=payload)

@mcp.tool()
async def get_final_summary(
    session_id: UUID = Field(..., description="The ID of the completed interview session.")
) -> Dict[str, Any]:
    """Gets the final, aggregated performance summary for a completed interview."""
    return await _call_backend("GET", f"/interviews/{session_id}/summary")

@mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def health_check(request):
    """Simple health check endpoint."""
    return JSONResponse({"status": "ok"})

def main():
    """Entrypoint to run the MCP Server."""
    mcp.run(transport="sse", host="127.0.0.1", port=settings.AI_EXCEL_INTERVIEWER_MCP_INTERNAL_PORT,path="/mcp",
    )

if __name__ == "__main__":
    main()