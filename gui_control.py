import gradio as gr
from os import environ
from microscope_demo_client import MicroscopeDemo
import asyncio
import os
from mqtt_client import MQTTClient
from dotenv import load_dotenv
import secrets

load_dotenv()

# HiveMQ Cloud settings
broker = os.getenv("HIVEMQ_BROKER")
port = int(os.getenv("HIVEMQ_PORT", 8883))
username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")

# Create MQTT client
mqtt_client = MQTTClient(broker, port, f"gui-control-{secrets.token_hex(4)}", username, password)

try:
    mqtt_client.connect()
    print("Connected to HiveMQ Cloud")
except Exception as e:
    print(f"Connection failed: {e}")

async def get_pos(microscope_selection, access_key):
    async with MicroscopeDemo(
        HIVEMQ_BROKER,
        HIVEMQ_PORT,
        f"{microscope_selection}clientuser",
        access_key,
        microscope_selection
    ) as microscope:
        pos = await microscope.get_pos()
        return f"x: {pos['x']}, y: {pos['y']}, z: {pos['z']}"

async def take_image(microscope_selection, access_key):
    async with MicroscopeDemo(
        HIVEMQ_BROKER,
        HIVEMQ_PORT,
        f"{microscope_selection}clientuser",
        access_key,
        microscope_selection
    ) as microscope:
        image = await microscope.take_image()
        return image

async def focus(microscope_selection, access_key, focus_amount):
    async with MicroscopeDemo(
        HIVEMQ_BROKER,
        HIVEMQ_PORT,
        f"{microscope_selection}clientuser",
        access_key,
        microscope_selection
    ) as microscope:
        await microscope.focus(focus_amount)
        return "Autofocus complete"

async def move(microscope_selection, access_key, x_move, y_move):
    async with MicroscopeDemo(
        HIVEMQ_BROKER,
        HIVEMQ_PORT,
        f"{microscope_selection}clientuser",
        access_key,
        microscope_selection
    ) as microscope:
        await microscope.move(x_move, y_move)
        return "Move complete"

def send_command(command):
    mqtt_client.publish("microscope/command", command)
    return f"Command sent: {command}"

def show():
    MICROSCOPES = ["microscope", "microscope2", "deltastagetransmission", "deltastagereflection"]
    with gr.Blocks() as demo:
        gr.Markdown("# GUI Control")
        
        microscope_selection = gr.Dropdown(choices=MICROSCOPES, label="Choose a microscope:", value="microscope2")
        access_key = gr.Textbox(label="Enter your access key here:", type="password")
        
        with gr.Tab("Position"):
            get_pos_button = gr.Button("Get position")
            pos_output = gr.Textbox(label="Current Position")
            get_pos_button.click(fn=get_pos, inputs=[microscope_selection, access_key], outputs=pos_output)
        
        with gr.Tab("Image"):
            take_image_button = gr.Button("Take image")
            image_output = gr.Image(label="Microscope Image")
            take_image_button.click(fn=take_image, inputs=[microscope_selection, access_key], outputs=image_output)
        
        with gr.Tab("Focus"):
            focus_amount = gr.Slider(minimum=1, maximum=5000, step=100, value=1000, label="Autofocus amount")
            focus_button = gr.Button("Focus")
            focus_output = gr.Textbox(label="Focus Status")
            focus_button.click(fn=focus, inputs=[microscope_selection, access_key, focus_amount], outputs=focus_output)
        
        with gr.Tab("Move"):
            x_move = gr.Slider(minimum=-20000, maximum=20000, step=250, value=0, label="X")
            y_move = gr.Slider(minimum=-20000, maximum=20000, step=250, value=0, label="Y")
            move_button = gr.Button("Move")
            move_output = gr.Textbox(label="Move Status")
            move_button.click(fn=move, inputs=[microscope_selection, access_key, x_move, y_move], outputs=move_output)

        command_input = gr.Textbox(label="Enter command")
        send_button = gr.Button("Send Command")
        output = gr.Textbox(label="Result")
        
        send_button.click(send_command, inputs=[command_input], outputs=[output])
    
    return demo

if __name__ == "__main__":
    show().launch()
