"""
ai_excel_interviewer/src/client/mcp_client.py

A standalone, interactive CLI for directly testing the AI Excel Interviewer's MCP Tool Server.
"""
import asyncio
import json
import logging
import sys
from contextlib import AsyncExitStack
from pathlib import Path

import click
from mcp import ClientSession
from mcp.client.sse import sse_client

try:
    PROJECT_ROOT = Path(__file__).resolve().parents[4]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
except IndexError:
    print("ERROR: Could not determine the project root. Make sure the script is in the correct directory structure.")
    sys.exit(1)

from shared_src.config import settings

logging.basicConfig(level="INFO", format="%(asctime)s - [INTERVIEW-MCP-CLIENT] - [%(levelname)s] - %(message)s")

def pretty_print_result(result: any):
    """Handles pretty-printing of JSON results."""
    try:
        data = json.loads(result)
        click.echo(json.dumps(data, indent=2))
    except (json.JSONDecodeError, TypeError):
        click.echo(result)

def get_required_input(prompt_text: str) -> str:
    """Helper to get non-empty input from the user."""
    while True:
        value = click.prompt(prompt_text, type=str).strip()
        if value:
            return value
        click.secho("This field cannot be empty.", fg="red")

async def run_mcp_client(server_url: str):
    """Main async function to run the interactive MCP client."""
    click.secho(f"Attempting to connect to Excel Interviewer MCP server at {server_url}...", fg="yellow")

    async with AsyncExitStack() as stack:
        try:
            sse_transport = await stack.enter_async_context(sse_client(server_url))
            session = await stack.enter_async_context(ClientSession(*sse_transport))
            await session.initialize()
            response = await session.list_tools()
            tool_names = [tool.name for tool in response.tools]
            click.secho(f"Successfully connected. Available tools: {tool_names}", fg="green")
        except Exception as e:
            click.secho(f"Failed to connect to MCP server: {e}", fg="red")
            return

        current_session_id = None

        while True:
            click.echo("\n" + "=" * 50)
            click.secho(f"Current Session ID: {current_session_id}", bold=True)
            tool = click.prompt(click.style("Enter tool to call (or 'quit')", fg="cyan"))
            if tool.lower() in ["q", "quit", "exit"]:
                break
            if tool not in tool_names:
                click.secho(f"Error: Tool '{tool}' not found.", fg="red")
                continue

            args = {}
            if tool == "start_interview":
                args["user_id"] = get_required_input("  Enter a user_id for this interview")
            elif tool in ["get_next_question", "evaluate_answer", "get_final_summary"]:
                if not current_session_id:
                    click.secho("Error: You must call 'start_interview' first to get a session_id.", fg="red")
                    continue
                args["session_id"] = current_session_id
                if tool == "evaluate_answer":
                    args["user_answer"] = get_required_input("  Enter the candidate's answer")

            try:
                click.echo(f"Calling tool '{tool}'...")
                result = await session.call_tool(tool, args)
                result_text = result.content[0].text if result.content else "{}"

                click.secho("--- Tool Result ---", fg="green", bold=True)
                pretty_print_result(result_text)

                if tool == "start_interview":
                    try:
                        result_data = json.loads(result_text)
                        current_session_id = result_data.get("session_id")
                        if current_session_id:
                            click.secho(f"Session started. ID '{current_session_id}' is now cached.", fg="yellow")
                    except json.JSONDecodeError:
                        click.secho("Error: Could not parse session_id from 'start_interview' response.", fg="red")

            except Exception as e:
                click.secho(f"--- Error during tool call ---\n{e}", fg="red")

@click.command()
@click.option(
    "--server-url",
    default=f"http://localhost:{settings.AI_EXCEL_INTERVIEWER_MCP_INTERNAL_PORT}/mcp",
    show_default=True,
    help="The full MCP server URL for the Excel Interviewer."
)
def main(server_url: str):
    """A standalone CLI to test the AI Excel Interviewer's MCP Server."""
    try:
        asyncio.run(run_mcp_client(server_url))
    except KeyboardInterrupt:
        click.echo("\nClient exited.")

if __name__ == "__main__":
    main()