# AI Excel Interviewer Agent

An advanced, adaptive AI agent that automates the technical screening process for Microsoft Excel skills. It conducts a dynamic, conversational mock interview, adjusting question difficulty based on candidate performance to provide a consistent, unbiased, and deeply insightful assessment.

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Key Concepts](#key-concepts)
3.  [Features](#features)
4.  [Architecture & Data Flow](#architecture--data-flow)
5.  [Agent In-Depth](#agent-in-depth)
    -   [Orchestration Workflow](#orchestration-workflow)
6.  [Getting Started](#getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Configuration](#configuration)
7.  [How to Run & Test](#how-to-run--test)
8.  [Example Interview Flow](#example-interview-flow)
9.  [Project Structure](#project-structure)

## Project Overview

The **AI Excel Interviewer** is designed to solve a critical bottleneck in the hiring pipeline for finance, operations, and data analytics roles: the time-consuming and inconsistent manual screening of Excel skills. This agent replaces that process with a standardized, on-demand, and intelligent conversational assessment.

The agent guides a candidate through a series of practical, scenario-based questions, evaluates their free-text answers, and provides a comprehensive performance summary at the end.

This automates a key part of the recruiting funnel, freeing up senior analysts' time, eliminating scheduling conflicts, and ensuring every candidate receives a fair and consistent evaluation.

## Key Concepts

-   **Adaptive Testing**: This is the agent's core intelligence. It does not follow a static script. Based on the candidate's answer, it dynamically adjusts the difficulty and topic of the next question, creating a tailored interview experience that can effectively gauge both beginner and expert-level skills.
-   **Stateful Interview Sessions**: Each interview is a persistent, stateful session managed in a PostgreSQL database. The agent tracks the current question number, topics covered, and the candidate's score throughout the conversation.
-   **LLM as a Subject Matter Expert**: The agent's backend leverages a powerful generative model (Gemini 1.5 Pro) for its core logic. The LLM is used not just to chat, but to:
    1.  Generate unique, context-aware interview questions on the fly.
    2.  Evaluate the nuance of a candidate's free-text answer against an internal rubric.
    3.  Synthesize the full interview transcript into a final, actionable feedback report.
-   **Three-Tier Architecture**: The agent is built on a robust 3-tier model (A2A -> MCP -> Backend) for a clean separation of concerns, scalability, and maintainability.

## Features

-   **Dynamic Question Generation:** Creates unique, scenario-based Excel questions in real-time, avoiding repetitive scripts.
-   **Adaptive Difficulty Engine:** Automatically increases or decreases question difficulty based on the correctness of the candidate's previous answer.
-   **Intelligent Answer Evaluation:** Uses an LLM to understand and grade free-text responses, recognizing partially correct answers and providing nuanced feedback.
-   **Persistent Interview Transcripts:** Saves the complete history of every interview session to a database for review and auditing.
-   **Automated Performance Summary:** At the end of the interview, it generates a final report detailing the candidate's score, identified strengths, and specific areas for improvement.
-   **Conversational and Engaging:** Interacts with the candidate in a professional, encouraging, and natural manner.

## Architecture & Data Flow

1.  **Request:** A user starts an interview via a client (e.g., the A2A test client or a web UI). The request hits the **A2A Server**.
2.  **Orchestration:** The agent's brain (ADK LlmAgent) consults its master prompt and knows it needs to start an interview. It calls the `start_interview` tool on its **MCP Server**.
3.  **Backend Logic:** The MCP Server forwards the request to the **Backend API**. The backend creates a new `InterviewSession` record in the **PostgreSQL Database** and returns the `session_id`.
4.  **Interview Loop:** The agent's brain then enters a loop:
    a. It calls `get_next_question` (MCP -> Backend -> LLM -> DB).
    b. It presents the question to the user.
    c. It receives the user's answer.
    d. It calls `evaluate_answer` (MCP -> Backend -> LLM -> DB), which grades the answer and updates the session state with the next topic/difficulty.
    e. It provides feedback to the user.
5.  **Final Report:** When the interview concludes, the agent calls `get_final_summary`. The backend retrieves the full session from the database, uses an LLM to write the summary, and returns the final report.
6.  **Response:** The A2A agent formats and delivers the final report to the user.

## Getting Started

### Prerequisites

-   Python 3.11+
-   Docker & Docker Compose (for PostgreSQL) or a local PostgreSQL instance.
-   A Google Gemini API Key.

### Configuration

Create a `.env` file in the project root (`ai_excel_interviewer/`) with the following content:

```dotenv
# .env
# --- AI Excel Interviewer Service ---
AI_EXCEL_INTERVIEWER_SERVICE_NAME = "ai_excel_interviewer"
AI_EXCEL_INTERVIEWER_INTERNAL_PORT = 8100
AI_EXCEL_INTERVIEWER_MCP_SERVICE_NAME = "ai_excel_interviewer_mcp"
AI_EXCEL_INTERVIEWER_MCP_INTERNAL_PORT = 9100
AI_EXCEL_INTERVIEWER_A2A_SERVICE_NAME = "ai_excel_interviewer_a2a"
AI_EXCEL_INTERVIEWER_A2A_INTERNAL_PORT = 10100
```

## How to Run & Test

This is a self-contained, 3-tier agent. You must run all three services to test it.

### Step 1: Set Up the Database

First, ensure your PostgreSQL is setup. 

### Step 2: Start the Agent's Services

Open three separate terminals. In each one, navigate to the project root and activate your virtual environment.

*   **Terminal 1: Start the Backend API**
    ```bash
    python -m ai_excel_interviewer.src.backend_api.server
    ```

*   **Terminal 2: Start the MCP Server**
    ```bash
    python -m ai_excel_interviewer.src.mcp_server.server
    ```

*   **Terminal 3: Start the A2A Agent Server**
    ```bash
    python -m ai_excel_interviewer.src.excel_interviewer_agent
    ```

### Step 3: Run the Test Client

In a fourth terminal, run the interactive A2A client.

```bash
# (Activate venv)
python -m ai_excel_interviewer.src.client.a2a_client
```

## Example Interview Flow

**You (Candidate):** `start interview`

**Interviewer:** "Hello, I'm your AI interviewer for Excel. We'll go through a series of questions to assess your skills. The difficulty will adapt based on your answers. Let's begin."
...
"Question 1: Imagine you have a small sales report. Column A has product names, and Column B has the quantity sold for each. In cell C1, how would you write a formula to find the total number of items sold across all products?"

**You (Candidate):** `=SUM(B:B)`

**Interviewer:** "That's correct! Using the SUM function is the most efficient way to total a range. Let's move to the next question."
...
"Question 2: You manage employee records where Column A has Employee IDs and Column M has salaries. On another sheet, you have a list of Employee IDs — how would you efficiently fetch the correct salary for each?"

... *(The interview continues adaptively)* ...

**You (Candidate):** `end interview`

**Interviewer:** *(Generates and displays the final summary report, including score, strengths, areas for improvement, and the full transcript.)*

## Project Structure

```text
ai_excel_interviewer/
    ├── .env
    ├── pyproject.toml
    └── src/
        ├── backend_api/
        │   └── server.py
        ├── mcp_server/
        │   └── server.py
        ├── excel_interviewer_agent/
        │   ├── __main__.py
        │   ├── agent.py
        │   └── agent_executor.py
        ├── prompts/
        │   └── agent_prompt.yaml
        └── client/
            └── a2A_client.py
```
