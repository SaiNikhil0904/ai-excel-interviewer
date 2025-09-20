"""
ai_excel_interviewer/src/client/a2a_client.py

Standalone A2A client for testing the AI Excel Interviewer.
Manages conversation state and displays streaming thoughts and final responses.
"""
import asyncio
import json
import os
import traceback
from uuid import uuid4
from typing import Any, Optional, Dict

import click
import httpx
import logging
from pathlib import Path
import sys

try:
    PROJECT_ROOT = Path(__file__).resolve().parents[4]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
except IndexError:
    print("ERROR: Could not determine the project root. Ensure the directory structure is correct.")
    sys.exit(1)

from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    SendMessageRequest, GetTaskRequest, TaskQueryParams,
    MessageSendParams, Message, Part, TextPart, Task, TaskState, JSONRPCErrorResponse, AgentCard
)
from shared_src.config import settings

# --- Configuration ---
SESSION_FILE = ".excel_interviewer_a2a_session.json"
logging.basicConfig(level="INFO", format="%(asctime)s - [EXCEL-A2A-CLIENT] - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

# --- Session Management ---
def load_session_id() -> Optional[str]:
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                return json.load(f).get("context_id")
        except Exception:
            return None
    return None

def save_session_id(context_id: str):
    with open(SESSION_FILE, "w") as f:
        json.dump({"context_id": context_id}, f)

def clear_session_id():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# --- A2A Interaction ---
def build_message_payload(text: str, user_id: str, context_id: Optional[str] = None) -> Dict[str, Any]:
    msg_dict = {
        "role": "user",
        "parts": [Part(root=TextPart(text=text))],
        "messageId": uuid4().hex,
        "metadata": {"user_id": user_id},
    }
    if context_id:
        msg_dict["context_id"] = context_id  # updated from contextId
    return {"message": Message.model_validate(msg_dict)}

async def poll_for_final_task(client: A2AClient, task_id: str) -> Optional[Task]:
    click.echo("Agent is processing...")
    last_thought = ""
    terminal_states = {TaskState.completed, TaskState.failed, TaskState.canceled, TaskState.rejected}

    for _ in range(180):
        await asyncio.sleep(1)
        try:
            req = GetTaskRequest(id=uuid4().hex, params=TaskQueryParams(id=task_id))
            resp = (await client.get_task(req)).root
            if isinstance(resp, JSONRPCErrorResponse):
                click.secho(f"Error polling task: {resp.error.message}", fg="red")
                return None

            task = resp.result
            if task.status.state == TaskState.working and task.status.message:
                thought = task.status.message.parts[0].root.text
                if thought != last_thought:
                    click.secho(f"  -> {thought}", dim=True)
                    last_thought = thought
            elif task.status.state in terminal_states:
                click.secho(f"Task finished with state: {task.status.state.value}", fg="green")
                return task
        except Exception as e:
            logger.error(f"Polling error: {e}", exc_info=True)
            return None

    click.secho("Polling timed out.", fg="red")
    return None

# --- Main Application Loop ---
async def interactive_loop(client: A2AClient, user_id: str, agent_card: AgentCard) -> None:
    click.secho(f"\nConnected to '{agent_card.name}'.", bold=True)
    click.echo("Type your query, e.g., 'Calculate total cost for ingredient A.'")
    click.echo("Use '/reset' to start a new conversation, or '/quit' to exit.")

    current_context_id = load_session_id()
    if current_context_id:
        click.secho(f"Restored session: {current_context_id}", fg="yellow")

    while True:
        query = click.prompt(click.style("\nYou", fg="cyan"), type=str).strip()
        if not query:
            continue
        if query.lower() in {"/exit", "/quit"}:
            break
        if query == "/reset":
            clear_session_id()
            current_context_id = None
            continue

        try:
            payload = build_message_payload(query, user_id, current_context_id)
            params = MessageSendParams(message=payload["message"])
            send_req = SendMessageRequest(id=uuid4().hex, params=params)

            response = await client.send_message(send_req)
            if isinstance(response.root, JSONRPCErrorResponse):
                click.secho(f"Error sending message: {response.root.error.message}", fg="red")
                continue

            initial_task = response.root.result
            if not current_context_id:
                current_context_id = initial_task.context_id  # updated from contextId
                save_session_id(current_context_id)

            final_task = await poll_for_final_task(client, initial_task.id)

            click.secho("\n--- Agent's Final Response ---", bold=True, fg="yellow")
            if final_task and final_task.status.state == TaskState.completed:
                click.echo(final_task.status.message.parts[0].root.text)
            elif final_task:
                click.secho(
                    f"Task ended with status '{final_task.status.state.value}': {final_task.status.message.parts[0].root.text}",
                    fg="red"
                )
            else:
                click.secho("Failed to get a final response from the agent.", fg="red")

        except Exception as e:
            click.secho(f"An unexpected client-side error occurred: {e}", fg="red")
            traceback.print_exc()

# --- CLI Entrypoint ---
@click.command()
@click.option(
    "--agent-url",
    default=f"http://localhost:{settings.AI_EXCEL_INTERVIEWER_A2A_INTERNAL_PORT}",
    help="URL of the AI Excel Interviewer A2A agent."
)
def main(agent_url: str):
    """Standalone, stateful A2A client for AI Excel Interviewer."""
    async def run_client():
        user_id = f"cli-user-{uuid4().hex[:6]}"
        try:
            async with httpx.AsyncClient(timeout=300.0) as session:
                resolver = A2ACardResolver(httpx_client=session, base_url=agent_url)
                agent_card = await resolver.get_agent_card()
                client = A2AClient(httpx_client=session, agent_card=agent_card)
                await interactive_loop(client, user_id, agent_card)
        except httpx.ConnectError:
            click.secho(f"\nConnection failed to {agent_url}.", fg="red")
        except Exception as exc:
            click.secho(f"\nAn unhandled error occurred during setup: {exc}", fg="red")
            traceback.print_exc()

    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        click.echo("\nClient exited.")

if __name__ == "__main__":
    main()