import boto3
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
table = dynamodb.Table("sla_tickets")

response = table.scan()

for item in response["Items"]:
    table.delete_item(
        Key={
            "ticket_id": item["ticket_id"]
        }
    )

print("All tickets deleted")