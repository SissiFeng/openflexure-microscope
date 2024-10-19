import gradio as gr

def show():
    with gr.Blocks() as demo:
        gr.Markdown("# OpenFlexure Microscope Documentation")
        
        gr.Markdown("""
        ## Introduction
        The OpenFlexure Microscope is an open-source, 3D-printed microscope designed for accessibility and customization.

        ## Features
        - High-resolution imaging
        - 3D-printed parts
        - Customizable design
        - Open-source software

        ## Usage Instructions
        1. Power on the microscope
        2. Place your sample on the stage
        3. Use the controls to focus and capture images

        ## Troubleshooting
        If you encounter any issues, please check our FAQ or contact support.
        """)

    return demo

if __name__ == "__main__":
    show().launch()