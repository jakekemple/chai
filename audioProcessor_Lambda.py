import boto3
import openai
import json
from datetime import datetime

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")
iot_client = boto3.client("iot-data")
table = dynamodb.Table("ConversationHistory")

# OpenAI API setup
openai.api_key = "xxxx"

# AWS IoT setup
iot_topic = "chai/feedback"  # The topic to publish responses to


def lambda_handler(event, context):
    meeting_id = event["meeting_id"]

    # Retrieve conversation history and existing feedback
    conversation_history, existing_feedback = get_conversation_history_and_feedback(
        meeting_id
    )
    updated_conversation = conversation_history + "\n" + convert_to_text(event["data"])

    # Calculate char_count and adjust updated_conversation if needed
    char_count = len(updated_conversation) + len(existing_feedback) + 450
    if char_count > 4000:
        slice_amount = char_count - 4000
        adjusted_conversation = updated_conversation[slice_amount:]
    else:
        adjusted_conversation = updated_conversation

    # Generate prompt for GPT-4
    chai_prompt = create_prompt(adjusted_conversation, existing_feedback)

    # Process updated conversation with GPT-4
    gpt_response = openai.Completion.create(
        model="text-davinci-004",
        prompt=chai_prompt,
        max_tokens=150,
    )
    processed_text = gpt_response.choices[0].text.strip()

    # Append new feedback to existing feedback
    updated_feedback = existing_feedback + "\n " + processed_text

    # Update DynamoDB with the new conversation history and feedback
    update_conversation_history_and_feedback(
        meeting_id, updated_conversation, updated_feedback
    )

    # Send processed text and meeting id back to device
    response_message = {"meeting_id": meeting_id, "text": processed_text}
    iot_client.publish(topic=iot_topic, qos=1, payload=json.dumps(response_message))

    return {
        "statusCode": 200,
        "body": "Processed and sent response at {}".format(datetime.now().isoformat()),
    }


def get_conversation_history_and_feedback(meeting_id):
    try:
        response = table.get_item(Key={"meeting_id": str(meeting_id)})
        if "Item" in response:
            return response["Item"].get("conversation_history", ""), response[
                "Item"
            ].get("feedback", "")
        else:
            return "", ""
    except Exception as e:
        print(e)
        return "", ""


def update_conversation_history_and_feedback(meeting_id, conversation, feedback):
    try:
        table.put_item(
            Item={
                "meeting_id": str(meeting_id),
                "conversation_history": conversation,
                "feedback": feedback,
                "last_updated": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        print(e)


def create_prompt(conversation_history, existing_feedback):
    return (
        "You are a meeting assistant who responds with helpful, supplementing comments "
        "or information based on a conversation between meeting attendees. "
        "Do not provide repeat feedback (anything too similar to the existing feedback "
        "list below) and do not under any circumstances provide any other information "
        "or text other than the helpful feedback in bullet points. Here is the latest "
        "conversation text:\n\n"
        + conversation_history
        + "\n\nAnd here is the existing feedback list:\n\n"
        + existing_feedback
    )


def convert_to_text(audio):
    # Placeholder function for converting audio to text using Whisper API
    return "Transcribed text from audio"
