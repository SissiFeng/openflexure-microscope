import gradio as gr

def show():
    with gr.Blocks() as demo:
        gr.Markdown("# Download and Installation")
        
        gr.Markdown("""
        ## Installation Instructions
        
        Currently, this program needs to be installed manually. Follow these steps:
        
        1. Clone the repository from GitHub:
           ```
           git clone https://github.com/AccelerationConsortium/ac-training-lab.git
           ```
        
        2. Navigate to the project directory:
           ```
           cd ac-training-lab/src/ac_training_lab/openflexure
           ```
        
        3. Install the required dependencies:
           ```
           pip install -r requirements.txt
           ```
        
        **Note:** A more streamlined installation process is under development.
        """)
        
        gr.Markdown("## Additional Resources")
        
        gr.Markdown("""
        - [AC GitHub Repository](https://github.com/AccelerationConsortium/ac-training-lab/tree/main/src%2Fac_training_lab%2Fopenflexure)
        - [OpenFlexure Stitching Library](https://gitlab.com/openflexure/openflexure-stitching) (Required for image stitching functionality)
        """)
        
        gr.Markdown("""
        ## Troubleshooting
        
        If you encounter any issues during installation or usage, please check the following:
        
        1. Ensure you have Python 3.7 or higher installed.
        2. Make sure all dependencies are correctly installed.
        3. Check the GitHub repository for any known issues or updates.
        
        For further assistance, please open an issue on the GitHub repository.
        """)

    return demo

if __name__ == "__main__":
    show().launch()
