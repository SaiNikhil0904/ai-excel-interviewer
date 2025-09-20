# Frontend

## Overview

This frontend project provides a user interface for interacting with the **Backend-for-Frontend (BFF)**.
Users can send messages, receive streaming responses, and maintain multi-turn conversation sessions.

## Features

* **Send messages** to agents via the BFF API.
* **Receive streaming responses** (SSE: Server-Sent Events) for real-time updates.
* **Multi-turn conversations** using `context_id` to maintain session state.
* Simple **health check** integration with the BFF.

## Prerequisites

* Node.js >= 18.x
* npm or yarn
* BFF server running locally (default: `http://localhost:8000`)

## Installation

```bash
cd frontend

# Install dependencies
npm install

npm install marked
```

## Running the Frontend

```bash
# Start development server
npm run dev
```

By default, it runs on `http://localhost:5173`.

## Configuration

The frontend expects the **BFF API** endpoint as an environment variable:

```env
BFF_URL = 'http://localhost:8000/api/v1'; 
```

## Usage

### Sending a Message

* Users type a message in the input box.
* Frontend POSTs to:

```
POST /api/v1/chats/messages
Body: { "content": "<your message>" }
Optional Query: context_id=<existing-session-id>
```

### Receiving Streaming Responses

* The frontend listens to **Server-Sent Events (SSE)**:

```js
const evtSource = new EventSource(`${BFF_URL}/chats/messages?context_id=${sessionId}`);
evtSource.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(message.type, message.content);
};
```

## Project Structure

```
frontend/
├── public/          # Static assets
├── src/
│   ├── components/  # React/Vue components
│   ├── services/    # API calls to BFF
│   ├── App.js       # Main app entry
│   └── main.js      # JS entrypoint
├── package.json
└── .env
```

## Notes

* Designed to work with **any BFF** following the streaming message API.
* Supports multiple agents and multiple conversation sessions.
* Ensure the BFF is running before starting the frontend.
