"""
ai_excel_interviewer/src/ai_excel_interviewer/agent.py

Defines the core ADK LlmAgent ("the brain") for the AI Excel Interviewer.
"""
import logging
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from ai_excel_interviewer.src.utils.prompts_loader import load_prompt
from shared_src.config import settings 

logger = logging.getLogger(__name__)

def _build_agent() -> LlmAgent:
    """Constructs and configures the AI Excel Interviewer LlmAgent."""
    mcp_url = f"http://127.0.0.1:{settings.AI_EXCEL_INTERVIEWER_MCP_INTERNAL_PORT}/mcp"

    toolset = MCPToolset(
        connection_params=SseConnectionParams(url=mcp_url),
        tool_filter=[
            "start_interview",
            "get_next_question",
            "evaluate_answer",
            "get_final_summary",
        ],
    )

    agent_instruction = load_prompt("agent_prompt.yaml")

    return LlmAgent(
        name="ExcelInterviewerOrchestrator",
        model="gemini-2.5-flash",
        instruction=agent_instruction,
        tools=[toolset],
    )

excel_interviewer_agent: LlmAgent = _build_agent()