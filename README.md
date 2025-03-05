# Chai: Real-Time AI Meeting Assistant

## Overview

Chai, The Real-Time AI Meeting Assistant, is a cloud-based application designed to enhance meeting experiences by providing automated, concise text feedback based on live audio input. Leveraging AWS IoT, AWS Lambda, and OpenAI’s GPT-3.5 and Whisper APIs, this project transcribes spoken audio in real-time and generates actionable insights in the form of bulleted feedback points. It aims to assist meeting attendees by offering technical information or relevant facts derived from their conversations, stored and managed via DynamoDB for persistent history tracking.

### Key Features
- **Real-Time Audio Transcription:** Captures audio from a local device, streams it via MQTT, and transcribes it using OpenAI’s Whisper API.
- **AI-Generated Feedback:** Processes transcriptions with GPT-3.5 to produce concise, non-repetitive feedback points based on conversation content.
- **Cloud Integration:** Utilizes AWS services (IoT Core, Lambda, S3, DynamoDB) for scalable streaming, processing, and storage.
- **Persistent Storage:** Logs conversation history and feedback in DynamoDB, tied to unique meeting IDs.
- **Feedback Delivery:** Publishes feedback back to the device via MQTT for real-time display.

### Project Structure
- **`lambda_handler.py`:** AWS Lambda function that processes audio, generates feedback, and updates DynamoDB.
- **`get_meeting_id.py`:** Lambda function to assign new meeting IDs by querying DynamoDB.
- **`feedback_listener.py`:** Local Python script to subscribe to feedback via AWS IoT MQTT and display it.
- **`record_audio.py`:** Local script to capture, encode, and stream audio to AWS IoT MQTT.

## Setup Instructions

### Prerequisites
- **AWS Account:** With access to IoT Core, Lambda, S3, DynamoDB, and API Gateway.
- **OpenAI API Key:** Obtain from [OpenAI](https://platform.openai.com/api-keys).
- **Python 3.8+:** Installed locally for running scripts.
- **AWS IoT Certificates:** Generate a device certificate, private key, and root CA from AWS IoT Core.
- **Hardware:** A microphone-enabled device (e.g., laptop) for audio input.

### Dependencies
Install required Python packages:
```bash
pip install boto3 openai pyaudio pydub paho-mqtt awscrt awsiot requests
