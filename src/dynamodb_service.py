import os
import boto3
import streamlit as st
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv(override=True)


def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)


def get_table():
    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=get_secret("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=get_secret("AWS_SECRET_ACCESS_KEY"),
        region_name=get_secret("AWS_REGION")
    )

    return dynamodb.Table(get_secret("DYNAMODB_TABLE_NAME"))


def save_ticket_to_db(ticket):
    table = get_table()

    item = ticket.copy()
    item["complexity_score"] = Decimal(str(item["complexity_score"]))
    item["sla_hours"] = Decimal(str(item["sla_hours"]))

    table.put_item(Item=item)


def load_tickets_from_db():
    table = get_table()

    items = []
    response = table.scan()
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = table.scan(
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        items.extend(response.get("Items", []))

    for item in items:
        item["complexity_score"] = int(item["complexity_score"])
        item["sla_hours"] = int(item["sla_hours"])

    return sorted(items, key=lambda x: x["ticket_id"])


def update_ticket_status_db(ticket_id, new_status):
    table = get_table()

    table.update_item(
        Key={"ticket_id": ticket_id},
        UpdateExpression="SET #status = :status",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={":status": new_status}
    )