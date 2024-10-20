import gradio as gr
import logging
import asyncio
import tenacity
from mqtt_client import MQTTClient
from key_request import generate_access_key
from device_status import get_device_status, show as show_device_status
from documentation import show as show_documentation
import download
import gui_control
import livestream
from access_control import check_access, generate_temp_key
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create MQTT client
mqtt_client = MQTTClient()
try:
    mqtt_client.connect()
except Exception as e:
    logger.error(f"Connection failed: {e}")

def about():
    return "This is a request site for credentials to use remote access to Openflexure Microscopes in the AC lab. You can either control the microscopes over python or the GUI with the help of a temporary key. You can view the live camera feed on a livestream. One person can use a microscope at once. Currently only Microscope2 is functional, but they will all be functional in the future"

@tenacity.retry(stop=tenacity.stop_after_attempt(3), wait=tenacity.wait_fixed(2))
def send_command_with_retry(command):
    mqtt_client.publish("command/topic", command)

async def send_command_with_timeout(command, timeout=10):
    try:
        return await asyncio.wait_for(send_command_with_retry(command), timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Command timed out after {timeout} seconds")
        return None
    
# Use access control in your application logic
def some_protected_function(key, device_id):
    if check_access(key, device_id):
        # Perform the protected action
        pass
    else:
        return "Access denied"

with gr.Blocks() as demo:
    gr.Markdown("# AC Microscope")
    
    with gr.Tab("About"):
        gr.Markdown(about())
    
    with gr.Tab("Request Key"):
        gr.Interface(
            fn=generate_access_key,
            inputs=gr.Textbox(label="Enter any text"),
            outputs="text",
            description="Generate a temporary access key"
        )
    
    with gr.Tab("Device Status"):
        show_device_status()

    with gr.Tab("Livestream"):
        livestream.show()
    
    with gr.Tab("Download"):
        download.show()
    
    with gr.Tab("GUI Control"):
        gui_control.show()
    
    with gr.Tab("Python Documentation"):
        show_documentation()
    
    with gr.Tab("Device Status"):
        status_output = gr.Textbox(label="Current Status")
        refresh_button = gr.Button("Refresh Status")
        refresh_button.click(get_device_status, inputs=[], outputs=[status_output])

if __name__ == "__main__":
    demo.launch()
