"""
🎙️ AudioProcessor — Local Voice-to-Text via OpenAI Whisper

Handles video/audio file ingestion:
  1. If video (.mp4, .mov, .webm, .mkv) → extract audio track to temp WAV
  2. If audio (any format) → convert to temp WAV via ffmpeg (fixes WinError 2)
  3. Transcribe audio via Whisper (runs entirely on-device)
  4. Return plain-text transcript
  5. Clean up temp files

All processing is 100% local — zero data leaves the machine.
"""

from __future__ import annotations
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  Auto-detect ffmpeg — system PATH first, then imageio-ffmpeg bundle
# ------------------------------------------------------------------ #
def _ensure_ffmpeg_on_path() -> None:
    """Find ffmpeg on the system and add its directory to PATH if missing.

    Search order:
      1. Already on system PATH (fast path).
      2. Common Windows install locations (winget, choco, scoop, manual).
      3. imageio-ffmpeg bundled static binary (works without any system install).
    """
    if shutil.which("ffmpeg"):
        return  # already reachable — nothing to do

    search_roots = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages",
        Path("C:/ProgramData/chocolatey/bin"),
        Path("C:/tools/ffmpeg/bin"),
        Path("C:/tools/ffmpeg"),
        Path("C:/ffmpeg/bin"),
        Path("C:/ffmpeg"),
        Path(os.environ.get("USERPROFILE", "")) / "scoop" / "shims",
        Path(os.environ.get("APPDATA", "")) / "ffmpeg" / "bin",
    ]

    for root in search_roots:
        if not root.exists():
            continue
        for match in root.rglob("ffmpeg.exe"):
            ffmpeg_dir = str(match.parent)
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
            logger.info("✓ Found ffmpeg at %s — added to PATH", ffmpeg_dir)
            return

    # ── Fallback: use the static binary bundled with imageio-ffmpeg ──────
    try:
        import imageio_ffmpeg  # type: ignore
        bundled = imageio_ffmpeg.get_ffmpeg_exe()
        if bundled and Path(bundled).exists():
            ffmpeg_dir = str(Path(bundled).parent)
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
            # Also expose as explicit env var so _get_ffmpeg_bin can find it
            os.environ["_IMAGEIO_FFMPEG_EXE"] = bundled
            logger.info("✓ Using imageio-ffmpeg bundled binary: %s", bundled)
            return
    except Exception as _exc:
        logger.debug("imageio-ffmpeg fallback failed: %s", _exc)

    logger.warning(
        "⚠ ffmpeg not found anywhere. Install with:  winget install Gyan.FFmpeg\n"
        "  OR:  pip install imageio-ffmpeg"
    )


_ensure_ffmpeg_on_path()

# Supported extensions
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv", ".avi"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".wma"}
ALL_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS


@st.cache_resource(show_spinner=False)
def _load_whisper_model():
    """Load Whisper model once and cache across Streamlit reruns."""
    import whisper  # lazy import
    logger.info("Loading Whisper 'base' model …")
    model = whisper.load_model("base")
    logger.info("✓ Whisper model loaded")
    return model


def _get_ffmpeg_bin() -> str:
    """Return path to ffmpeg binary.

    Checks (in order):
      1. System PATH via shutil.which
      2. _IMAGEIO_FFMPEG_EXE env var set by _ensure_ffmpeg_on_path
      3. Direct imageio-ffmpeg import as final fallback
    """
    # 1. System PATH
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        return ffmpeg_bin

    # 2. imageio-ffmpeg env var (set at module load time)
    bundled = os.environ.get("_IMAGEIO_FFMPEG_EXE", "")
    if bundled and Path(bundled).exists():
        return bundled

    # 3. Try importing imageio-ffmpeg directly
    try:
        import imageio_ffmpeg  # type: ignore
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).exists():
            return exe
    except Exception:
        pass

    raise RuntimeError(
        "ffmpeg is required but was not found.\n"
        "Fix option A (recommended): pip install imageio-ffmpeg\n"
        "Fix option B: winget install Gyan.FFmpeg  (then restart the app)"
    )


def _convert_to_wav(input_path: str | Path) -> str:
    """
    Convert any audio/video file to a 16 kHz mono WAV using ffmpeg.
    Returns path to a temporary WAV file (caller must delete it).

    This is the core fix for [WinError 2]: Whisper's internal ffmpeg call
    sometimes fails on Windows with certain audio codecs (mp3, m4a, etc.)
    when given a path with spaces or unusual temp directory paths.
    By pre-converting to PCM WAV ourselves, Whisper only needs to read
    a plain raw audio file — no ffmpeg required internally.
    """
    ffmpeg_bin = _get_ffmpeg_bin()

    # Use NamedTemporaryFile to get a safe path, close it immediately
    # so ffmpeg can write to it on Windows (no file-locking issues)
    tmp_fd, tmp_wav = tempfile.mkstemp(suffix=".wav", prefix="meeting_audio_")
    os.close(tmp_fd)  # Release the file descriptor immediately

    input_path = str(input_path)
    logger.info("Converting %s → WAV %s", input_path, tmp_wav)

    try:
        result = subprocess.run(
            [
                ffmpeg_bin,
                "-y",                  # overwrite output
                "-i", input_path,
                "-vn",                 # drop video stream
                "-acodec", "pcm_s16le",  # 16-bit PCM
                "-ar", "16000",        # 16 kHz (Whisper optimal)
                "-ac", "1",            # mono
                tmp_wav,
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            _safe_delete(tmp_wav)
            raise RuntimeError(
                f"ffmpeg conversion failed (code {result.returncode}):\n"
                f"{result.stderr[-800:]}"
            )
    except subprocess.TimeoutExpired:
        _safe_delete(tmp_wav)
        raise RuntimeError("Audio conversion timed out (>5 min)")
    except FileNotFoundError:
        _safe_delete(tmp_wav)
        raise RuntimeError("ffmpeg binary not found at runtime — reinstall ffmpeg")
    except RuntimeError:
        raise
    except Exception as exc:
        _safe_delete(tmp_wav)
        raise RuntimeError(f"Failed to convert audio: {exc}") from exc

    return tmp_wav


def _safe_delete(path: str | Path) -> None:
    """Delete a file without raising if it doesn't exist."""
    try:
        os.remove(path)
    except OSError:
        pass


class AudioProcessor:
    """Transcribes audio/video files using a locally-running Whisper model."""

    def __init__(self) -> None:
        self.model = _load_whisper_model()

    def transcribe_file(self, file_path: str | Path) -> str:
        """
        Transcribe an audio or video file and return the text.

        Strategy:
          - All files (video AND audio) are first converted to a 16 kHz
            mono WAV via ffmpeg using mkstemp (no file-locking on Windows).
          - Whisper only ever sees a plain PCM WAV → eliminates [WinError 2].
        """
        file_path = Path(file_path)
        ext = file_path.suffix.lower()

        if ext not in ALL_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '{ext}'. "
                f"Accepted: {sorted(ALL_EXTENSIONS)}"
            )

        # Always convert to WAV first — fixes WinError 2 on Windows for ALL formats
        wav_path = _convert_to_wav(file_path)
        try:
            return self._transcribe(wav_path)
        finally:
            _safe_delete(wav_path)

    def _transcribe(self, audio_path: str) -> str:
        """Run Whisper inference on a WAV file."""
        logger.info("Transcribing %s with Whisper …", audio_path)
        try:
            result = self.model.transcribe(
                audio_path,
                language=None,   # auto-detect language
                fp16=False,      # CPU-safe; set True if you have a CUDA GPU
            )
        except Exception as exc:
            raise RuntimeError(
                f"Whisper transcription failed: {exc}"
            ) from exc

        text = result.get("text", "").strip()
        logger.info("✓ Transcription complete — %d characters", len(text))
        return text
