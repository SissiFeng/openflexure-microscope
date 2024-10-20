import gradio as gr
import json
import logging
import secrets
from mqtt_client import MQTTClient
from os import environ
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 MQTT 客户端
mqtt_client = MQTTClient()

def get_device_status():
    # 这里应该实现获取设备状态的逻辑
    # 现在我们只返回一个模拟的状态
    return json.dumps({
        "microscope1": "online",
        "microscope2": "offline",
        "deltastagetransmission": "online",
        "deltastagereflection": "maintenance"
    }, indent=2)

def show():
    with gr.Blocks() as demo:
        gr.Markdown("# Device Status")
        
        status_output = gr.JSON(label="Current Status")
        refresh_button = gr.Button("Refresh Status")
        
        refresh_button.click(get_device_status, inputs=[], outputs=[status_output])
        
    return demo

if __name__ == "__main__":
    show().launch()
