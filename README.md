# 🚀 AI-Powered SLA Breach Prediction System

An intelligent support ticket monitoring platform that uses Large Language Models (LLMs) to automatically analyze support tickets, assign severity levels, calculate SLA deadlines, predict SLA breach risks, generate WhatsApp alerts, and provide real-time operational analytics through an interactive Streamlit dashboard.

---

# 📌 Project Overview

Organizations often struggle to monitor hundreds of support tickets and identify which tickets are likely to violate Service Level Agreements (SLAs).

This project solves that problem using AI-powered ticket classification and SLA intelligence.

The system automatically:

- Analyzes support ticket descriptions using LLMs
- Assigns complexity scores (1–5)
- Determines ticket priority levels
- Calculates SLA deadlines dynamically
- Detects critical breach-risk tickets
- Sends WhatsApp alerts for urgent incidents
- Tracks ticket lifecycle from Open → Closed
- Provides real-time dashboards and analytics

---

# 🎯 Problem Statement

Support teams handle large volumes of tickets daily.

Without intelligent monitoring:

- Critical incidents may be overlooked
- SLA deadlines may be missed
- Customer satisfaction decreases
- Revenue-impacting issues remain unresolved

The AI-Powered SLA Breach Prediction System acts as a Support Operations Assistant that continuously evaluates ticket risk levels and highlights incidents requiring immediate attention.

---

# 🏗 System Architecture

```text
                +---------------------+
                | Support Engineer    |
                +----------+----------+
                           |
                           v

                +---------------------+
                | Ticket Creation     |
                | Manual / CSV Upload |
                +----------+----------+
                           |
                           v

                +---------------------+
                | Groq LLM Engine     |
                | Llama-3.3-70B       |
                +----------+----------+
                           |
                           v

                +---------------------+
                | Complexity Scoring  |
                | Score: 1 - 5        |
                +----------+----------+
                           |
                           v

                +---------------------+
                | Priority Mapping    |
                | Low / Med / High    |
                | Critical            |
                +----------+----------+
                           |
                           v

                +---------------------+
                | SLA Engine          |
                | Deadline Generator  |
                +----------+----------+
                           |
                           v

                +---------------------+
                | Risk Evaluation     |
                | Normal              |
                | At Risk             |
                | Breached            |
                +----------+----------+
                           |
            +--------------+--------------+
            |                             |
            v                             v

+---------------------+       +----------------------+
| Streamlit Dashboard |       | WhatsApp Alerts      |
| Analytics & Reports |       | Twilio API           |
+---------------------+       +----------------------+
```

---

# ⚙️ Workflow

## Step 1: Ticket Creation

Tickets can be created through:

### Manual Entry

Support engineer enters:

- Customer Name
- Ticket Description

### CSV Upload

Bulk ticket upload:

```csv
customer_name,comment
Ram,The company logo is slightly misaligned.
Ravi,One customer cannot download invoice.
```

---

## Step 2: AI Ticket Analysis

The ticket description is sent to the Groq LLM.

The model evaluates:

- Business Impact
- User Impact
- Technical Complexity
- Service Availability
- Revenue Impact

Output:

```text
Complexity Score = 1 to 5
```

---

## Step 3: Priority Assignment

| Complexity Score | Priority |
|-----------------|----------|
| 1 | Low |
| 2 | Low |
| 3 | Medium |
| 4 | High |
| 5 | Critical |

---

## Step 4: SLA Deadline Calculation

| Priority | SLA Window |
|----------|-----------|
| Low | 24 Hours |
| Medium | 8 Hours |
| High | 4 Hours |
| Critical | 2 Hours |

Example:

```text
Created Time : 10:00 AM
Priority     : High
SLA Window   : 4 Hours
Deadline     : 2:00 PM
```

---

## Step 5: Risk Detection

The system continuously calculates:

```python
Remaining Time = SLA Deadline - Current Time
```

Risk Levels:

### 🟢 Normal

More than 60 minutes remaining

### 🟠 At Risk

Less than 60 minutes remaining

### 🔴 Breached

Remaining time less than 0

---

## Step 6: Critical Alert Generation

When:

- Remaining Time < 60 Minutes

OR

- Complexity Score = 5

The ticket becomes:

```text
CRITICAL BREACH RISK
```

The ticket is immediately displayed in:

- Critical Alert Panel
- Dashboard Monitoring Section
- WhatsApp Alert System

---

## Step 7: Ticket Resolution Lifecycle

```text
Open
 ↓
In Progress
 ↓
Resolved
 ↓
Closed
```

Resolved and Closed tickets are automatically moved to a dedicated historical records page.

---

# 🧠 AI Severity Classification

Model Used:

```text
Groq API
Llama-3.3-70B-Versatile
```

Severity Levels:

| Score | Description |
|---------|-------------|
| 1 | Cosmetic Issue |
| 2 | Single User Issue |
| 3 | Functional Bug |
| 4 | Major Service Impact |
| 5 | Critical Outage |

Examples:

### Score 1

```text
Logo alignment issue
```

### Score 2

```text
One customer cannot download invoice
```

### Score 3

```text
Several users unable to export reports
```

### Score 4

```text
Payment gateway failures affecting many users
```

### Score 5

```text
Production database crash
Authentication service outage
Entire application unavailable
```

---

# 📊 Features

## 📝 Create Support Ticket

- Manual ticket creation
- Bulk CSV upload
- Instant AI severity analysis
- Automatic SLA calculation

![Create Ticket Module](images/upload_file.png)

---

## 📈 Operational Dashboard

Displays:

- Total Tickets
- Active Tickets
- Critical Priority Tickets
- Breached Tickets
- At Risk Tickets
- Live SLA Countdown
- Inline Status Updates

![Operational Dashboard](images/dashboard.png)

---

## 📊 SLA Analysis Dashboard

Provides:

- Breach Rate Analysis
- Priority Distribution
- Risk Status Distribution
- Complexity Trends
- Resolution Performance

![Analysis Dashboard](images/analysis.png)

---

## ✅ Resolved & Closed Tickets

Maintains historical records for:

- Resolved Tickets
- Closed Tickets
- Resolution Metrics
- Customer Statistics

![Resolved Tickets](images/resolved.png)

---

## 📱 WhatsApp Critical Alerts

Integrated using:

```text
Twilio WhatsApp API
```

Example Alert:

```text
🚨 SLA OUTAGE EMERGENCY DISPATCH 🚨

Ticket ID: T012
Customer: Emergency Client

Current Risk State:
CRITICAL COUNTDOWN

Time Left:
29 Minutes before breach

Immediate action required.
```

![WhatsApp Alert](images/alert_message.jpeg)

---

# 📊 Analytics Provided

The system automatically generates:

- Breach Rate
- Resolution Rate
- Average Complexity
- Average SLA Window
- Priority Distribution
- Risk Status Distribution
- Ticket Status Breakdown

---

# 🛠 Tech Stack

## Frontend

- Streamlit

## Backend

- Python

## AI

- Groq API
- Llama 3.3 70B Versatile

## Data Processing

- Pandas
- NumPy

## Visualization

- Plotly

## Notifications

- Twilio WhatsApp API

## Deployment

- Streamlit Community Cloud

---

# 📂 Project Structure

```text
AI-Powered-SLA-Breach-Prediction-System/
│
├── app.py
├── requirements.txt
├── README.md
│
├── images/
│   ├── upload_file.png
│   ├── dashboard.png
│   ├── analysis.png
│   ├── resolved.png
│   └── alert_message.jpeg
│
├── data/
│   └── tickets.csv
│
├── src/
│   ├── llm_service.py
│   ├── sla_engine.py
│   ├── analytics.py
│   ├── ticket_service.py
│   └── whatsapp_alert.py
│
└── .env
```

---

# 🚀 Future Enhancements

- Email Alert Integration
- Multi-Agent AI Architecture
- Root Cause Analysis
- SLA Forecasting
- Predictive Escalation Engine
- Knowledge Base Integration
- RAG-Powered Incident Resolution
- Cloud-Native Deployment

---

# 📈 Business Benefits

✅ Reduced SLA Violations

✅ Faster Incident Response

✅ Automated Ticket Prioritization

✅ Real-Time Risk Monitoring

✅ Improved Customer Satisfaction

✅ Better Operational Visibility

✅ Proactive Incident Management

---

# 👨‍💻Team Members

- HARINI
- SRI NITISH
- SARIGA
- ATHISH


---

## ⭐ If you found this project useful, please give it a Star.
