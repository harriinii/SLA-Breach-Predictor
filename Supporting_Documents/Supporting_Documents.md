# Supporting Documents — SLA Breach Prediction System

---

## 1. Architecture Decision Record

### ADR-01: LLM via Groq instead of direct OpenAI

**Decision:** Use Groq's hosted inference for Llama 3.3 70B rather than OpenAI GPT models.

**Rationale:**
- Groq provides significantly lower latency per token (sub-second for short prompts), which matters for real-time ticket creation UX.
- Llama 3.3 70B is sufficiently capable for structured classification tasks with a well-crafted system prompt.
- Cost is lower at comparable quality for this use case.

**Trade-offs:** Groq has lower rate limits than OpenAI on free tiers; bulk CSV imports are rate-limited to sequential processing to stay within limits.

---

### ADR-02: DynamoDB as the ticket store

**Decision:** Use AWS DynamoDB (via `src/dynamodb_service.py`) instead of a local CSV or SQLite store.

**Rationale:**
- Streamlit Community Cloud has an ephemeral filesystem; local files are lost on restart.
- DynamoDB provides durable, low-latency reads appropriate for a 30-second dashboard refresh cycle.
- The schema is flat (each ticket is a single item), which maps naturally to DynamoDB's key-value model.

**Trade-offs:** Requires AWS credentials at runtime; adds cold-start latency on first load.

---

### ADR-03: Streamlit as the frontend

**Decision:** Use Streamlit with custom CSS over a React or FastAPI+React stack.

**Rationale:**
- Single-developer project; Streamlit eliminates frontend/backend split.
- Plotly charts integrate natively.
- Deployment to Streamlit Community Cloud is zero-config.

**Trade-offs:** Limited layout control; custom CSS overrides are required for the dark-mode design system used in this project.

---

## 2. Data Flow

```
User submits ticket description
        │
        ▼
app.py: create_ticket()
        │
        ├─► src/llm_service.py: analyze_ticket(description)
        │       └─► Groq API: Llama 3.3 70B
        │               └─► returns (priority, complexity_score)
        │
        ├─► src/sla_engine.py: get_sla_hours(priority)
        │                       calculate_deadline(created_at, sla_hours)
        │
        ├─► src/dynamodb_service.py: save_ticket_to_db(ticket)
        │
        └─► twilio_alert.py: send_sla_sms_alert()  [if Critical or score ≥ 4]
                └─► Twilio WhatsApp API
```

**Dashboard refresh cycle (every 30 s):**

```
st_autorefresh fires
        │
        ▼
prepare_dashboard_data()
        ├─► load_tickets_from_db()      [DynamoDB scan]
        ├─► calculate_remaining_minutes() per ticket
        ├─► get_risk_status() per ticket
        └─► send_sla_sms_alert() for any ticket crossing 60-min threshold
                                  [deduplicated via st.session_state.sent_alerts]
```

---

## 3. Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key for LLM inference |
| `AWS_ACCESS_KEY_ID` | Yes | AWS credential for DynamoDB |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS credential for DynamoDB |
| `AWS_DEFAULT_REGION` | Yes | AWS region where DynamoDB table is hosted |
| `TWILIO_ACCOUNT_SID` | Yes | Twilio account SID for WhatsApp alerts |
| `TWILIO_AUTH_TOKEN` | Yes | Twilio auth token |
| `TWILIO_FROM_NUMBER` | Yes | Twilio WhatsApp sender number (e.g. `whatsapp:+14155238886`) |
| `TWILIO_TO_NUMBER` | Yes | Recipient WhatsApp number |

For local development, set these in a `.env` file (listed in `.gitignore`). For Streamlit Community Cloud, set them in the **Secrets** panel.

---

## 4. DynamoDB Table Schema

**Table name:** `sla_tickets` (configurable in `dynamodb_service.py`)

| Attribute | Type | Notes |
|---|---|---|
| `ticket_id` | String (PK) | Format: `T001`, `T002`, … |
| `customer_name` | String | Free text |
| `comment` | String | Raw issue description |
| `created_at` | String | ISO format: `YYYY-MM-DD HH:MM:SS` (IST) |
| `status` | String | `Open` → `In Progress` → `Resolved` → `Closed` |
| `priority` | String | `Low` / `Medium` / `High` / `Critical` |
| `complexity_score` | Number | 1–5 |
| `sla_hours` | Number | 24 / 8 / 4 / 2 |
| `sla_deadline` | String | ISO format (IST) |

No secondary indexes are required; the dashboard loads all tickets via a full table scan.

---

## 5. Local Setup

```bash
# Clone the repository
git clone https://github.com/srinitish/SLA-Breach-Prediction-System.git
cd SLA-Breach-Prediction-System

# Install dependencies (Python 3.11+ recommended)
pip install -r requirements.txt

# Set environment variables
cp .env.example .env   # then fill in your keys

# Run the app
streamlit run app.py
```

---

## 6. Deployment (Streamlit Community Cloud)

1. Push code to GitHub (main branch).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select the repository and set **Main file path** to `app.py`.
4. Under **Advanced settings → Secrets**, paste all environment variables in TOML format:

```toml
GROQ_API_KEY = "gsk_..."
AWS_ACCESS_KEY_ID = "AKIA..."
AWS_SECRET_ACCESS_KEY = "..."
AWS_DEFAULT_REGION = "ap-south-1"
TWILIO_ACCOUNT_SID = "AC..."
TWILIO_AUTH_TOKEN = "..."
TWILIO_FROM_NUMBER = "whatsapp:+14155238886"
TWILIO_TO_NUMBER = "whatsapp:+91XXXXXXXXXX"
```

5. Deploy. The app auto-redeploys on each push to main.

---

## 7. Known Limitations

- **No authentication.** The dashboard is publicly accessible on Streamlit Community Cloud. Add `streamlit-authenticator` or move to a private deployment for production use.
- **Sequential CSV processing.** Large CSVs (>50 rows) will take several minutes due to per-ticket LLM calls.
- **Single DynamoDB table scan.** For high ticket volumes (>10k), add a GSI on `status` to avoid full scans on every refresh.
- **IST timezone hardcoded.** `IST = pytz.timezone("Asia/Kolkata")` is set globally. Multi-region deployments need timezone parameterisation.
