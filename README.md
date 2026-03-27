# Job Market Analytics Dashboard

A two-part project that scrapes remote job listings from the RemoteOK API, filters and loads them into a PostgreSQL database, and visualizes the data through an interactive Streamlit dashboard.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Pipeline: pipeline.py](#pipeline-pipelinepy)
- [Dashboard: appy](#dashboard-appy)
- [Security Notice](#security-notice)

---

## Overview

| Component | File | Description |
|---|---|---|
| **ETL Pipeline** | `pipeline.py` | Fetches jobs from RemoteOK API, filters by keywords, loads to PostgreSQL |
| **Dashboard** | `app.py` | Streamlit app for interactive filtering, KPIs, charts, and CSV export |

---

## Project Structure

```
├── pipeline.py        # ETL: extract → transform → load to DB
├── app.py             # Streamlit dashboard
├── dashboard.log      # Auto-generated runtime log
└── README.md
```

---

## Requirements

- Python 3.8+
- PostgreSQL (running locally or remotely)

Install dependencies:

```bash
pip install streamlit pandas psycopg2-binary requests
```

---

## Database Setup

Create the database and table in PostgreSQL before running anything:

```sql
CREATE DATABASE jobs_db;

\c jobs_db

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    tags TEXT,
    salary_min INTEGER,
    salary_max INTEGER
);
```

---

## Configuration

Both files currently hardcode database credentials. Before running, update the connection details in each file (or move them to environment variables — see [Security Notice](#security-notice)):

```python
DB_CONFIG = {
    "host": "localhost",
    "database": "jobs_db",
    "user": "postgres",
    "password": "your_password_here"
}
```

---

## Usage

### Step 1 — Run the ETL Pipeline

Fetches jobs from the RemoteOK API, filters for data/tech roles, and inserts them into the `jobs` table:

```bash
python pipeline.py
```

Expected output:
```
Filtered jobs: <N>
✅ Data inserted successfully
```

### Step 2 — Launch the Dashboard

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## Pipeline: `pipeline.py`

### What it does

1. **Extract** — Calls the [RemoteOK API](https://remoteok.com/api) with a browser `User-Agent` header.
2. **Transform** — Parses each job into a flat record with `title`, `company`, `location`, `tags`, `salary_min`, and `salary_max`. Filters to roles matching any of these keywords:

   `data`, `analytics`, `engineer`, `ml`, `ai`, `python`, `sql`

   Deduplicates on `(title, company)`.

3. **Load** — Inserts each filtered job row into the `jobs` PostgreSQL table.

---

## Dashboard: `app.py`

### Features

**Sidebar Filters**
- Keyword search across job title and tags
- Filter by company
- Filter by location

**KPI Metrics**
- Most in-demand skill (top tag across filtered jobs)
- Top hiring company

**Charts**
- Top 10 hiring companies
- Top 10 skills (from tags)
- Top 10 job roles
- Top 10 locations
- Remote vs. onsite breakdown
- Salary distribution (`salary_max`)

**Data Export**
- Download the current filtered view as a CSV file

**Raw Data Table**
- Full paginated view of filtered results

### Logging

All DB connection events and data load results are written to `dashboard.log`:

```
2025-01-01 10:00:00 - INFO - DB connection successful
2025-01-01 10:00:01 - INFO - Loaded 342 rows
```

---

## Security Notice

> ⚠️ The database password is currently hardcoded in both `pipeline.py` and `app.py`. **Do not commit these files to version control as-is.**

Move credentials to environment variables before deploying:

```bash
export DB_HOST=localhost
export DB_NAME=jobs_db
export DB_USER=postgres
export DB_PASSWORD=your_password
```

Then update the connection config:

```python
import os

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "database": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"]
}
```

Alternatively, use a `.env` file with the `python-dotenv` package and add `.env` to `.gitignore`.
