import gradio as gr
import stable_whisper
import torch
import gc
import sys
import threading
import queue
from sub_gen import generate_subtitles

LOADED_MODEL_NAME = None
LOADED_MODEL = None

def get_model(model_name):
    global LOADED_MODEL_NAME, LOADED_MODEL
    if LOADED_MODEL_NAME != model_name:
        LOADED_MODEL = None
        gc.collect()
        if torch.cuda.is_available(): torch.cuda.empty_cache()
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        LOADED_MODEL = stable_whisper.load_model(model_name, device=device)
        LOADED_MODEL_NAME = model_name
    return LOADED_MODEL

# Intercepts terminal prints and pipes them to the Gradio UI
class LogRedirector:
    def __init__(self, q):
        self.q = q
    def write(self, msg):
        self.q.put(msg)
        sys.__stdout__.write(msg)
    def flush(self):
        sys.__stdout__.flush()

def process_video(video_path, model_type, task):
    if not video_path:
        yield None, None, "Error: No video uploaded.", "Failed"
        return
    
    yield None, None, "Initializing model and securing VRAM...", "Loading..."

    q = queue.Queue()
    redirector = LogRedirector(q)
    result_container = {}

    def run_ml():
        old_stdout = sys.stdout
        sys.stdout = redirector
        try:
            model = get_model(model_type)
            srt = generate_subtitles(video_path, model=model, task=task)
            result_container['srt'] = srt
        except Exception as e:
            result_container['error'] = str(e)
        finally:
            sys.stdout = old_stdout
            q.put(None) # Signal the generator to stop

    # Run the blocking ML task in a separate thread
    t = threading.Thread(target=run_ml)
    t.start()

    live_logs = ""
    while True:
        msg = q.get()
        if msg is None:
            break
        live_logs += msg
        # Yield streams the updated text to the frontend instantly
        yield gr.update(), gr.update(), live_logs, "Transcribing..."

    t.join()

    if 'error' in result_container:
        yield None, None, live_logs + f"\nError: {result_container['error']}", "Failed"
    else:
        srt_path = result_container['srt']
        yield gr.Video(value=video_path, subtitles=srt_path), srt_path, live_logs, "Complete!"

with gr.Blocks() as demo:
    gr.Markdown("Subtitle Generator")
    
    with gr.Row():
        with gr.Column():
            video_input = gr.Video(label="Upload Video", sources=["upload"])
            model_dropdown = gr.Dropdown(
                choices=["tiny.en", "base.en", "small.en", "medium.en", "large-v3",
                        "tiny", "base", "small", "medium","turbo"], 
                value="small.en", 
                label="Model Size"
            )
            task_dropdown = gr.Dropdown(
                choices=["transcribe", "translate"], 
                value="transcribe", 
                label="Action"
            )
            submit_btn = gr.Button("Generate Subtitles", variant="primary")
            status_text = gr.Textbox(label="Status", interactive=False)
            
        with gr.Column():
            video_output = gr.Video(label="Preview with Subtitles")
            srt_download = gr.File(label="Download .srt File")
            
    with gr.Row():
        terminal_output = gr.Textbox(
            label="Live Terminal Output", 
            lines=12, 
            max_lines=15, 
            interactive=False,
            autoscroll=True
        )

    submit_btn.click(
        fn=process_video,
        inputs=[video_input, model_dropdown, task_dropdown],
        outputs=[video_output, srt_download, terminal_output, status_text]
    )

if __name__ == "__main__":
    demo.queue().launch(
        theme=gr.themes.Soft(), 
        server_name="0.0.0.0", 
        server_port=7860,
        share=True
    )