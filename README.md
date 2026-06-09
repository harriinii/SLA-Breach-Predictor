# 🚀 AI-Powered SLA Breach Prediction System

An intelligent support ticket monitoring platform that uses Large Language Models (LLMs) to automatically analyze support tickets, assign severity levels, predict SLA breach risks, generate real-time alerts, and provide operational analytics through an interactive Streamlit dashboard.

---

## 📌 Project Overview

Organizations often struggle to identify support tickets that are likely to violate Service Level Agreements (SLAs). Manual monitoring becomes difficult as ticket volumes increase.

This project solves that problem by leveraging AI-powered ticket classification and SLA intelligence to:

- Analyze ticket descriptions automatically
- Assign complexity scores (1–5)
- Determine ticket priority levels
- Calculate SLA deadlines dynamically
- Predict potential SLA breaches
- Generate critical alerts
- Provide real-time operational analytics
- Send WhatsApp notifications for high-risk incidents

---

## 🎯 Problem Statement

Support teams receive hundreds of tickets daily.

Without intelligent prioritization:

- Critical incidents may be overlooked
- SLA deadlines can be missed
- Customer satisfaction decreases
- Revenue-impacting issues remain unresolved

This system acts as an AI-powered Support Operations Assistant that continuously monitors tickets and identifies potential SLA violations before they occur.

---

# 🏗 System Architecture

```text
                +---------------------+
                |   Support Engineer  |
                +----------+----------+
                           |
                           v
                +---------------------+
                | Ticket Submission   |
                | (Manual / CSV)      |
                +----------+----------+
                           |
                           v
                +---------------------+
                | LLM Severity Engine |
                | (Groq Llama 3.3)    |
                +----------+----------+
                           |
        +------------------+------------------+
        |                                     |
        v                                     v

+--------------------+           +--------------------+
| Complexity Score   |           | Priority Mapping   |
|      (1-5)         |           | Low / Med / High   |
+---------+----------+           +---------+----------+
          |                                |
          +---------------+----------------+
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
           +---------------+---------------+
           |                               |
           v                               v

+---------------------+       +----------------------+
| Dashboard Analytics |       | WhatsApp Alerts      |
| Streamlit           |       | Twilio API           |
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

Bulk ticket upload using:

```csv
customer_name,comment
Ram,The company logo is slightly misaligned.
Ravi,One customer cannot download invoice.
```

---

## Step 2: AI Ticket Analysis

The ticket description is sent to the LLM.

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

Based on complexity score:

| Complexity | Priority |
|------------|----------|
| 1-2 | Low |
| 3 | Medium |
| 4 | High |
| 5 | Critical |

---

## Step 4: SLA Deadline Calculation

Each priority receives a predefined SLA window.

| Priority | SLA |
|-----------|------|
| Low | 24 Hours |
| Medium | 8 Hours |
| High | 4 Hours |
| Critical | 2 Hours |

Example:

```text
Created Time:
10:00 AM

Priority:
High

SLA:
4 Hours

Deadline:
2:00 PM
```

---

## Step 5: Risk Detection

Remaining time is continuously calculated.

```python
Remaining Time =
SLA Deadline - Current Time
```

Risk Levels:

### Normal

```text
More than 60 minutes remaining
```

### At Risk

```text
Less than 60 minutes remaining
```

### Breached

```text
Remaining time < 0
```

---

## Step 6: Critical Alert Generation

When:

- Remaining Time < 60 Minutes

OR

- Complexity Score = 5

The ticket enters:

```text
CRITICAL BREACH RISK
```

and appears in:

- Dashboard Alert Panel
- WhatsApp Notifications

---

## Step 7: Ticket Resolution

Support Engineers can update status:

```text
Open
↓
In Progress
↓
Resolved
↓
Closed
```

Completed tickets are automatically moved to:

```text
Resolved & Closed Tickets
```

while maintaining historical records.

---

# 🧠 AI Severity Classification Model

The system uses:

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
Authentication system down
Complete application outage
```

---

# 📊 Dashboard Features

### Operational Dashboard

Displays:

- Total Tickets
- Active Tickets
- Critical Tickets
- Breached Tickets
- At Risk Tickets

---

### Active Ticket Management

Allows:

- Status Updates
- SLA Tracking
- Risk Monitoring

---

### Critical Alert Panel

Highlights:

- Tickets nearing SLA breach
- High-risk incidents
- Critical outages

---

### Analytics Dashboard

Provides:

- Priority Distribution
- Risk Status Analysis
- Complexity Trends
- Resolution Metrics
- Breach Rate Analysis

---

### Historical Records

Stores:

- Resolved Tickets
- Closed Tickets
- SLA Performance History

---

# 📱 WhatsApp Alert System

Integrated using:

```text
Twilio WhatsApp API
```

Automatically sends alerts for:

```text
CRITICAL BREACH RISK

Ticket ID: T012
Customer: Emergency Client
Time Remaining: 29 Minutes

Action Required Immediately
```

---

# 🖥 Screenshots

## Create Ticket Module

![Create Ticket](images/upload_file.png)

---

## Operational Dashboard

![Dashboard](images/dashboard.png)

---

## Analytics Dashboard

![Analytics](images/analysis.png)

---

## Resolved & Closed Tickets

![Resolved](images/resolved.png)

---

## WhatsApp Critical Alert

![Alert](images/alert_message.jpeg)

---

# 🛠 Tech Stack

## Frontend

- Streamlit

## Backend

- Python

## AI

- Groq API
- Llama 3.3 70B

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
├── app.py
├── requirements.txt
├── data/
│   └── tickets.csv
│
├── src/
│   ├── llm_service.py
│   ├── sla_engine.py
│   ├── ticket_service.py
│   ├── whatsapp_alert.py
│   └── analytics.py
│
└── README.md
```

---

# 🚀 Future Enhancements

- Email Alerts
- Multi-Agent AI Architecture
- Root Cause Analysis
- SLA Forecasting
- Predictive Ticket Escalation
- Team Performance Analytics
- AWS Cloud Deployment
- RAG-based Incident Knowledge Base

---

# 📈 Business Benefits

✅ Reduced SLA Violations

✅ Faster Incident Response

✅ Improved Customer Satisfaction

✅ Automated Ticket Prioritization

✅ Real-Time Risk Monitoring

✅ Better Operational Visibility

---

# 👨‍💻 Author

**Sri Nitish**

B.Tech Information Technology

AI / Machine Learning Enthusiast

---

## ⭐ If you found this project useful, give it a star on GitHub.