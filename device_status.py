import gradio as gr
from mqtt_client import MQTTClient
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

# HiveMQ Cloud settings
broker = os.getenv("HIVEMQ_BROKER", "f84673212a5c46da8fa64f37d38b3630.s1.eu.hivemq.cloud")
port = int(os.getenv("HIVEMQ_PORT", 8883))
username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")

# Create MQTT client
mqtt_client = MQTTClient(broker, port, f"device-status-{secrets.token_hex(4)}", username, password)

device_status = {}

def on_status_message(client, userdata, message):
    device_id = message.topic.split('/')[-2]
    status = message.payload.decode()
    device_status[device_id] = status

mqtt_client.client.message_callback_add("devices/+/status", on_status_message)

try:
    mqtt_client.connect()
    mqtt_client.subscribe("devices/+/status")
    print("Connected to HiveMQ Cloud")
except Exception as e:
    print(f"Connection failed: {e}")

def get_device_status():
    status_text = "Device Status:\n"
    for device, status in device_status.items():
        status_text += f"{device}: {status}\n"
    return status_text if device_status else "No devices connected"

def show():
    with gr.Blocks() as demo:
        gr.Markdown("# Device Status")
        status_output = gr.Textbox(label="Current Status")
        refresh_button = gr.Button("Refresh Status")
        
        refresh_button.click(get_device_status, inputs=[], outputs=[status_output])
    
    return demo

if __name__ == "__main__":
    show().launch()
