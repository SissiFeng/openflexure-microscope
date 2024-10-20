import paho.mqtt.client as mqtt
import ssl
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.broker = os.getenv("HIVEMQ_BROKER")
        self.port = int(os.getenv("HIVEMQ_PORT", 8884))  # WebSocket port
        self.username = os.getenv("HIVEMQ_USERNAME")
        self.password = os.getenv("HIVEMQ_PASSWORD")
        self.client_id = f"openflexure-microscope-{os.urandom(4).hex()}"

        # 创建 MQTT 客户端
        self.client = mqtt.Client(client_id=self.client_id, transport="websockets")
        self.client.username_pw_set(self.username, self.password)
        self.client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)

        # 绑定回调函数
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            logger.info("Connecting to MQTT broker...")
        except Exception as e:
            logger.error(f"Connection error: {e}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected successfully to MQTT broker")
            client.subscribe("test/topic", qos=1)
        else:
            logger.error(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        logger.warning(f"Disconnected with return code {rc}")
        if rc != 0:
            self.reconnect()

    def on_message(self, client, userdata, msg):
        logger.info(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

    def reconnect(self):
        try:
            self.client.reconnect()
            logger.info("Reconnected successfully")
        except Exception as e:
            logger.error(f"Reconnection failed: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Disconnected from MQTT broker")

    def publish(self, topic, message):
        self.client.publish(topic, message, qos=1)
        logger.info(f"Published message to topic {topic}")

# 使用示例
if __name__ == "__main__":
    client = MQTTClient()
    client.connect()

    # 这里可以添加其他操作，比如发布消息
    # client.publish("test/topic", "Hello, HiveMQ!")

    # 保持程序运行
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Exiting...")
        client.disconnect()
