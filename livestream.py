import gradio as gr

def show():
    livestreammicroscope2 = "https://youtube.com/live/RhkhjbebLfs"

    with gr.Blocks() as demo:
        gr.Markdown("# Livestream")
        gr.Markdown("Here are the live microscope camera views of all the microscopes")
        
        gr.Markdown("## Microscope 2:")
        gr.HTML(f'<a href="{livestreammicroscope2}" target="_blank">Microscope 2 Livestream</a>')

        
        # gr.Markdown("## Microscope 1:")
        # gr.HTML('<a href="your_microscope1_link" target="_blank">Microscope 1 Livestream</a>')
        
        # gr.Markdown("## Delta Stage Transmission:")
        # gr.HTML('<a href="your_deltastagetransmission_link" target="_blank">Delta Stage Transmission Livestream</a>')
        
        # gr.Markdown("## Delta Stage Reflection:")
        # gr.HTML('<a href="your_deltastagereflection_link" target="_blank">Delta Stage Reflection Livestream</a>')

    return demo

if __name__ == "__main__":
    show().launch()