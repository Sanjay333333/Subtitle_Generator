import stable_whisper
import os
import torch

def generate_subtitles(video_path, model=None, model_type="small.en", task="transcribe"):
    if model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = stable_whisper.load_model(model_type, device=device)

    result = model.transcribe(video_path, task=task, verbose=True)

    result.split_by_length(max_chars=42)

    base_name = os.path.basename(video_path)
    output_filename = os.path.splitext(base_name)[0] + ".srt"
    
    result.to_srt_vtt(output_filename, segment_level=True, word_level=False)

    return output_filename