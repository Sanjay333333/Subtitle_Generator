# 🎬 AI Subtitle Generator

A fast, interactive web application built with **Gradio** and **stable-whisper** that automatically generates synchronized `.srt` subtitles for your video files. It includes live transcription logging, in-browser subtitle preview, and flexible model selection.

---

## ✨ Features

- **High-Precision Timestamps:** Powered by [`stable-whisper`](https://github.com/jianfch/stable-ts) to ensure accurate word- and segment-level subtitle synchronization.
- **Readable Subtitle Formatting:** Automatically splits transcript segments to a readable maximum length (`42` characters per line) to prevent screen overcrowding.
- **Real-Time Terminal Streaming:** Intercepts standard output and pipes live Whisper transcription progress directly into the Gradio UI.
- **Interactive UI Preview:** Watch the uploaded video with generated subtitles rendered directly in your browser.
- **Multiple Whisper Models:** Switch dynamically between English-specialized (`tiny.en`, `small.en`, `medium.en`) and multilingual models (`large-v3`, `turbo`, etc.).
- **Translate or Transcribe:** Support for transcribing original speech or translating foreign audio directly into English.
- **VRAM & Memory Management:** Efficiently unloads prior models and flushes CUDA cache upon model switching to prevent out-of-memory errors.
- **Local Working Directory Output:** Automatically saves generated `.srt` files straight to your project directory.

---

## 📁 Project Structure

```text
.
├── app.py           # Gradio web interface, thread management, and log redirection
├── sub_gen.py       # Core transcription pipeline and SRT file generation
└── README.md        # Project documentation
```

---

## 🛠️ Prerequisites

1. **Python 3.9+**
2. **FFmpeg:** Required by Whisper to decode media files.
   - **Ubuntu/Debian:** `sudo apt install ffmpeg`
   - **macOS (Homebrew):** `brew install ffmpeg`
   - **Windows (Chocolatey / Scoop):** `choco install ffmpeg` or `scoop install ffmpeg`
3. **NVIDIA GPU (Recommended):** CUDA-compatible GPU for accelerated inference (falls back to CPU automatically if unavailable).

---

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/subtitle-generator.git
   cd subtitle-generator
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Linux/macOS:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install PyTorch:**
   Install the appropriate PyTorch build for your CUDA setup from [pytorch.org](https://pytorch.org/get-started/locally/). For example:
   ```bash
   # CUDA 12.1 example:
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

4. **Install required dependencies:**
   ```bash
   pip install stable-whisper gradio
   ```

---

## 💻 Usage

1. **Launch the application:**
   ```bash
   python app.py
   ```

2. **Open the Web UI:**
   - Open your browser and navigate to `http://localhost:7860` (or access the generated public share link if `share=True`).

3. **Generate Subtitles:**
   1. Drag and drop your video file into the **Upload Video** box.
   2. Select your desired **Model Size** (e.g., `small.en` for fast English transcription or `large-v3` / `turbo` for complex audio).
   3. Choose the **Action** (`transcribe` or `translate`).
   4. Click **Generate Subtitles**.
   5. Monitor real-time progress via the **Live Terminal Output** box.
   6. Once finished, preview the video with embedded subtitles or download the exported `.srt` file.

---

## ⚙️ How It Works

1. **Model Loader (`get_model`):** Caches the loaded Whisper model in memory. When changing models, it performs garbage collection (`gc.collect()`) and empties CUDA cache (`torch.cuda.empty_cache()`).
2. **Standard Output Redirection (`LogRedirector`):** Captures stdout during `model.transcribe(..., verbose=True)` in a background thread and forwards messages through a thread-safe `queue.Queue`.
3. **Subtitle Post-Processing:** `sub_gen.py` formats the output using `split_by_length(max_chars=42)` and exports segment-level subtitle tracks into standard `.srt` format using the video's base filename.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).