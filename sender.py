from pydub import AudioSegment
from io import BytesIO
import pyaudio
import time
import paho.mqtt.client as mqtt
import requests
from functools import partial
import json
import base64
import ssl

# Declare global variables
global frames, start_time, meeting_id


# Function to get the next meeting ID
def get_next_meeting_id():
    # Call our chaiGetMeetingId Lambda function via API Gateway
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
KEEPALIVE = 30

# Files for the device certificate and private key
cert_filepath = "Macbook22.cert.pem"
pri_key_filepath = "Macbook22.private.key"
ca_filepath = "root-CA.crt"

# Current device id
client_id = "macbook22-listener"


# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


def on_publish(client, userdata, mid):
    print(f"Message {mid} published.")


def on_disconnect(client, userdata, rc):
    print("Disconnected with result code " + str(rc))


# MQTT client setup
client = mqtt.Client(client_id=client_id)
client.tls_set(
    ca_certs=ca_filepath,
    certfile=cert_filepath,
    keyfile=pri_key_filepath,
    tls_version=ssl.PROTOCOL_TLSv1_2,
)
client.on_connect = on_connect
client.on_publish = on_publish
client.on_disconnect = on_disconnect


# Connect to MQTT Broker
client.connect(MQTT_BROKER, MQTT_PORT, KEEPALIVE)
client.loop_start()


# Function to handle the recording in callback mode
def callback(interval, audio, in_data, frame_count, time_info, status):
    global frames, start_time, meeting_id

    frames.append(in_data)
    if time.time() - start_time >= interval:
        try:
            # Combine frames into a single audio segment
            combined = AudioSegment.empty()
            for frame in frames:
                segment = AudioSegment(
                    frame,
                    sample_width=audio.get_sample_size(pyaudio.paInt16),
                    frame_rate=44100,
                    channels=1,
                )
                combined += segment

            # Export combined audio to MP3
            buffer = BytesIO()
            combined.export(buffer, format="mp3")

            # Encode to Base64
            buffer.seek(0)
            encoded_audio_data = base64.b64encode(buffer.read()).decode("utf-8")

            payload = json.dumps(
                {"meeting_id": meeting_id, "audio_data": encoded_audio_data}
            )
            if len(payload) < 128000:  # Check payload size (128 KB)
                client.publish(MQTT_TOPIC, payload, qos=1)
                print("Audio chunk sent. Chunk size is {} kbs".format(len(payload)))
            else:
                print("Payload size exceeds limit.")
            frames.clear()
            start_time = time.time()

        except Exception as e:
            print(f"Error publishing message: {e}")

    return (None, pyaudio.paContinue)


# Function to start recording
def record_audio(interval, format, channels, rate, chunk):
    global frames, start_time, meeting_id
    frames = []
    start_time = time.time()
    meeting_id = get_next_meeting_id()
    print("meeting id: ", meeting_id)

    audio = pyaudio.PyAudio()

    # Create a partial function of the callback, filling in the interval and audio
    callback_with_interval = partial(callback, interval, audio)

    # Open stream using callback mode
    stream = audio.open(
        format=format,
        channels=channels,
        rate=rate,
        input=True,
        frames_per_buffer=chunk,
        stream_callback=callback_with_interval,
    )

    stream.start_stream()
    print("Recording started.")

    try:
        while stream.is_active():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Recording stopped. Sending remaining audio...")
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
record_audio(10, pyaudio.paInt16, 1, 44100, 1024)
