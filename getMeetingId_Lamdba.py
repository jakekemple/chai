import boto3

# Initialize DynamoDB client
dynamodb = boto3.client("dynamodb")
table_name = "ConversationHistory"


def lambda_handler(event, context):
    # Scan the DynamoDB table to find the highest meeting_id
    response = dynamodb.scan(
        TableName=table_name,
        ProjectionExpression="meeting_id",
    )

    max_meeting_id = 0

    # Iterate through the items to find the highest meeting ID
    if "Items" in response:
        for item in response["Items"]:
            meeting_id = int(item["meeting_id"]["N"])
            if meeting_id > max_meeting_id:
                max_meeting_id = meeting_id

    # Increment to get the new meeting ID
    new_meeting_id = max_meeting_id + 1

    # Return the new meeting ID
    return {"statusCode": 200, "body": new_meeting_id}
