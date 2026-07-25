# 🛡️ CyberSOC Intelligence Platform

An AI-powered Security Operations Center (SOC) dashboard that combines traditional incident management with AI-assisted analysis, built with Streamlit, MySQL, and Groq.

---

## 📌 Overview

CyberSOC Intelligence Platform is a Python-based SOC application that lets analysts investigate, manage, and analyze security incidents through an interactive dashboard, backed by a MySQL database and an AI assistant powered by Groq's fast open-model inference.

The platform enables analysts to:

- View and manage security incidents
- Detect brute-force login patterns and flag suspicious activity
- Track assets by criticality and link them to incidents
- Run ad-hoc read-only SQL queries against the incident data
- Get AI-generated incident summaries and ask natural-language questions about the current data

---

## 🚀 Features

- 📊 Interactive multi-page SOC dashboard (Overview, Incidents, Brute-Force Detection, Assets, Add Incident, Ad-hoc Query, AI Assistant)
- 🤖 AI-assisted incident summaries and Q&A via Groq
- 🗄️ MySQL schema with tables, a view, a trigger, and stored procedures
- 🔐 Role-based access control (`soc_analyst` read-only role, `soc_admin` full-access role)
- 🔎 Full-text search over incident titles
- ⚡ Real-time queries and charts (Altair)
- 🐍 Built entirely with Python

---

## 🏗️ Project Structure

```
CyberSOC-Intelligence-Platform/
│
├── app.py                 # Main Streamlit application (all dashboard pages)
├── query_handlers.py      # MySQL connection, SELECT/write queries, stored-procedure calls
├── db_config.py           # One-time DB setup: creates schema, tables, view, trigger, procedures, RBAC users
├── ai_helper.py           # Groq AI integration (incident summaries, data Q&A)
├── soc.sql                # Full MySQL schema, sample data, view/trigger/procedure definitions
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not committed — create this yourself)
└── README.md
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend development |
| Streamlit | Dashboard interface |
| MySQL | Database |
| Groq | AI-powered incident analysis |
| mysql-connector-python | Database driver |
| python-dotenv | Environment variable management |
| Pandas / Altair | Data processing & charts |

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/OfficialSubhayan/CyberSOC-Intelligence-Platform.git
cd CyberSOC-Intelligence-Platform
```

### Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**
```bash
.venv\Scripts\activate
```

**Linux/Mac**
```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=SecurityOpsCenter

GROQ_API_KEY=your_groq_api_key
```

> Get a Groq API key at [console.groq.com](https://console.groq.com).

---

## 🗄️ Database Setup

Make sure a MySQL server is running and reachable with the credentials in your `.env`. That's it — you don't need to run anything else manually.

The first time you launch the app (see [Run the Application](#️-run-the-application) below), it automatically checks whether the `SecurityOpsCenter` database exists yet. If it doesn't, it creates the schema, seeds sample data, and sets up the view, trigger, stored procedures, and RBAC users for you — you'll see a brief "Checking database..." spinner while this happens. On every run after that, the check finds the database already there and skips setup instantly, so your data (added incidents, etc.) is never wiped by a normal restart.

If you ever want to force a full reset back to the seeded sample data, you can still run the initializer directly — **note this drops and recreates the entire database**, discarding any data you've added:

```bash
python db_config.py
```

You should see:
```
Connecting to MySQL server...
Executing 55 SQL statements...
Database initialization complete.
```

If a specific statement fails, the script prints which one and its SQL so you can diagnose it directly.

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

The dashboard opens automatically in your browser.

---

## 🤖 AI Module

The AI Assistant page uses Groq to:

- Summarize a selected incident in plain English for non-technical stakeholders
- Answer natural-language questions grounded strictly in the current incident data (it's instructed not to invent details)

Model used: `groq/compound` 

---

## 📂 Database Schema Highlights

| Object | Type | Purpose |
|--------|------|---------|
| `Employees`, `Assets`, `Vulnerabilities`, `Incidents`, `AccessLogs` | Tables | Core SOC data |
| `IncidentAssets`, `IncidentVulnerabilities` | Tables | Many-to-many links |
| `SuspiciousActivity` | View | Employees/assets with ≥3 failed access attempts |
| `trg_flag_critical_incident` | Trigger | Auto-escalates an incident to Critical severity when a linked vulnerability is Critical |
| `GetIncidentsByAsset(assetID)` | Procedure | Lists incidents tied to a given asset |
| `LockAccountAfterNFailures(employeeID, threshold)` | Procedure | Flags an employee who exceeded N failed logins in the last hour |
| `soc_analyst` / `soc_admin` | MySQL users | Read-only vs. full-access roles |

---

## 📈 Future Enhancements

- SIEM integration
- Threat intelligence API feeds
- User authentication for the dashboard itself
- Alert correlation across incidents
- MITRE ATT&CK mapping
- Incident timeline view
- PDF report generation

---

## 🎯 Learning Objectives

This project demonstrates practical experience with:

- Python & Streamlit application development
- SQL database design (schema, views, triggers, stored procedures, RBAC)
- AI integration for real-world analyst workflows
- Environment variable / secrets management
- Security Operations Center (SOC) concepts and incident management

---

## 👥 Team Contributions

| Team Member | Contribution |
|-------------|--------------|
| **Sarthak Mukherjee** | Database design & SQL development |
| **Sayar Sekhar Ghosh** | AI integration & testing |
| **Subhayan Mitra** | Streamlit dashboard development & backend development |
| **Surojit Jana** | Database connectivity, project integration & GitHub management |

---

## ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.
