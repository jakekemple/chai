from awscrt import mqtt
from awsiot import mqtt_connection_builder
import time

# AWS IoT Core endpoint and credentials
endpoint = "xxx"
cert_filepath = "Macbook22.cert.pem"
pri_key_filepath = "Macbook22.private.key"
ca_filepath = "root-CA.crt"
client_id = "macbook22-listener"

# Topic to subscribe to
feedback_topic = "chai/feedback"


def on_feedback_received(topic, payload, **kwargs):
    print("Feedback received from {}: {}".format(topic, payload.decode("utf-8")))


def main():
    # Initialize MQTT connection
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath=cert_filepath,
        pri_key_filepath=pri_key_filepath,
        ca_filepath=ca_filepath,
        client_id=client_id,
        clean_session=False,
        keep_alive_secs=30,
    )

    # Establish connection
    print("Connecting to {} with client ID {}".format(endpoint, client_id))
    connect_future = mqtt_connection.connect()
    connect_future.result()
    print("Connected!")

    # Subscribe to the feedback topic
    print("Subscribing to {}".format(feedback_topic))
    subscribe_future, _ = mqtt_connection.subscribe(
        topic=feedback_topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_feedback_received
    )
    subscribe_future.result()
    print("Subscribed to feedback topic")

    # Keep the script running to continue receiving messages
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")


if __name__ == "__main__":
    main()
