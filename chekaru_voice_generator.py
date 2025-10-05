"""
=========================================================
CHEKARU VOICE GENERATOR - Dynamic Voice Model + Preview Edition
Developed by: Mayj Amilano
=========================================================

A full-featured text-to-speech (TTS) desktop app powered by
Bark’s open-source voice models from Suno AI. Users can now
search and preview community-shared voices before generating
full-length audio.

Features:
- Splash screen with threaded model loading
- Dynamic fetching of community voice models (if online)
- Offline fallback to local voices
- Searchable dropdown with descriptive names
- "Preview Voice" button for instant 2-second sample
- Intelligent text-splitting for long inputs
- Multi-chunk generation merged into one .wav file
- Threaded UI with progress and status feedback
=========================================================
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write
import numpy as np
import textwrap
import requests
import simpleaudio as sa
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# ----------------------------
# Local voice fallback list
# ----------------------------
LOCAL_VOICE_OPTIONS = [
    {"id": "v2/en_speaker_0", "name": "Deep Male (English)"},
    {"id": "v2/en_speaker_1", "name": "Warm Female (English)"},
    {"id": "v2/en_speaker_2", "name": "Young Male (English)"},
    {"id": "v2/en_speaker_3", "name": "Bright Female (English)"},
    {"id": "v2/en_speaker_4", "name": "Calm Narrator (English)"},
    {"id": "v2/en_speaker_5", "name": "Energetic Performer (English)"},
    {"id": "v2/en_speaker_6", "name": "Cinematic Deep Tone (English)"},
    {"id": "v2/en_speaker_7", "name": "Soft Female (English)"},
]

# ----------------------------
# Fetch Bark Community Voices
# ----------------------------
def fetch_community_voices():
    url = "https://raw.githubusercontent.com/rsxdalv/bark-speaker-directory/main/src/voices.json"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return [{"id": v["id"], "name": v["name"]} for v in data]
    except Exception as e:
        print("Unable to fetch community voices:", e)
    return []

# ----------------------------
# Combine voice lists
# ----------------------------
def get_voice_catalog():
    remote_voices = fetch_community_voices()
    if remote_voices:
        print(f"Fetched {len(remote_voices)} community voices.")
        ids = {v["id"] for v in LOCAL_VOICE_OPTIONS}
        merged = LOCAL_VOICE_OPTIONS + [v for v in remote_voices if v["id"] not in ids]
        return merged
    else:
        print("Using local voices only (offline mode).")
        return LOCAL_VOICE_OPTIONS

# ----------------------------
# Splash Screen
# ----------------------------
def show_splash():
    splash = tk.Tk()
    splash.title("Chekaru Voice Generator")
    splash.geometry("400x220")
    splash.config(bg="#1a1a1a")
    splash.resizable(False, False)

    label = tk.Label(
        splash,
        text="Loading Voice Models...\nPlease wait a moment",
        font=("Arial", 12, "bold"),
        fg="white",
        bg="#1a1a1a"
    )
    label.pack(expand=True, pady=30)

    pb = ttk.Progressbar(splash, mode="indeterminate", length=280)
    pb.pack(pady=20)
    pb.start(10)

    def load_models():
        try:
            preload_models()
            voices = get_voice_catalog()
            splash.after(300, lambda: [pb.stop(), splash.destroy(), show_main_ui(voices)])
        except Exception as e:
            pb.stop()
            messagebox.showerror("Error loading models", str(e))
            splash.destroy()

    threading.Thread(target=load_models, daemon=True).start()
    splash.mainloop()

# ----------------------------
# Main UI
# ----------------------------
def show_main_ui(voice_catalog):
    root = tk.Tk()
    root.title("Chekaru Voice Generator")
    root.geometry("620x520")
    root.resizable(False, False)

    tk.Label(root, text="Enter text to generate:", font=("Arial", 11, "bold")).pack(pady=5)
    text_box = tk.Text(root, height=8, width=70, wrap="word")
    text_box.pack(pady=5)

    tk.Label(root, text="Select Voice Model:", font=("Arial", 11, "bold")).pack(pady=5)

    # Voice list (searchable Combobox)
    voice_names = [v["name"] for v in voice_catalog]
    voice_choice = ttk.Combobox(root, values=voice_names, width=50)
    voice_choice.set(voice_names[0])
    voice_choice.pack(pady=5)

    status_label = tk.Label(root, text="Idle", font=("Arial", 10), foreground="gray")
    status_label.pack(pady=10)

    progress_bar = ttk.Progressbar(root, mode='indeterminate', length=440)
    progress_bar.pack(pady=10)
    progress_bar.pack_forget()

    # ------------------------
    # Audio Generation Logic
    # ------------------------
    def generate_voice():
        text_prompt = text_box.get("1.0", tk.END).strip()
        if not text_prompt:
            messagebox.showwarning("Missing text", "Please enter text to generate.")
            return

        selected_name = voice_choice.get()
        voice_entry = next((v for v in voice_catalog if v["name"] == selected_name), voice_catalog[0])
        voice_model = voice_entry["id"]

        def worker():
            try:
                progress_bar.pack(pady=10)
                progress_bar.start(10)
                status_label.config(text="Generating voice...", fg="orange")

                # Split long text automatically
                chunks = textwrap.wrap(text_prompt, width=250)
                combined_audio = []

                for i, chunk in enumerate(chunks):
                    status_label.config(text=f"Processing chunk {i+1}/{len(chunks)}...", fg="orange")
                    root.update_idletasks()
                    audio_array = generate_audio(chunk, history_prompt=voice_model)
                    combined_audio.append(audio_array)

                # Merge all audio chunks
                final_audio = np.concatenate(combined_audio)

                filename = filedialog.asksaveasfilename(
                    title="Save audio file as",
                    defaultextension=".wav",
                    filetypes=[("WAV files", "*.wav")]
                )
                if filename:
                    write(filename, SAMPLE_RATE, final_audio)
                    status_label.config(text=f"✅ Done! Saved to:\n{filename}", fg="green")
                else:
                    status_label.config(text="Canceled by user.", fg="gray")

            except Exception as e:
                messagebox.showerror("Error", str(e))
                status_label.config(text="❌ Error during generation.", fg="red")
            finally:
                progress_bar.stop()
                progress_bar.pack_forget()

        threading.Thread(target=worker, daemon=True).start()

    # ------------------------
    # Voice Preview Logic
    # ------------------------
    def preview_voice():
        selected_name = voice_choice.get()
        voice_entry = next((v for v in voice_catalog if v["name"] == selected_name), voice_catalog[0])
        voice_model = voice_entry["id"]

        def worker_preview():
            try:
                progress_bar.pack(pady=10)
                progress_bar.start(10)
                status_label.config(text=f"Previewing: {selected_name}", fg="orange")

                # Short sample phrase
                sample_text = "Hello, this is a quick voice preview."
                audio_array = generate_audio(sample_text, history_prompt=voice_model)

                # Play the preview
                temp_file = "preview_sample.wav"
                write(temp_file, SAMPLE_RATE, audio_array)
                wave_obj = sa.WaveObject.from_wave_file(temp_file)
                play_obj = wave_obj.play()
                play_obj.wait_done()

                status_label.config(text=f"Preview finished: {selected_name}", fg="green")

            except Exception as e:
                messagebox.showerror("Error", str(e))
                status_label.config(text="❌ Error in preview.", fg="red")
            finally:
                progress_bar.stop()
                progress_bar.pack_forget()

        threading.Thread(target=worker_preview, daemon=True).start()

    # Buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=15)
    ttk.Button(btn_frame, text="Preview Voice", command=preview_voice).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Generate Audio", command=generate_voice).grid(row=0, column=1, padx=10)

    root.mainloop()

# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    show_splash()
