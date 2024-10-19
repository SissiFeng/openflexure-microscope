---
title: Openflexure Microscope
emoji: 🔬
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 3.50.2
app_file: app.py
pinned: false
license: mit
---

# Openflexure Microscope Remote Control

This Hugging Face Space provides a web interface for remote access and control of Openflexure Microscopes in the AC lab. Users can control microscopes, view live camera feeds, and manage access through temporary keys.

## Features

- Remote microscope control
- Live camera feed
- Temporary access key generation
- Device status monitoring
- GUI and Python-based control options

## Usage

1. Request a temporary access key
2. Use the key to access microscope controls
3. View live camera feed
4. Monitor device status

For more detailed instructions, please refer to the documentation tab within the application.

## Technology

- Gradio for the web interface
- MQTT for device communication
- HiveMQ as the MQTT broker

## License

This project is licensed under the MIT License.

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
