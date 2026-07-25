# 🛡️ CyberSOC Intelligence Platform

An AI-powered Security Operations Center (SOC) dashboard designed to help security analysts investigate, manage, and analyze cybersecurity incidents through an interactive dashboard integrated with Google's Gemini AI.

---

## 📌 Overview

CyberSOC Intelligence Platform is a Python-based Security Operations Center (SOC) application that combines traditional incident management with Artificial Intelligence.

The platform enables analysts to:

- View and manage security incidents
- Store and retrieve incidents from a MySQL database
- Perform AI-assisted incident analysis
- Ask security-related questions using Google Gemini
- Monitor incident information through an intuitive dashboard

This project demonstrates how AI can enhance SOC workflows by providing intelligent insights during security investigations.

---

## 🚀 Features

- 📊 Interactive SOC Dashboard
- 🤖 Google Gemini AI Integration
- 🗄️ MySQL Database Connectivity
- 🔍 AI-assisted Incident Analysis
- 📋 Incident Management
- ⚡ Real-time Database Operations
- 🔐 Environment Variable Support using `.env`
- 🐍 Built entirely with Python

---

## 🏗️ Project Structure

```
CyberSOC-Intelligence-Platform/
│
├── app.py                 # Main Streamlit application
├── db.py                  # Database connection & queries
├── ai_helper.py           # Gemini AI integration
├── soc.sql                # MySQL database schema
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not included)
└── README.md
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend Development |
| Streamlit | Dashboard Interface |
| MySQL | Database |
| Google Gemini AI | AI-powered Analysis |
| Python Dotenv | Environment Variables |
| Pandas | Data Processing |

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/OfficialSubhayan/CyberSOC-Intelligence-Platform.git

cd CyberSOC-Intelligence-Platform
```

### Create Virtual Environment

```bash
python -m venv .venv
```

Activate it

Windows

```bash
.venv\Scripts\activate
```

Linux/Mac

```bash
source .venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Setup

1. Create a MySQL database.

2. Import the SQL file.

```sql
source soc.sql;
```

---

## 🔑 Configure Environment Variables

Create a `.env` file.

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password

GOOGLE_API_KEY=your_gemini_api_key
```

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

The dashboard will open automatically in your browser.

---

## 🤖 AI Module

The application integrates Google Gemini AI to assist SOC analysts by:

- Explaining security incidents
- Summarizing alerts
- Providing threat analysis
- Answering cybersecurity-related queries
- Improving analyst productivity

---

## 📂 Database

The project uses MySQL for storing SOC incident information.

Typical information includes:

- Incident ID
- Incident Type
- Severity
- Source
- Status
- Description
- Timestamp

---

## 📸 Dashboard Preview

> Add screenshots of your dashboard here.

Example:

<img width="1900" height="820" alt="image" src="https://github.com/user-attachments/assets/7ae5f7bd-60c4-4b70-b1c0-b442b5651be1" />

---

## 📈 Future Enhancements

- SIEM Integration
- Threat Intelligence APIs
- User Authentication
- Alert Correlation
- MITRE ATT&CK Mapping
- Incident Timeline
- PDF Report Generation
- Role-Based Access Control
- SOC Analytics Dashboard

---

## 🎯 Learning Objectives

This project demonstrates practical knowledge of:

- Python Programming
- SQL Database Management
- AI Integration
- Environment Variable Management
- Streamlit Dashboard Development
- Security Operations Center (SOC) Concepts
- Incident Management

---

## 👥 Team Contributions

| Team Member | Contribution |
|-------------|--------------|
| **Sarthak Mukherjee** | Database Design & SQL Development |
| **Surojit Jana** | Streamlit Dashboard Development |
| **Sayar Sekhar Ghosh** | AI Integration & Testing |
| **Subhayan Mitra** | Backend Development, Database Connectivity, Project Integration & GitHub Management |

---

## ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.
