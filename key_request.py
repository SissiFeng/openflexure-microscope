import gradio as gr
import random
import time
from os import environ
import requests
from pymongo.mongo_client import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGODB_URI = environ["MONGODB_URI"]
HIVEMQ_BASE_URL = environ["HIVEMQ_BASE_URL"]
HIVEMQ_API_TOKEN = environ["HIVEMQ_API_TOKEN"]

database_name = "openflexure-microscope"
collection_name = "Cluster0"
microscopes = ["microscope", "microscope2", "deltastagetransmission", "deltastagereflection"]
access_time = 180  # 3 minutes

client = MongoClient(MONGODB_URI)
db = client[database_name]
collection = db[collection_name]

def check_variable(variable_name):
    try:
        document = collection.find_one({"variable_name": variable_name})
        return document.get("value") if document else None
    except Exception as e:
        logger.error(f"Error checking variable: {e}")
        return None

def update_variable(variable_name, new_value):
    try:
        collection.update_one(
            {"variable_name": variable_name},
            {"$set": {"value": new_value}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error updating variable: {e}")

def create_user(username, password):
    api_url = f"{HIVEMQ_BASE_URL}/mqtt/credentials"
    headers = {
        "Authorization": f"Bearer {HIVEMQ_API_TOKEN}",
        "Content-Type": "application/json",
    }
    new_user = {"credentials": {"username": username, "password": password}}
    try:
        response = requests.post(api_url, json=new_user, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error creating user: {e}")

def delete_user(username):
    headers = {
        "Authorization": f"Bearer {HIVEMQ_API_TOKEN}",
        "Content-Type": "application/json",
    }
    api_url = f"{HIVEMQ_BASE_URL}/mqtt/credentials/username/{username}"
    try:
        response = requests.delete(api_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error deleting user: {e}")

def role_user(username, role):
    headers = {
        "Authorization": f"Bearer {HIVEMQ_API_TOKEN}",
        "Content-Type": "application/json",
    }
    api_url = f"{HIVEMQ_BASE_URL}/user/{username}/roles/{role}/attach"
    try:
        response = requests.put(api_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error assigning role to user: {e}")

def generate_access_key(microscope):
    current_time = int(time.time())
    last_access_time = check_variable(microscope)

def show():
    with gr.Blocks() as demo:
        microscope_dropdown = gr.Dropdown(choices=MICROSCOPES, label="Choose a microscope:", value="microscope2")
        output = gr.Textbox(label="Access Key or Wait Time")
        generate_button = gr.Button("Request temporary access")
        generate_button.click(fn=generate_access_key, inputs=[microscope_dropdown], outputs=[output])
    return demo
    
    if last_access_time is None or current_time >= last_access_time + access_time:
        access_key = f"Microscope{random.randint(10000000, 99999999)}"
        username = f"{microscope}clientuser"
        
        delete_user(username)
        create_user(username, access_key)
        
        role_mapping = {
            "microscope2": "3",
            "microscope": "4",
            "deltastagereflection": "5",
            "deltastagetransmission": "6"
        }
        role_user(username, role_mapping.get(microscope, "3"))
        
        update_variable(microscope, current_time)
        return f"Access key: {access_key}"
    else:
        wait_time = last_access_time + access_time - current_time
        minutes, seconds = divmod(wait_time, 60)
        return f"Please wait {minutes:02d}:{seconds:02d} before requesting a new key."

def show():
    with gr.Blocks() as demo:
        gr.Markdown("# Request Temporary Access Key")
        gr.Markdown(f"Keys will last {access_time/60} minutes before being overridable.")
        
        microscope_dropdown = gr.Dropdown(choices=microscopes, label="Choose a microscope:", value="microscope2")
        output = gr.Textbox(label="Access Key or Wait Time")
        
        generate_button = gr.Button("Request temporary access")
        generate_button.click(generate_access_key, inputs=[microscope_dropdown], outputs=[output])
        
    return demo

if __name__ == "__main__":
    show().launch()
