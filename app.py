import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

from twilio_alert import send_sla_sms_alert
from src.llm_service import analyze_ticket, generate_risk_reason
from src.sla_engine import get_sla_hours, calculate_deadline
from src.dynamodb_service import (
    save_ticket_to_db,
    load_tickets_from_db,
    update_ticket_status_db
)

IST = pytz.timezone("Asia/Kolkata")

st.set_page_config(
    page_title="SLA Breach Predictor",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Reset & Base ─────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Remove default streamlit padding to use full width */
.main .block-container {
    padding: 1.5rem 2rem 2rem 2rem !important;
    max-width: 100% !important;
}

[data-testid="stAppViewContainer"] { background: #0d1117; color: #e6edf3; }
[data-testid="stSidebar"] { background: #0d1117 !important; border-right: 1px solid #21262d; }
[data-testid="stHeader"] { background: transparent; display:none; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stToolbar"] { display: none; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

/* ── Sidebar ─────────────────────────────────────────── */
.sb-brand {
    padding: 20px 16px 20px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 8px;
}
.sb-brand-row {
    display: flex; align-items: center; gap: 10px;
}
.sb-brand-icon { font-size: 26px; }
.sb-brand-name {
    font-size: 15px; font-weight: 700;
    color: #e6edf3; letter-spacing: -0.01em;
}
.sb-brand-tag {
    font-size: 10px; color: #58a6ff;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-top: 2px;
}
.sb-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; color: #484f58;
    margin-top: 10px; padding-top: 10px;
    border-top: 1px solid #21262d;
}
.sb-nav-label {
    font-size: 10px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.1em;
    color: #484f58; padding: 14px 16px 6px;
}
.sb-section-label {
    font-size: 10px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.1em;
    color: #484f58; padding: 16px 0 8px;
}
.sb-alert-item {
    background: #1a0f0f; border: 1px solid #3d1c1c;
    border-left: 3px solid #f78166;
    border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;
}
.sb-alert-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; font-weight: 700; color: #f78166; margin-bottom: 3px;
}
.sb-alert-text { font-size: 11px; color: #8b949e; line-height: 1.4; }
.sb-ok {
    background: #0d1f14; border: 1px solid #1e4026;
    border-radius: 8px; padding: 10px 12px;
    font-size: 12px; color: #3fb950; text-align: center;
}

/* ── Radio nav styling ───────────────────────────────── */
[data-testid="stRadio"] > div { gap: 2px !important; }
[data-testid="stRadio"] label {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 9px 14px !important;
    font-size: 13px !important; font-weight: 500 !important;
    color: #8b949e !important; cursor: pointer !important;
    display: flex !important; align-items: center !important;
    transition: all 0.15s !important; width: 100% !important;
}
[data-testid="stRadio"] label:hover {
    background: #161b22 !important; color: #e6edf3 !important;
}
[data-testid="stRadio"] label:has(input:checked) {
    background: #1c2128 !important; color: #58a6ff !important;
    border-left: 2px solid #58a6ff !important;
}
[data-testid="stRadio"] label p { margin: 0 !important; }

/* ── Page hero ───────────────────────────────────────── */
.page-hero {
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    border: 1px solid #30363d; border-radius: 12px;
    padding: 22px 28px; margin-bottom: 22px;
    position: relative; overflow: hidden;
}
.page-hero::before {
    content: ""; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #58a6ff 0%, #3fb950 50%, #f78166 100%);
}
.page-hero h1 {
    font-size: 22px; font-weight: 700; color: #e6edf3;
    margin: 0 0 4px; letter-spacing: -0.02em;
}
.page-hero p { font-size: 12px; color: #8b949e; margin: 0; }

/* ── KPI Grid ────────────────────────────────────────── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px; margin-bottom: 22px;
}
.kpi-card {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 10px; padding: 16px 18px;
    position: relative; overflow: hidden;
    transition: border-color 0.2s, transform 0.15s;
}
.kpi-card:hover { border-color: #30363d; transform: translateY(-1px); }
.kpi-label {
    font-size: 10px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.1em; color: #484f58;
    margin-bottom: 6px;
}
.kpi-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 30px; font-weight: 700; line-height: 1;
}
.kpi-bar { height: 2px; border-radius: 1px; margin-top: 10px; width: 36px; }

.kpi-blue  .kpi-val { color: #58a6ff; }  .kpi-blue  .kpi-bar { background: #58a6ff; }
.kpi-green .kpi-val { color: #3fb950; }  .kpi-green .kpi-bar { background: #3fb950; }
.kpi-amber .kpi-val { color: #e3b341; }  .kpi-amber .kpi-bar { background: #e3b341; }
.kpi-red   .kpi-val { color: #f78166; }  .kpi-red   .kpi-bar { background: #f78166; }
.kpi-purple.kpi-val { color: #d2a8ff; }  .kpi-purple .kpi-bar { background: #d2a8ff; }

/* ── Inline table with status dropdowns ──────────────── */
.ticket-table-wrap {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 10px; overflow: hidden; margin-bottom: 22px;
    width: 100%;
}
.ticket-table-header {
    display: grid;
    grid-template-columns: 80px 140px 1fr 150px 110px 80px 80px 80px 140px 90px 155px 140px;
    background: #0d1117; border-bottom: 1px solid #21262d;
    padding: 10px 0;
}
.ticket-table-header-cell {
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #484f58; padding: 0 12px;
}
.ticket-row {
    display: grid;
    grid-template-columns: 80px 140px 1fr 150px 110px 80px 80px 80px 140px 90px 155px 140px;
    border-bottom: 1px solid #21262d;
    padding: 6px 0; align-items: center;
    transition: background 0.15s;
}
.ticket-row:last-child { border-bottom: none; }
.ticket-row:hover { background: #1c2128; }
.ticket-row.row-breached { background: #1a0f0f; }
.ticket-row.row-risk     { background: #150f1a; }
.ticket-row.row-done     { background: #0d1a10; }
.ticket-cell {
    font-size: 12px; color: #c9d1d9; padding: 0 12px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.ticket-cell.mono {
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
}
.tc-id { color: #58a6ff; font-weight: 600; }

/* priority pill */
.pill {
    display: inline-block; padding: 2px 8px;
    border-radius: 20px; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.06em; white-space: nowrap;
}
.pill-critical { background:#2d1a0a; color:#e3b341; border:1px solid #4a2e10; }
.pill-high     { background:#3d1c1c; color:#f78166; border:1px solid #5a2020; }
.pill-medium   { background:#0e2233; color:#58a6ff; border:1px solid #1a3a55; }
.pill-low      { background:#0d1f14; color:#3fb950; border:1px solid #1e4026; }
.pill-breached { background:#3d1c1c; color:#f78166; border:1px solid #f7816655; }
.pill-risk     { background:#1e0d33; color:#d2a8ff; border:1px solid #d2a8ff44; }
.pill-normal   { background:#0d1f14; color:#3fb950; border:1px solid #3fb95044; }
.pill-done     { background:#0e1d33; color:#58a6ff; border:1px solid #58a6ff44; }
.pill-open     { background:#21262d; color:#8b949e; border:1px solid #30363d; }
.pill-inprog   { background:#0e2233; color:#58a6ff; border:1px solid #1a3a55; }
.pill-resolved { background:#0d1f14; color:#3fb950; border:1px solid #1e4026; }
.pill-closed   { background:#161b22; color:#8b949e; border:1px solid #30363d; }

/* ── Inputs / Buttons ────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #0d1117 !important; border: 1px solid #30363d !important;
    border-radius: 8px !important; color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important; font-size: 13px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #58a6ff !important; box-shadow: 0 0 0 3px #58a6ff1a !important;
}
[data-testid="stFormSubmitButton"] button,
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #1f6feb, #388bfd) !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    font-size: 13px !important; letter-spacing: 0.02em !important;
    box-shadow: 0 2px 8px #1f6feb33 !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
[data-testid="stFormSubmitButton"] button:hover,
[data-testid="stButton"] button:hover {
    opacity: 0.88 !important; transform: translateY(-1px) !important;
}

/* ── Selectbox ───────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: #0d1117 !important; border: 1px solid #30363d !important;
    border-radius: 8px !important; color: #e6edf3 !important; font-size: 13px !important;
}
[data-testid="stMultiSelect"] > div > div {
    background: #0d1117 !important; border: 1px solid #30363d !important;
    border-radius: 8px !important;
}

/* ── Tabs ────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    background: #161b22; border-radius: 10px;
    padding: 4px; border: 1px solid #21262d; gap: 4px;
}
[data-testid="stTabs"] [role="tab"] {
    border-radius: 7px !important; font-size: 13px !important;
    font-weight: 500 !important; color: #8b949e !important; padding: 8px 18px !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #21262d !important; color: #e6edf3 !important;
}

/* ── Charts container ────────────────────────────────── */
.chart-card {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 10px; padding: 20px; margin-bottom: 16px;
}
.chart-title {
    font-size: 12px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #8b949e; margin-bottom: 14px;
}

/* ── Ticket created card ─────────────────────────────── */
.created-card {
    background: #161b22; border: 1px solid #1e4026;
    border-radius: 10px; padding: 20px 24px; margin-top: 16px;
}
.created-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px; font-weight: 700; color: #3fb950; margin-bottom: 14px;
}
.created-meta { display: flex; gap: 24px; flex-wrap: wrap; }
.meta-item { }
.meta-lbl { font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; color: #484f58; margin-bottom: 3px; }
.meta-val { font-size: 22px; font-weight: 700; color: #e6edf3; }
.meta-dl { margin-top: 14px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #484f58; }

/* ── Section heading ─────────────────────────────────── */
.sec-head {
    font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.1em;
    color: #484f58; margin: 20px 0 12px; display: flex; align-items: center; gap: 8px;
}
.sec-head::after {
    content: ""; flex: 1; height: 1px; background: #21262d;
}

/* ── Analysis page ───────────────────────────────────── */
.analysis-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;
}
.analysis-grid-3 {
    display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 16px;
}
.insight-card {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 10px; padding: 20px; position: relative;
}
.insight-label {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: #484f58; margin-bottom: 8px;
}
.insight-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px; font-weight: 700; color: #e6edf3; line-height: 1;
}
.insight-sub { font-size: 11px; color: #8b949e; margin-top: 4px; }

/* ── Misc ────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #161b22; border: 1px solid #21262d; border-radius: 10px;
    padding: 14px 18px;
}
[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 11px !important; }
[data-testid="stMetricValue"] { color: #58a6ff !important; font-size: 24px !important; }
[data-testid="stAlert"] { border-radius: 8px !important; }
hr { border-color: #21262d !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #58a6ff; }

/* ── Spinner ─────────────────────────────────────────── */
[data-testid="stSpinner"] > div { border-top-color: #58a6ff !important; }

/* ── CSV info ────────────────────────────────────────── */
.csv-info {
    background: #0e1d33; border: 1px solid #1a3a55; border-radius: 8px;
    padding: 10px 14px; font-size: 12px; color: #58a6ff; margin-bottom: 14px;
}

/* ── Progress bar ────────────────────────────────────── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #1f6feb, #3fb950) !important;
}
</style>
""", unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
if "sent_alerts" not in st.session_state:
    st.session_state.sent_alerts = set()
if "status_updates" not in st.session_state:
    st.session_state.status_updates = {}

# ══════════════════════════════════════════════════════════
# DATA HELPERS
# ══════════════════════════════════════════════════════════
def load_tickets():
    items = load_tickets_from_db()
    if items:
        return pd.DataFrame(items)
    return pd.DataFrame(columns=[
        "ticket_id","customer_name","comment","created_at",
        "status","priority","complexity_score","sla_hours","sla_deadline"
    ])

def save_ticket(ticket):      save_ticket_to_db(ticket)
def _update_db(tid, ns):      update_ticket_status_db(tid, ns)

def get_next_ticket_id():
    df = load_tickets()
    return f"T{len(df) + 1:03d}"

def create_ticket(customer_name, comment):
    created_at = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    priority, complexity_score = analyze_ticket(comment)
    sla_hours  = get_sla_hours(priority)
    deadline   = calculate_deadline(created_at, sla_hours)
    ticket = {
        "ticket_id": get_next_ticket_id(),
        "customer_name": customer_name,
        "comment": comment,
        "created_at": created_at,
        "status": "Open",
        "priority": priority,
        "complexity_score": complexity_score,
        "sla_hours": sla_hours,
        "sla_deadline": deadline
    }
    save_ticket(ticket)
    try:
        score = int(complexity_score)
    except:
        score = 0
    if str(priority).lower() == "critical" or score >= 4:
        try:
            send_sla_sms_alert(
                customer_name=customer_name, ticket_id=ticket["ticket_id"],
                minutes_left=int(sla_hours * 60),
                risk_level=f"Priority={priority}, Complexity={complexity_score}"
            )
        except Exception as e:
            st.warning(f"SMS alert failed: {e}")
    return ticket

def calculate_remaining_minutes(deadline):
    dt = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
    dt = IST.localize(dt)
    return int((dt - datetime.now(IST)).total_seconds() / 60)

def get_risk_status(row):
    if row["status"] in ["Resolved", "Closed"]: return "Completed"
    if row["remaining_minutes"] < 0:             return "Breached"
    if row["remaining_minutes"] < 60 or int(row["complexity_score"]) > 4:
        return "CRITICAL BREACH RISK"
    return "Normal"

def prepare_dashboard_data():
    df = load_tickets()
    if not df.empty:
        # Apply any pending in-session status overrides
        for tid, ns in st.session_state.status_updates.items():
            df.loc[df["ticket_id"] == tid, "status"] = ns

        df["remaining_minutes"] = df["sla_deadline"].apply(calculate_remaining_minutes)
        df["risk_status"]       = df.apply(get_risk_status, axis=1)

        for _, row in df.iterrows():
            if row["status"] in ["Resolved", "Closed"]: continue
            if 0 < row["remaining_minutes"] <= 60:
                ak = f"{row['ticket_id']}_countdown"
                if ak not in st.session_state.sent_alerts:
                    try:
                        send_sla_sms_alert(
                            customer_name=row["customer_name"], ticket_id=row["ticket_id"],
                            minutes_left=row["remaining_minutes"], risk_level="CRITICAL COUNTDOWN"
                        )
                        st.session_state.sent_alerts.add(ak)
                    except Exception:
                        pass
    return df

def get_allowed_status_options(current_status):
    if current_status == "Open":       return ["In Progress","Resolved","Closed"]
    if current_status == "In Progress": return ["Resolved","Closed"]
    return []

@st.cache_data(ttl=600)
def get_ai_risk_reason(ticket_id, comment, complexity_score, remaining_minutes):
    try:
        return generate_risk_reason(comment, complexity_score, remaining_minutes)
    except Exception:
        return "Unable to generate AI reason."

def upload_csv_to_dynamodb(uploaded_file):
    csv_df = pd.read_csv(uploaded_file)
    for col in ["customer_name","comment"]:
        if col not in csv_df.columns:
            st.error(f"CSV must contain '{col}' column."); return
    created_count = 0
    progress = st.progress(0, text="Processing…")
    total = len(csv_df)
    for i, (_, row) in enumerate(csv_df.iterrows()):
        cn = str(row["customer_name"]).strip()
        cm = str(row["comment"]).strip()
        if cn and cm and cn != "nan" and cm != "nan":
            create_ticket(cn, cm); created_count += 1
        progress.progress((i+1)/total, text=f"Processing {i+1}/{total}…")
    progress.empty()
    st.success(f"✅ {created_count} tickets uploaded successfully.")

# ══════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════
CHART_COLORS = ["#58a6ff","#f78166","#e3b341","#3fb950","#d2a8ff","#79c0ff","#56d364"]

def chart_layout():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter",
            color="#e6edf3",
            size=16
        ),

        title_font=dict(
            color="#ffffff",
            size=22
        ),

        legend=dict(
            font=dict(
                color="#e6edf3",
                size=16
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(t=60, b=30, l=30, r=30)
    )

def priority_pill(p):
    cls = {"Critical":"pill-critical","High":"pill-high","Medium":"pill-medium","Low":"pill-low"}.get(p,"pill-low")
    return f'<span class="pill {cls}">{p}</span>'

def status_pill(s):
    cls = {"Open":"pill-open","In Progress":"pill-inprog","Resolved":"pill-resolved","Closed":"pill-closed"}.get(s,"pill-open")
    return f'<span class="pill {cls}">{s}</span>'

def risk_pill(r):
    cls = {"Breached":"pill-breached","CRITICAL BREACH RISK":"pill-risk","Normal":"pill-normal","Completed":"pill-done"}.get(r,"pill-normal")
    icon = {"Breached":"🔴","CRITICAL BREACH RISK":"⚠️","Normal":"✅","Completed":"✔️"}.get(r,"")
    short = {"CRITICAL BREACH RISK":"AT RISK"}.get(r, r)
    return f'<span class="pill {cls}">{icon} {short}</span>'

def rem_color(mins):
    if mins < 0:  return "#f78166"
    if mins < 60: return "#e3b341"
    return "#8b949e"

def show_critical_alerts(df):
    cdf = df[df["risk_status"].isin(["CRITICAL BREACH RISK","Breached"])]
    with st.sidebar:
        st.markdown('<div class="sb-section-label">⚡ Critical Alerts</div>', unsafe_allow_html=True)
        if cdf.empty:
            st.markdown('<div class="sb-ok">✅ No critical alerts</div>', unsafe_allow_html=True)
        else:
            for _, row in cdf.iterrows():
                reason = get_ai_risk_reason(
                    row["ticket_id"], row["comment"],
                    int(row["complexity_score"]), int(row["remaining_minutes"])
                )
                st.markdown(f"""
                <div class="sb-alert-item">
                    <div class="sb-alert-id">🔴 {row['ticket_id']}</div>
                    <div class="sb-alert-text">{reason}</div>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# INLINE-EDITABLE TICKET TABLE
# ══════════════════════════════════════════════════════════
def render_ticket_table(df, allow_edit=True):
    """Render full-width ticket table with inline status dropdowns."""
    cols = ["ticket_id","customer_name","comment","created_at","status",
            "priority","complexity_score","sla_hours","sla_deadline","remaining_minutes","risk_status"]

    if df.empty:
        st.info("No tickets to display.")
        return

    # ── header row ──
    header_html = """
    <div class="ticket-table-wrap">
      <div class="ticket-table-header">
        <div class="ticket-table-header-cell">ID</div>
        <div class="ticket-table-header-cell">Customer</div>
        <div class="ticket-table-header-cell">Comment</div>
        <div class="ticket-table-header-cell">Created</div>
        <div class="ticket-table-header-cell">Status</div>
        <div class="ticket-table-header-cell">Priority</div>
        <div class="ticket-table-header-cell">Score</div>
        <div class="ticket-table-header-cell">SLA h</div>
        <div class="ticket-table-header-cell">Deadline</div>
        <div class="ticket-table-header-cell">Mins Left</div>
        <div class="ticket-table-header-cell">Risk</div>
        <div class="ticket-table-header-cell">Update Status</div>
      </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # ── data rows: each row = 12 st.columns mirroring grid ──
    COL_RATIOS = [0.7, 1.2, 2.2, 1.4, 1.0, 0.8, 0.7, 0.7, 1.4, 0.8, 1.4, 1.3]

    for _, row in df.iterrows():
        risk = row["risk_status"]
        row_bg = ""
        if risk == "Breached":            row_bg = "background:#1a0f0f;"
        elif risk == "CRITICAL BREACH RISK": row_bg = "background:#150f1a;"
        elif risk == "Completed":         row_bg = "background:#0d1a10;"

        st.markdown(
            f'<div style="height:0;border-bottom:1px solid #21262d;{row_bg}margin:0;"></div>',
            unsafe_allow_html=True
        )

        cols_ui = st.columns(COL_RATIOS)
        with cols_ui[0]:
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:12px;'
                f'color:#58a6ff;font-weight:700;padding:6px 0;">{row["ticket_id"]}</div>',
                unsafe_allow_html=True)
        with cols_ui[1]:
            st.markdown(
                f'<div style="font-size:12px;color:#c9d1d9;padding:6px 0;'
                f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                f'{row["customer_name"]}</div>', unsafe_allow_html=True)
        with cols_ui[2]:
            st.markdown(
                f'<div style="font-size:11px;color:#8b949e;padding:6px 0;'
                f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" '
                f'title="{str(row["comment"]).replace(chr(34), chr(39))}">'
                f'{str(row["comment"])[:60]}{"…" if len(str(row["comment"]))>60 else ""}</div>',
                unsafe_allow_html=True)
        with cols_ui[3]:
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;'
                f'color:#484f58;padding:6px 0;">{str(row["created_at"])[:16]}</div>',
                unsafe_allow_html=True)
        with cols_ui[4]:
            st.markdown(
                f'<div style="padding:6px 0;">{status_pill(row["status"])}</div>',
                unsafe_allow_html=True)
        with cols_ui[5]:
            st.markdown(
                f'<div style="padding:6px 0;">{priority_pill(row["priority"])}</div>',
                unsafe_allow_html=True)
        with cols_ui[6]:
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:13px;'
                f'color:#e6edf3;font-weight:600;padding:6px 0;">{row["complexity_score"]}</div>',
                unsafe_allow_html=True)
        with cols_ui[7]:
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:12px;'
                f'color:#8b949e;padding:6px 0;">{row["sla_hours"]}</div>',
                unsafe_allow_html=True)
        with cols_ui[8]:
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;'
                f'color:#484f58;padding:6px 0;">{str(row["sla_deadline"])[:16]}</div>',
                unsafe_allow_html=True)
        with cols_ui[9]:
            mins = int(row["remaining_minutes"])
            clr  = rem_color(mins)
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:13px;'
                f'font-weight:700;color:{clr};padding:6px 0;">{mins}</div>',
                unsafe_allow_html=True)
        with cols_ui[10]:
            st.markdown(
                f'<div style="padding:6px 0;">{risk_pill(row["risk_status"])}</div>',
                unsafe_allow_html=True)
        with cols_ui[11]:
            if allow_edit and row["status"] not in ["Resolved","Closed"]:
                opts = get_allowed_status_options(row["status"])
                if opts:
                    sel = st.selectbox(
                        label="",
                        options=opts,
                        key=f"sel_{row['ticket_id']}",
                        label_visibility="collapsed"
                    )
                    if st.button("Apply", key=f"btn_{row['ticket_id']}", use_container_width=True):
                        _update_db(row["ticket_id"], sel)
                        st.session_state.status_updates[row["ticket_id"]] = sel
                        st.rerun()
            else:
                st.markdown('<div style="font-size:11px;color:#484f58;padding:6px 0;">—</div>',
                            unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    now_str = datetime.now(IST).strftime("%d %b %Y · %H:%M IST")
    st.markdown(f"""
    <div class="sb-brand">
        <div class="sb-brand-row">
            <div class="sb-brand-icon">🛡️</div>
            <div>
                <div class="sb-brand-name">SLA Predictor</div>
                <div class="sb-brand-tag">Breach Intelligence</div>
            </div>
        </div>
        <div class="sb-time">{now_str}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-nav-label">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "nav",
        ["🎫  Create Ticket", "📊  Dashboard", "📈  Analysis", "✅  Resolved & Closed"],
        label_visibility="collapsed"
    )


# ══════════════════════════════════════════════════════════
# PAGE — CREATE TICKET
# ══════════════════════════════════════════════════════════
if page == "🎫  Create Ticket":
    st.markdown("""
    <div class="page-hero">
        <h1>🎫 Create Support Ticket</h1>
        <p>AI classifies priority &amp; complexity score instantly on submission</p>
    </div>""", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["✏️  Manual Entry", "📂  Upload CSV"])

    with tab1:
        with st.form("ticket_form"):
            col_a, col_b = st.columns([1, 2])
            with col_a:
                customer_name = st.text_input("Customer Name", placeholder="e.g. Acme Corp")
            with col_b:
                comment = st.text_area("Issue Description", placeholder="Describe the problem in detail…", height=110)
            submit = st.form_submit_button("🚀 Analyze & Create Ticket", use_container_width=True)

        if submit:
            if not customer_name or not comment:
                st.error("Please fill in both fields.")
            else:
                with st.spinner("AI is analyzing the ticket…"):
                    ticket = create_ticket(customer_name, comment)
                pc = {"Critical":"#e3b341","High":"#f78166","Medium":"#58a6ff","Low":"#3fb950"}.get(ticket["priority"],"#8b949e")
                st.markdown(f"""
                <div class="created-card">
                    <div class="created-id">✅ Ticket {ticket['ticket_id']} created</div>
                    <div class="created-meta">
                        <div class="meta-item">
                            <div class="meta-lbl">Priority</div>
                            <div class="meta-val" style="color:{pc}">{ticket['priority']}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-lbl">Complexity</div>
                            <div class="meta-val">{ticket['complexity_score']}<span style="font-size:14px;color:#484f58"> /5</span></div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-lbl">SLA Window</div>
                            <div class="meta-val">{ticket['sla_hours']}<span style="font-size:14px;color:#484f58"> hrs</span></div>
                        </div>
                    </div>
                    <div class="meta-dl">⏱ Deadline: {ticket['sla_deadline']}</div>
                </div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="csv-info">📋 CSV must include columns: <strong>customer_name</strong>, <strong>comment</strong></div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload tickets.csv", type=["csv"])
        if uploaded_file:
            if st.button("⚡ Process CSV"):
                with st.spinner("Importing and classifying tickets…"):
                    upload_csv_to_dynamodb(uploaded_file)


# ══════════════════════════════════════════════════════════
# PAGE — DASHBOARD
# ══════════════════════════════════════════════════════════
elif page == "📊  Dashboard":
    st_autorefresh(interval=30000, key="dashboard_refresh")

    st.markdown("""
    <div class="page-hero">
        <h1>📊 Operational Dashboard</h1>
        <p>Live SLA breach intelligence · auto-refreshes every 30 s · update ticket status inline</p>
    </div>""", unsafe_allow_html=True)

    df = prepare_dashboard_data()

    if df.empty:
        st.info("No tickets yet. Go to **Create Ticket** to get started.")
    else:
        show_critical_alerts(df)
        active_df = df[~df["status"].isin(["Resolved","Closed"])]

        # KPI row
        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-card kpi-blue">
                <div class="kpi-label">Total Tickets</div>
                <div class="kpi-val">{len(df)}</div>
                <div class="kpi-bar"></div>
            </div>
            <div class="kpi-card kpi-green">
                <div class="kpi-label">Active</div>
                <div class="kpi-val">{len(active_df)}</div>
                <div class="kpi-bar"></div>
            </div>
            <div class="kpi-card kpi-amber">
                <div class="kpi-label">Critical Priority</div>
                <div class="kpi-val">{len(df[df['priority']=='Critical'])}</div>
                <div class="kpi-bar"></div>
            </div>
            <div class="kpi-card kpi-red">
                <div class="kpi-label">Breached</div>
                <div class="kpi-val">{len(df[df['risk_status']=='Breached'])}</div>
                <div class="kpi-bar"></div>
            </div>
            <div class="kpi-card kpi-purple">
                <div class="kpi-label">At Risk</div>
                <div class="kpi-val">{len(df[df['risk_status']=='CRITICAL BREACH RISK'])}</div>
                <div class="kpi-bar"></div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Sidebar filters
        with st.sidebar:
            st.markdown('<div class="sb-section-label">🔍 Filters</div>', unsafe_allow_html=True)
            priority_filter = st.multiselect("Priority", active_df["priority"].unique(),
                                             placeholder="All priorities", label_visibility="collapsed")
            risk_filter     = st.multiselect("Risk",     active_df["risk_status"].unique(),
                                             placeholder="All risk levels", label_visibility="collapsed")

        filtered_df = active_df.copy()
        if priority_filter: filtered_df = filtered_df[filtered_df["priority"].isin(priority_filter)]
        if risk_filter:     filtered_df = filtered_df[filtered_df["risk_status"].isin(risk_filter)]

        st.markdown('<div class="sec-head">📋 Active Tickets — click Apply to update status inline</div>', unsafe_allow_html=True)
        render_ticket_table(filtered_df, allow_edit=True)


# ══════════════════════════════════════════════════════════
# PAGE — ANALYSIS  (new page)
# ══════════════════════════════════════════════════════════
elif page == "📈  Analysis":
    st.markdown("""
    <div class="page-hero">
        <h1>📈 SLA Analysis</h1>
        <p>Deep-dive into breach patterns, priority distribution, complexity trends &amp; resolution performance</p>
    </div>""", unsafe_allow_html=True)

    df = prepare_dashboard_data()

    if df.empty:
        st.info("No data yet. Create tickets to see analysis.")
    else:
        df["complexity_score"] = pd.to_numeric(df["complexity_score"], errors="coerce")
        resolved_df = df[df["status"].isin(["Resolved","Closed"])]
        active_df   = df[~df["status"].isin(["Resolved","Closed"])]
        breach_rate = round(len(df[df["risk_status"]=="Breached"]) / len(df) * 100, 1) if len(df) else 0
        avg_complexity = round(df["complexity_score"].mean(), 2)
        avg_sla = round(df["sla_hours"].mean(), 1)
        resolution_rate = round(len(resolved_df) / len(df) * 100, 1) if len(df) else 0

        # ── Row 1: insight cards ──
        st.markdown(f"""
        <div class="analysis-grid" style="grid-template-columns:repeat(4,1fr);">
            <div class="insight-card">
                <div class="insight-label">Breach Rate</div>
                <div class="insight-value" style="color:#f78166">{breach_rate}%</div>
                <div class="insight-sub">{len(df[df['risk_status']=='Breached'])} of {len(df)} tickets</div>
            </div>
            <div class="insight-card">
                <div class="insight-label">Avg Complexity</div>
                <div class="insight-value" style="color:#e3b341">{avg_complexity}</div>
                <div class="insight-sub">out of 5.0 max</div>
            </div>
            <div class="insight-card">
                <div class="insight-label">Avg SLA Window</div>
                <div class="insight-value" style="color:#58a6ff">{avg_sla}h</div>
                <div class="insight-sub">across all priorities</div>
            </div>
            <div class="insight-card">
                <div class="insight-label">Resolution Rate</div>
                <div class="insight-value" style="color:#3fb950">{resolution_rate}%</div>
                <div class="insight-sub">{len(resolved_df)} tickets resolved</div>
            </div>
        </div>""", unsafe_allow_html=True)

        AXIS = dict(color="#8b949e", gridcolor="#21262d", zerolinecolor="#21262d")

        # ── Row 2: Priority donut + Risk bar ──
        c1, c2 = st.columns(2)
        with c1:
            prio_cnt = df["priority"].value_counts().reset_index()
            prio_cnt.columns = ["Priority", "Count"]
            fig1 = px.pie(
                prio_cnt, names="Priority", values="Count",
                title="Tickets by Priority",
                color_discrete_sequence=CHART_COLORS, hole=0.45
            )
            fig1.update_layout(**chart_layout())
            fig1.update_traces(
                textfont_size=11, textfont_color="#e6edf3",
                marker=dict(line=dict(color="#0d1117", width=2))
            )
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            risk_cnt = df["risk_status"].value_counts().reset_index()
            risk_cnt.columns = ["Risk Status", "Count"]
            fig2 = px.bar(
                risk_cnt, x="Risk Status", y="Count",
                title="Tickets by Risk Status",
                text="Count", color="Risk Status",
                color_discrete_sequence=CHART_COLORS
            )
            fig2.update_layout(
                **chart_layout(),
                xaxis={**AXIS}, yaxis={**AXIS},
                showlegend=False
            )
            fig2.update_traces(textfont_color="#e6edf3", marker_line_width=0)
            st.plotly_chart(fig2, use_container_width=True)

        # ── Row 3: Complexity histogram + Status donut ──
        c3, c4 = st.columns(2)
        with c3:
            fig3 = px.histogram(
                df, x="complexity_score", nbins=5,
                title="Complexity Score Distribution",
                color_discrete_sequence=["#58a6ff"]
            )
            fig3.update_layout(
                **chart_layout(),
                xaxis={**AXIS, "title": "Complexity Score"},
                yaxis={**AXIS, "title": "Count"},
                showlegend=False, bargap=0.12
            )
            fig3.update_traces(marker_line_width=0)
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            status_cnt = df["status"].value_counts().reset_index()
            status_cnt.columns = ["Status", "Count"]
            fig4 = px.pie(
                status_cnt, names="Status", values="Count",
                title="Ticket Status Breakdown",
                color_discrete_sequence=CHART_COLORS, hole=0.45
            )
            fig4.update_layout(**chart_layout())
            fig4.update_traces(
                textfont_size=11, textfont_color="#e6edf3",
                marker=dict(line=dict(color="#0d1117", width=2))
            )
            st.plotly_chart(fig4, use_container_width=True)

        # ── Row 4: SLA box + Complexity vs Remaining scatter ──
        c5, c6 = st.columns(2)
        with c5:
            fig5 = px.box(
                df, x="priority", y="sla_hours",
                title="SLA Hours by Priority",
                color="priority",
                color_discrete_sequence=CHART_COLORS
            )
            fig5.update_layout(
                **chart_layout(),
                xaxis={**AXIS}, yaxis={**AXIS},
                showlegend=False
            )
            fig5.update_traces(marker_color="#58a6ff", line_color="#8b949e")
            st.plotly_chart(fig5, use_container_width=True)

        with c6:
            fig6 = px.scatter(
                df, x="complexity_score", y="remaining_minutes",
                color="priority", title="Complexity vs Remaining Minutes",
                color_discrete_sequence=CHART_COLORS,
                hover_data=["ticket_id", "customer_name"]
            )
            fig6.update_layout(
    title="Priority vs Complexity",
    xaxis_title="Priority",
    yaxis_title="Complexity Score",
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)
            fig6.add_hline(
                y=0, line_dash="dash", line_color="#f78166", opacity=0.6,
                annotation_text="Breach line", annotation_font_color="#f78166",
                annotation_font_size=10
            )
            fig6.add_hline(
                y=60, line_dash="dot", line_color="#e3b341", opacity=0.6,
                annotation_text="60 min warning", annotation_font_color="#e3b341",
                annotation_font_size=10
            )
            st.plotly_chart(fig6, use_container_width=True)

        # ── Breach breakdown table ──
        st.markdown('<div class="sec-head">🔴 Breached & At-Risk Tickets</div>', unsafe_allow_html=True)
        breach_df = df[df["risk_status"].isin(["Breached","CRITICAL BREACH RISK"])].copy()
        if breach_df.empty:
            st.success("🎉 No breached or at-risk tickets right now.")
        else:
            render_ticket_table(breach_df, allow_edit=True)


# ══════════════════════════════════════════════════════════
# PAGE — RESOLVED & CLOSED
# ══════════════════════════════════════════════════════════
elif page == "✅  Resolved & Closed":
    st.markdown("""
    <div class="page-hero">
        <h1>✅ Resolved &amp; Closed Tickets</h1>
        <p>Historical record of all completed support tickets</p>
    </div>""", unsafe_allow_html=True)

    df = prepare_dashboard_data()

    if df.empty:
        st.info("No tickets available.")
    else:
        completed_df = df[df["status"].isin(["Resolved","Closed"])]
        if completed_df.empty:
            st.success("No resolved or closed tickets yet.")
        else:
            df["complexity_score"] = pd.to_numeric(df["complexity_score"], errors="coerce")
            avg_c = round(completed_df["complexity_score"].apply(pd.to_numeric, errors="coerce").mean(), 1)

            st.markdown(f"""
            <div class="kpi-row" style="grid-template-columns:repeat(3,1fr);max-width:600px;">
                <div class="kpi-card kpi-green">
                    <div class="kpi-label">Resolved / Closed</div>
                    <div class="kpi-val">{len(completed_df)}</div>
                    <div class="kpi-bar"></div>
                </div>
                <div class="kpi-card kpi-amber">
                    <div class="kpi-label">Avg Complexity</div>
                    <div class="kpi-val">{avg_c}</div>
                    <div class="kpi-bar"></div>
                </div>
                <div class="kpi-card kpi-blue">
                    <div class="kpi-label">Unique Customers</div>
                    <div class="kpi-val">{completed_df['customer_name'].nunique()}</div>
                    <div class="kpi-bar"></div>
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown('<div class="sec-head">📋 Completed Ticket Records</div>', unsafe_allow_html=True)
            render_ticket_table(completed_df, allow_edit=False)