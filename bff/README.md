# BFF (Backend-for-Frontend) Service

A lightweight Backend-for-Frontend (BFF) service that provides a secure, stateful API layer between a frontend client and backend AI agents. It manages chat sessions, user requests, and streams agent responses in real-time.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Concepts](#key-concepts)
3. [Features](#features)
4. [Architecture & Data Flow](#architecture--data-flow)
5. [Getting Started](#getting-started)

   * [Prerequisites](#prerequisites)
   * [Configuration](#configuration)
6. [Running Locally](#running-locally)
7. [API Reference](#api-reference)
8. [Project Structure](#project-structure)

---

## Project Overview

The **Chat BFF** simplifies frontend development by exposing a clean REST API for chat interactions.
It acts as a **gateway** between the UI and backend agents, handling session IDs, message streaming, and authentication (if enabled).

---

## Key Concepts

* **Backend-for-Frontend (BFF):** Tailored backend optimized for a single frontend app.
* **Chat Sessions:** Each conversation has a unique `context_id` that maintains continuity across multiple messages.
* **Streaming (SSE):** Uses Server-Sent Events to stream real-time agent responses (e.g., “thoughts” and “final answers”).

---

## Features

* **Session Management:** Maintain conversational context across multiple turns.
* **Real-time Streaming:** Forward agent responses to the frontend as they arrive.
* **Extensible Service Layer:** Plug in any backend agent client (e.g., local mock, A2A, OpenAI, LangChain).
* **CORS Enabled:** Configurable allowed origins for frontend access.

## Architecture & Data Flow

1. **Frontend → BFF:** The frontend sends a chat message to the BFF.
2. **BFF → Agent:** The BFF forwards the request to the backend agent service.
3. **Agent → BFF:** The agent streams responses back.
4. **BFF → Frontend:** The BFF streams these events directly to the client in real-time.

## Getting Started

### Prerequisites

* Python 3.11+
* `pip`
* PostgreSQL 

### Installation

```bash
pip install -e ./bff
```

### Configuration

Create a `.env` file at the project root:

```bash
# --- BFF Server Configuration ---
BFF_PORT_EXPOSED=8000
BFF_PORT_INTERNAL=8000
ALLOWED_ORIGINS='["http://localhost:5173", "*"]'
```

## Running Locally

```bash
python -m bff.src.main
```

Swagger docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Reference

### Chat Endpoints

| Method | Path                     | Description                                            |
| ------ | ------------------------ | ------------------------------------------------------ |
| `POST` | `/api/v1/chats/messages` | Sends a new message and streams agent responses (SSE). |

### Health Check

| Method | Path      | Description                   |
| ------ | --------- | ----------------------------- |
| `GET`  | `/health` | Returns `{ "status": "ok" }`. |

---

## Project Structure

```text
bff
├── pyproject.toml
├── README.md
└── src/
    ├── __init__.py
    ├── chat.py        # API routes
    ├── main.py        # FastAPI app entrypoint
    ├── schemas.py     # Pydantic models
    └── service.py     # Service layer for agent communication
```