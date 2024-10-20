import gradio as gr
import logging
import secrets
import string
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient
from os import environ
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGODB_URI = environ["MONGODB_URI"]

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

def generate_access_key(microscope):
    # Generate a random key
    key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
    
    # Set expiration time (e.g., 3 minutes from now)
    expiration_time = datetime.now() + timedelta(minutes=3)
    
    # Store the key in MongoDB (you might want to encrypt it in a real application)
    update_variable(f"{microscope}_key", {"key": key, "expiration": expiration_time})
    
    logger.info(f"Generated key for {microscope}, expires at {expiration_time}")
    
    return f"Your temporary access key for {microscope} is: {key}\nIt will expire at {expiration_time}"

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
