import pyaudio
import time
import paho.mqtt.client as mqtt
import requests


# Function to get the next meeting ID
def get_next_meeting_id():
    # Call the Lambda function via API Gateway or a similar trigger
    # Replace with the URL of your API Gateway
    response = requests.get(
        "xxxx"
    )
    if response.status_code == 200:
        return response.json()
    else:
        return None


# MQTT configuration
MQTT_BROKER = "xxx"
MQTT_PORT = 8883
MQTT_TOPIC = "chai/audio"

# Files for the device certificate and private key
cert_filepath = "Macbook22.cert.pem"
pri_key_filepath = "Macbook22.private.key"
ca_filepath = "root-CA.crt"

# Current device id
client_id = "macbook22-listener"

# MQTT client setup
client = mqtt.Client(client_id=client_id)
client.tls_set(ca_certs=ca_filepath, certfile=cert_filepath, keyfile=pri_key_filepath)
client.connect(MQTT_BROKER, MQTT_PORT, 60)


def record_audio(
    interval=10, format=pyaudio.paInt16, channels=1, rate=44100, chunk=1024
):
    audio = pyaudio.PyAudio()

    # Open stream
    stream = audio.open(
        format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk
    )

    print("Recording...")

    # Get the next meeting ID
    meeting_id = get_next_meeting_id()

    frames = []
    start_time = time.time()

    try:
        while True:
            data = stream.read(chunk)
            frames.append(data)

            # Check if interval has passed
            if time.time() - start_time >= interval:
                # Prepare the payload with meeting ID and audio data
                payload = {"meeting_id": meeting_id, "audio_data": frames}

                # Send the audio data with meeting ID
                client.publish(MQTT_TOPIC, payload)
                frames = []
                start_time = time.time()

    except KeyboardInterrupt:
        print("Recording stopped. Sending remaining audio...")

        # Send any remaining audio data
        payload = {"meeting_id": meeting_id, "audio_data": frames}
        client.publish(MQTT_TOPIC, payload)

    finally:
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        audio.terminate()
        # Disconnect MQTT client
        client.disconnect()
        print("Done recording.")


# Run the recorder
record_audio()
