from datetime import datetime, timedelta

SLA_HOURS = {
    "Critical": 2,
    "High": 4,
    "Medium": 8,
    "Low": 24
}


def get_sla_hours(priority):
    return SLA_HOURS.get(priority, 24)


def calculate_deadline(created_at, sla_hours):
    created_time = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
    deadline = created_time + timedelta(hours=int(sla_hours))
    return deadline.strftime("%Y-%m-%d %H:%M:%S")