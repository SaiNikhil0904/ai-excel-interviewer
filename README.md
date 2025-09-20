# AI-Powered Excel Mock Interviewer

## Project Overview
The **AI-Powered Excel Mock Interviewer** is an intelligent system designed to automate the evaluation of candidates' Excel skills. It simulates real interviews, evaluates answers, and generates constructive feedback reports.

This README will guide you through **setting up the environment, database, and AI agent** step by step.

---

## 1. Setup `ai_excel_interviewer`

1. Clone the repository:
```bash
[git clone https://github.com/your-username/ai-excel-interviewer.git](https://github.com/SaiNikhil0904/ai-excel-interviewer.git)
````

2. Create a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:

```bash
pip install -r ai_excel_interviewer/requirements.txt
```

---

## 2. Configure Environment Variables

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Open `.env` and **replace placeholder values**:

* Set your `GOOGLE_API_KEY`
* Configure any other environment-specific settings

---

## 3. Setup the Database (PostgreSQL)

1. Navigate to the **shared\_src README** for detailed database setup:

   ```
   shared_src/README.md
   ```
Follow the steps to setup the Postgresql in local
---

## 4. Agent Setup

1. Navigate to the AI agent setup documentation:

   ```
   ai_excel_interviewer/README.md
   ```

2. Typical steps include:

   * Installing required AI packages
   * Setting up A2A client or chosen LLM
   * Configuring agent-specific environment variables
   * Running any initialization scripts
---

## Notes

* Make sure `.env` is **not committed** to the repository.
* Follow the step-by-step instructions in `shared_src/README.md` and `ai_excel_interviewer/README.md` for full setup.
