<![CDATA[<div align="center">

# 🧠 Meeting Architect

### Role-Aware Virtual Meeting Intelligence System

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-00f0ff?style=for-the-badge)](LICENSE)

**Transform raw meeting transcripts into structured intelligence — decisions, action items, and role-tailored summaries.**

*Powered by local LLM inference with complete privacy. Zero data leaves your machine.*

---

[Features](#-features) · [Architecture](#-architecture) · [Getting Started](#-getting-started) · [Usage](#-usage) · [Project Structure](#-project-structure) · [Tech Stack](#-tech-stack) · [License](#-license)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔒 **100% Local & Private** | All processing runs on-device — no cloud APIs, no data leakage |
| 🧠 **Role-Aware Analysis** | Tailored intelligence for **Engineering**, **Product**, and **Management** stakeholders |
| 🎙️ **Voice-to-Text** | Upload audio/video files — Whisper transcribes them locally |
| 📝 **Transcript Analysis** | Paste raw meeting text and get instant structured output |
| ⚡ **Structured JSON Output** | Pydantic-validated responses with decisions, action items & summaries |
| 🗄️ **Meeting Vault** | Auto-saved history with keyword-based department categorization |
| 🎨 **Cyberpunk UI** | Immersive Three.js 3D backgrounds with glassmorphism design |
| 🏷️ **Auto-Categorization** | Meetings are automatically tagged to relevant departments via keyword scanning |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit UI                        │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │  Landing Page │  │  Transcript  │  │  Media Upload │ │
│  │  (Three.js)   │  │  Analyzer    │  │  Analyzer     │ │
│  └──────────────┘  └──────┬───────┘  └───────┬───────┘ │
│                           │                  │         │
│  ┌────────────────────────┴──────────────────┘         │
│  │              Vault Sidebar                          │
│  └────────────────────────┬──────────────────────────┘ │
├───────────────────────────┼─────────────────────────────┤
│                    Core Engine                          │
│  ┌───────────┐  ┌────────┴────────┐  ┌──────────────┐  │
│  │  Whisper   │  │ MeetingAnalyzer │  │  Storage /   │  │
│  │  (STT)     │  │ (Ollama/Gemma)  │  │  Vault       │  │
│  └───────────┘  └────────┬────────┘  └──────────────┘  │
│                          │                              │
│  ┌───────────┐  ┌────────┴────────┐  ┌──────────────┐  │
│  │  Audio     │  │  Role Prompts   │  │  Pydantic    │  │
│  │  Processor │  │  (per role)     │  │  Schema      │  │
│  └───────────┘  └─────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed on your system:

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Ollama** — [Download](https://ollama.com/download)
- **FFmpeg** (required for audio/video processing) — see [FFmpeg Setup](#ffmpeg-setup) below

### 1. Clone the Repository

```bash
git clone https://github.com/YashsaiDessai/role-aware-virtual-meeting-intelligence-system.git
cd role-aware-virtual-meeting-intelligence-system
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
.\venv\Scripts\activate.bat

# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Pull the Gemma Model via Ollama

Make sure the Ollama application is running, then pull the required model:

```bash
ollama pull gemma4:e2b
```

> **Note:** The `gemma4:e2b` model is lightweight and works well for meeting analysis. You can also use `gemma4:e4b` for better accuracy if your hardware supports it.

### 5. Run the Application

```bash
streamlit run ui/app.py
```

The app will open in your browser at **http://localhost:8501**.

---

### FFmpeg Setup

FFmpeg is required for processing audio/video files. The app will auto-detect FFmpeg if it's installed via common methods:

<details>
<summary><strong>Windows</strong></summary>

```bash
# Using winget (recommended)
winget install Gyan.FFmpeg

# Using Chocolatey
choco install ffmpeg

# Using Scoop
scoop install ffmpeg
```

</details>

<details>
<summary><strong>macOS</strong></summary>

```bash
brew install ffmpeg
```

</details>

<details>
<summary><strong>Linux</strong></summary>

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

</details>

> **Tip:** If you only plan to use the **Transcript Analyzer** (paste text), you do **not** need FFmpeg.

---

## 📖 Usage

### Option 1: Transcript Analyzer

1. Launch the app and click the **📝 Transcript** card on the landing page
2. Select a **Stakeholder Lens** (Engineering / Product / Management)
3. Paste your raw meeting transcript into the text area
4. Click **⚡ Analyze Transcript**
5. View the structured output — Summary, Key Decisions, and Action Items
6. The analysis is automatically saved to the Meeting Vault

### Option 2: Media Analyzer

1. Launch the app and click the **🎙️ Audio / Video** card
2. Upload a meeting recording (`.mp4`, `.mov`, `.wav`, `.mp3`, etc.)
3. Click **🎙️ Transcribe** — Whisper processes the audio locally
4. Select your **Stakeholder Lens**
5. Click **⚡ Analyze Transcript**
6. View role-tailored results

### Meeting Vault

- Past analyses are automatically saved and grouped by department in the **sidebar**
- Click any archived meeting to review its analysis
- Meetings are auto-categorized using keyword detection — a single meeting can appear under multiple departments
- Use the department badges in the sidebar to switch between stakeholder lenses
- Click **🗑️ Clear History** to wipe all saved analyses

---

## 🎯 Stakeholder Roles

| Role | Focus Areas | Priority Rules |
|------|-------------|----------------|
| **🔧 Engineering** | Tech debt, blockers, architecture, testing & reliability | Unblocking tasks → high priority |
| **📦 Product** | Roadmap, customer impact, prioritization, cross-team deps | Upcoming release impact → high priority |
| **📊 Management** | Risks, deadlines, resource allocation, strategic alignment | Imminent deadlines & escalations → high priority |

---

## 📂 Project Structure

```
role-aware-virtual-meeting-intelligence-system/
│
├── ui/                          # Streamlit frontend
│   ├── app.py                   # Landing page with Three.js hero scene
│   ├── home_scene.html          # Three.js neural sphere animation
│   ├── background.html          # Three.js 3D document stack scene
│   ├── vault_sidebar.py         # Shared vault sidebar component
│   └── pages/
│       ├── 1_Transcript.py      # Paste & analyze transcript page
│       └── 2_Media.py           # Upload & transcribe media page
│
├── core/                        # Backend logic
│   ├── __init__.py
│   ├── engine.py                # MeetingAnalyzer — Ollama inference + retry loop
│   ├── prompts.py               # Role-specific system prompts
│   ├── schema.py                # Pydantic models (MeetingOutput, ActionItem)
│   ├── audio.py                 # AudioProcessor — Whisper STT + FFmpeg
│   └── storage.py               # Meeting Vault — JSON storage & auto-categorization
│
├── data/
│   └── vault/                   # Local JSON storage for saved analyses (gitignored)
│
├── tests/                       # Test directory
├── requirements.txt             # Python dependencies
├── .gitignore
├── LICENSE                      # MIT License
└── README.md
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | [Streamlit](https://streamlit.io) with custom CSS (Cyberpunk/Glassmorphism) |
| **3D Visuals** | [Three.js](https://threejs.org) (neural sphere + document stack scenes) |
| **LLM Inference** | [Ollama](https://ollama.com) with [Gemma 4](https://ai.google.dev/gemma) (local, private) |
| **Speech-to-Text** | [OpenAI Whisper](https://github.com/openai/whisper) (local inference) |
| **Audio Processing** | [FFmpeg](https://ffmpeg.org) via subprocess |
| **Schema Validation** | [Pydantic](https://docs.pydantic.dev) |
| **Data Storage** | Local JSON files (zero external databases) |
| **Language** | Python 3.10+ |

---

## 🔧 Configuration

### Changing the LLM Model

Edit the model name in `core/engine.py`:

```python
class MeetingAnalyzer:
    def __init__(self, model: str = "gemma4:e2b") -> None:
        self.model = model
```

You can use any Ollama-compatible model:

```bash
# Pull a different model
ollama pull gemma4:e4b      # larger, more accurate
ollama pull llama3.2         # alternative model
```

### Changing the Whisper Model

Edit the model size in `core/audio.py`:

```python
model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
```

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | ~39 MB | Fastest | Basic |
| `base` | ~140 MB | Fast | Good (default) |
| `small` | ~460 MB | Moderate | Better |
| `medium` | ~1.5 GB | Slow | Great |
| `large` | ~2.9 GB | Slowest | Best |

---

## 🧪 Running the Engine Standalone

You can test the core engine without the UI:

```bash
python -m core.engine
```

This runs a built-in smoke test with a sample transcript across all three roles.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for hackathons**

*Local-First · Zero Data Leakage · Role-Aware Intelligence*

</div>
]]>