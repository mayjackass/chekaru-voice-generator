# 🗣️ Bark Voice Generator (Custom TTS UI)

**Developer:** Mayj Amilano  
**Description:**  
A full-featured desktop Text-to-Speech (TTS) application built with Python and Tkinter, powered by **Bark’s open-source voice models** from **Suno AI**.  
It features a clean UI, threaded performance, and dynamic voice fetching from the community-maintained Bark Speaker Directory.

---

## 🎧 Features
- Splash screen with threaded model loading  
- Dynamic fetching of community voice models (if online)  
- Offline fallback to local voices  
- Searchable dropdown with descriptive voice names  
- “Preview Voice” button for quick audio test  
- Intelligent text-splitting for long inputs  
- Multi-chunk generation merged into one seamless `.wav`  
- Progress feedback and threaded UI for smooth performance  

---

## 🧠 Requirements
```bash
pip install bark torch scipy numpy simpleaudio requests
