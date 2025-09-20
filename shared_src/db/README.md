# Database Setup Guide for AI Excel Interviewer

This document provides a comprehensive guide to setting up the PostgreSQL database required for the AI Excel Interviewer agent. A correct database setup is critical for storing interview sessions, transcripts, and user data.

## Table of Contents

1.  [Overview](#overview)
2.  [Prerequisites](#prerequisites)
3.  [Step 1: PostgreSQL Instance Setup](#step-1-postgresql-instance-setup)
    -   [Using pgAdmin (GUI)](#using-pgadmin-gui)
    -   [Using psql (Command Line)](#using-psql-command-line)
4.  [Step 2: Schema & Table Creation](#step-2-schema--table-creation)
    -   [Method A: Automatic (for Local Development)](#method-a-automatic-for-local-development)
    -   [Method B: Migrations (for Production)](#method-b-migrations-for-production)
5.  [Configuration Check (`.env`)](#configuration-check-env)
6.  [Troubleshooting Common Errors](#troubleshooting-common-errors)

## Overview

The agent uses a PostgreSQL database to persistently store all interview-related data. The setup process involves two main stages:
1.  **Infrastructure Setup**: Creating the database itself and a dedicated user role with the correct permissions within your PostgreSQL instance.
2.  **Schema Creation**: Running a script to create the necessary tables (`interview_sessions`, `interview_turns`) inside the newly created database.

## Prerequisites

-   **PostgreSQL Installed**: You must have a running PostgreSQL instance (version 12 or newer). If you don't have it installed, you can download it from the [official website](https://www.postgresql.org/download/).
-   **Database Client**: You need a way to connect to PostgreSQL to run admin commands. We recommend one of the following:
    -   **pgAdmin**: A powerful graphical user interface for managing PostgreSQL (usually included with the installer).
    -   **psql**: The standard command-line interface for PostgreSQL.

## Step 1: PostgreSQL Instance Setup

Before running the application, you need to create the database and a user for the agent to connect with. The credentials you create here **must** match the ones in your `.env` file.

---

### Using pgAdmin (GUI)

This is the recommended method for those who prefer a visual interface.

1.  **Connect to your Server**: Open pgAdmin and connect to your local PostgreSQL instance. You will likely use the `postgres` superuser and the password you set during installation.

2.  **Create the Database**:
    -   In the left-hand browser panel, right-click on **Databases**.
    -   Select **Create** -> **Database...**.
    -   In the "Database" field, enter `excel_interviewer_db`.
    -   Click **Save**.

3.  **Create the Login/Group Role (User)**:
    -   In the browser panel, right-click on **Login/Group Roles**.
    -   Select **Create** -> **Login/Group Role...**.
    -   In the "General" tab, enter the name `excel_user`.
    -   Go to the "Definition" tab and enter the password. **It must be `a-very-secure-password`** to match the `.env` file.
    -   Go to the "Privileges" tab and set "Can login?" to **Yes**.
    -   Click **Save**.

4.  **Grant Privileges**:
    -   Find your new database (`excel_interviewer_db`) in the browser panel, right-click it, and select **Query Tool**.
    -   Paste and run the following SQL command to grant all necessary permissions to your new user:
        ```sql
        GRANT ALL PRIVILEGES ON DATABASE excel_interviewer_db TO excel_user;
        ```

## Configuration Check (`.env`)

Before running any application code, double-check that your `.env` file in the project root (`ai_excel_interviewer/.env`) has the correct values that you just set up.

```dotenv
# .env

DB_USER="excel_user"
DB_PASSWORD="a-very-secure-password"
DB_NAME="excel_interviewer_db"
DB_HOST="localhost"
DB_PORT="5432"
```