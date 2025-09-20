# AI-Powered Excel Mock Interviewer

## Project Overview

The **AI-Powered Excel Mock Interviewer** is an intelligent system designed to simulate professional Excel interviews. It evaluates candidate answers, adapts question difficulty, and generates detailed feedback reports.

This README guides you through **setting up the environment, database, backend, AI agent, and frontend** step by step.

---

## 1. Setup `ai_excel_interviewer`

1. **Clone the repository**:

```bash
git clone https://github.com/SaiNikhil0904/ai-excel-interviewer.git
```

2. **Create and Activate Python Virtual Environment**:

```bash
# Create the virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate
```

3. **Install Python dependencies**:

```bash
pip install -r ai_excel_interviewer/requirements.txt
```

---

## 2. Configure Environment Variables

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Open `.env` and **replace placeholder values**, including:

```env
GOOGLE_API_KEY="your_google_api_key_here"
```

3. Double-check the `.env` file before running any application code.

---

## 3. Setup the Database (PostgreSQL)

**Option 1: Detailed Guide**
Go to: [shared\_src DB README](https://github.com/SaiNikhil0904/ai-excel-interviewer/blob/main/shared_src/db/README.md)

**Option 2: Quick Setup**

1. Ensure PostgreSQL and pgAdmin 4 are installed.

2. `.env` configuration:

```env
DB_USER="excel_user"
DB_PASSWORD="a-very-secure-password"
DB_NAME="excel_interviewer_db"
DB_HOST="localhost"
DB_PORT="5432"
```

3. **Setup using pgAdmin (GUI)**:

* **Connect to your Server**: Open pgAdmin and connect using `postgres` superuser credentials.
* **Create the Database**:

  * Right-click `Databases` → `Create → Database…`
  * Enter `excel_interviewer_db` and save.
* **Create Login/Group Role**:

  * Right-click `Login/Group Roles` → `Create → Login/Group Role…`
  * Name: `excel_user`
  * Password: `a-very-secure-password`
  * Set "Can login?" to Yes → Save.

---

## 4. Backend-for-Frontend (BFF) Setup

1. Refer to [BFF README](https://github.com/SaiNikhil0904/ai-excel-interviewer/blob/main/bff/README.md).

2. **Configuration**: Create `.env` at project root:

```env
BFF_PORT_EXPOSED=8000
BFF_PORT_INTERNAL=8000
ALLOWED_ORIGINS='["http://localhost:5173", "*"]'
```

3. **Install BFF**:

```bash
pip install -e ./bff
```

4. **Run Locally**:

```bash
python -m bff.src.main
```

---

## 5. AI Excel Interviewer Agent Setup

1. Refer to [AI Excel Interviewer README](https://github.com/SaiNikhil0904/ai-excel-interviewer/blob/main/ai_excel_interviewer/README.md).

2. **Configuration**: Create `.env` in project root:

```env
AI_EXCEL_INTERVIEWER_SERVICE_NAME="ai_excel_interviewer"
AI_EXCEL_INTERVIEWER_INTERNAL_PORT=8100
AI_EXCEL_INTERVIEWER_MCP_SERVICE_NAME="ai_excel_interviewer_mcp"
AI_EXCEL_INTERVIEWER_MCP_INTERNAL_PORT=9100
AI_EXCEL_INTERVIEWER_A2A_SERVICE_NAME="ai_excel_interviewer_a2a"
AI_EXCEL_INTERVIEWER_A2A_INTERNAL_PORT=10100
```

3. **Install & Run Services**:

```bash
# Install package
pip install -e ./ai_excel_interviewer
# or
pip install -r ai_excel_interviewer/requirements.txt
```

4. **Start the Agent Services** (open 3 terminals):

* **Terminal 1**: Backend API

```bash
python -m ai_excel_interviewer.src.backend_api.server
```

* **Terminal 2**: MCP Server

```bash
python -m ai_excel_interviewer.src.mcp_server.server
```

* **Terminal 3**: A2A Agent Server

```bash
python -m ai_excel_interviewer.src.excel_interviewer_agent
```

* **Optional**: Run the interactive A2A client

```bash
python -m ai_excel_interviewer.src.client.a2a_client
```

---

## 6. Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
npm install marked
```

3. Run the development server:

```bash
npm run dev
```

By default, the frontend runs at [http://localhost:5173](http://localhost:5173).

---

## Notes

* Keep your `.env` files **private**; do not commit them.
* Follow the detailed instructions in the referenced READMEs for each component (Database, BFF, Agent, Frontend).
* Services must be run in the correct order to function: **Database → Backend → MCP → A2A → Frontend**.
