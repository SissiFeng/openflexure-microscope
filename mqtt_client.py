import paho.mqtt.client as mqtt
import logging
import time
import ssl
import json
import queue

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self, broker, port, client_id, username, password):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.username_pw_set(username, password)
        self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
        self.message_queue = queue.Queue()

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
            client.subscribe("test/topic", qos=1)
        else:
            logger.error(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc, properties=None):
        if rc != 0:
            logger.warning("Unexpected disconnection. Attempting to reconnect...")
            self.reconnect()

    def on_message(self, client, userdata, msg):
        self.message_queue.put(json.loads(msg.payload))

    def reconnect(self):
        while True:
            try:
                self.client.reconnect()
                logger.info("Reconnected successfully")
                break
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")
                time.sleep(5)

    def publish(self, topic, message, qos=2):
        result = self.client.publish(topic, json.dumps(message), qos=qos)
        result.wait_for_publish()
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Message published successfully: {message}")
        else:
            logger.error(f"Failed to publish message: {result.rc}")

    def subscribe(self, topic, qos=1):
        self.client.subscribe(topic, qos=qos)

    def get_message(self, timeout=None):
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
        logger.info("Disconnected from MQTT broker")
