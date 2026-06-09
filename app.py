import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

from src.llm_service import analyze_ticket
from src.sla_engine import get_sla_hours, calculate_deadline
from src.dynamodb_service import (
    save_ticket_to_db,
    load_tickets_from_db,
    update_ticket_status_db
)

IST = pytz.timezone("Asia/Kolkata")

st.set_page_config(page_title="SLA Breach Predictor", layout="wide")


def load_tickets():
    items = load_tickets_from_db()

    if items:
        return pd.DataFrame(items)

    return pd.DataFrame(columns=[
        "ticket_id",
        "customer_name",
        "comment",
        "created_at",
        "status",
        "priority",
        "complexity_score",
        "sla_hours",
        "sla_deadline"
    ])


def save_ticket(ticket):
    save_ticket_to_db(ticket)


def update_ticket_status(ticket_id, new_status):
    update_ticket_status_db(ticket_id, new_status)


def get_next_ticket_id():
    df = load_tickets()
    return f"T{len(df) + 1:03d}"


def create_ticket(customer_name, comment):
    created_at = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

    priority, complexity_score = analyze_ticket(comment)
    sla_hours = get_sla_hours(priority)
    deadline = calculate_deadline(created_at, sla_hours)

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
    return ticket


def calculate_remaining_minutes(deadline):
    deadline_time = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
    deadline_time = IST.localize(deadline_time)
    current_time = datetime.now(IST)

    return int((deadline_time - current_time).total_seconds() / 60)


def get_risk_status(row):
    if row["status"] in ["Resolved", "Closed"]:
        return "Completed"

    if row["remaining_minutes"] < 0:
        return "Breached"

    if row["remaining_minutes"] < 60 or int(row["complexity_score"]) > 4:
        return "CRITICAL BREACH RISK"

    return "Normal"


def prepare_dashboard_data():
    df = load_tickets()

    if not df.empty:
        df["remaining_minutes"] = df["sla_deadline"].apply(calculate_remaining_minutes)
        df["risk_status"] = df.apply(get_risk_status, axis=1)

    return df


def color_risk_status(row):
    if row["risk_status"] in ["Breached", "CRITICAL BREACH RISK"]:
        return ["background-color: red; color: white"] * len(row)

    if row["risk_status"] == "Completed":
        return ["background-color: lightgreen"] * len(row)

    return [""] * len(row)


def get_allowed_status_options(current_status):
    if current_status == "Open":
        return ["In Progress", "Resolved", "Closed"]

    if current_status == "In Progress":
        return ["Resolved", "Closed"]

    return []


def show_critical_alerts(df):
    critical_df = df[
        (df["risk_status"] == "CRITICAL BREACH RISK") |
        (df["risk_status"] == "Breached")
    ]

    st.sidebar.divider()
    st.sidebar.subheader("Critical Alerts")

    if critical_df.empty:
        st.sidebar.success("No critical alerts")
    else:
        for _, row in critical_df.iterrows():
            if row["remaining_minutes"] < 0:
                reason = "SLA already breached"
            elif row["remaining_minutes"] < 30:
                reason = "Less than 30 minutes to complete"
            elif int(row["complexity_score"]) > 4:
                reason = "High complexity issue may affect many users"
            else:
                reason = "Close to SLA breach"

            st.sidebar.error(f"{row['ticket_id']} - {reason}")


def upload_csv_to_dynamodb(uploaded_file):
    csv_df = pd.read_csv(uploaded_file)

    required_columns = ["customer_name", "comment"]

    for col in required_columns:
        if col not in csv_df.columns:
            st.error(f"CSV must contain '{col}' column.")
            return

    created_count = 0

    for _, row in csv_df.iterrows():
        customer_name = str(row["customer_name"]).strip()
        comment = str(row["comment"]).strip()

        if customer_name and comment and customer_name != "nan" and comment != "nan":
            create_ticket(customer_name, comment)
            created_count += 1

    st.success(f"{created_count} tickets uploaded successfully.")


st.sidebar.title("SLA Predictor")
page = st.sidebar.radio("Navigation", ["Create Ticket", "Dashboard"])


if page == "Create Ticket":
    st.title("SLA Breach Predictor")
    st.subheader("Support Engineer - Create Ticket")

    tab1, tab2 = st.tabs(["Manual Ticket Entry", "Upload CSV"])

    with tab1:
        with st.form("ticket_form"):
            customer_name = st.text_input("Customer Name")
            comment = st.text_area("Comment")
            submit = st.form_submit_button("Create Ticket")

        if submit:
            if not customer_name or not comment:
                st.error("Please fill all fields")
            else:
                with st.spinner("AI is analyzing ticket comment..."):
                    ticket = create_ticket(customer_name, comment)

                st.success(f"Ticket {ticket['ticket_id']} created successfully.")

                col1, col2 = st.columns(2)
                col1.metric("Priority", ticket["priority"])
                col2.metric("Complexity Score", ticket["complexity_score"])

                st.caption(f"SLA Deadline: {ticket['sla_deadline']}")

    with tab2:
        st.info("CSV must contain columns: customer_name, comment")

        uploaded_file = st.file_uploader(
            "Upload tickets.csv",
            type=["csv"]
        )

        if uploaded_file is not None:
            if st.button("Process CSV"):
                with st.spinner("Reading CSV and creating tickets..."):
                    upload_csv_to_dynamodb(uploaded_file)


elif page == "Dashboard":
    st.title("Operational SLA Dashboard")

    st_autorefresh(interval=30000, key="dashboard_refresh")

    df = prepare_dashboard_data()

    if df.empty:
        st.info("No tickets created yet.")
    else:
        show_critical_alerts(df)

        active_table_df = df[~df["status"].isin(["Resolved", "Closed"])]

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Total Tickets", len(df))
        col2.metric("Active Tickets", len(active_table_df))
        col3.metric("Critical Tickets", len(df[df["priority"] == "Critical"]))
        col4.metric("Breached", len(df[df["risk_status"] == "Breached"]))
        col5.metric(
            "Critical Risk",
            len(df[df["risk_status"] == "CRITICAL BREACH RISK"])
        )

        st.divider()

        priority_filter = st.sidebar.multiselect(
            "Filter by Priority",
            active_table_df["priority"].unique()
        )

        risk_filter = st.sidebar.multiselect(
            "Filter by Risk Status",
            active_table_df["risk_status"].unique()
        )

        filtered_df = active_table_df.copy()

        if priority_filter:
            filtered_df = filtered_df[filtered_df["priority"].isin(priority_filter)]

        if risk_filter:
            filtered_df = filtered_df[filtered_df["risk_status"].isin(risk_filter)]

        st.subheader("Active Ticket Records")

        display_columns = [
            "ticket_id",
            "customer_name",
            "comment",
            "created_at",
            "status",
            "priority",
            "complexity_score",
            "sla_hours",
            "sla_deadline",
            "remaining_minutes",
            "risk_status"
        ]

        styled_df = filtered_df[display_columns].style.apply(
            color_risk_status,
            axis=1
        )

        st.dataframe(styled_df, use_container_width=True)

        st.divider()

        st.subheader("Update Ticket Status")

        active_df = df[~df["status"].isin(["Resolved", "Closed"])]

        if active_df.empty:
            st.success("No active tickets available for status update.")
        else:
            selected_ticket = st.selectbox(
                "Select Active Ticket ID",
                active_df["ticket_id"].tolist()
            )

            current_status = active_df.loc[
                active_df["ticket_id"] == selected_ticket,
                "status"
            ].iloc[0]

            st.info(f"Current Status: {current_status}")

            allowed_statuses = get_allowed_status_options(current_status)

            new_status = st.selectbox(
                "Select New Status",
                allowed_statuses
            )

            if st.button("Update Status"):
                update_ticket_status(selected_ticket, new_status)
                st.success(f"{selected_ticket} updated to {new_status}")
                st.rerun()

        st.divider()

        st.subheader("Analytics Charts")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            priority_counts = df["priority"].value_counts().reset_index()
            priority_counts.columns = ["Priority", "Count"]

            fig_priority = px.pie(
                priority_counts,
                names="Priority",
                values="Count",
                title="Tickets by Priority"
            )

            st.plotly_chart(fig_priority, use_container_width=True)

        with chart_col2:
            risk_counts = df["risk_status"].value_counts().reset_index()
            risk_counts.columns = ["Risk Status", "Count"]

            fig_risk = px.bar(
                risk_counts,
                x="Risk Status",
                y="Count",
                title="Tickets by Risk Status",
                text="Count"
            )

            st.plotly_chart(fig_risk, use_container_width=True)