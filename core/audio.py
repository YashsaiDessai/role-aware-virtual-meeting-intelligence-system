"""
🎙️ AudioProcessor — Local Voice-to-Text via OpenAI Whisper

Handles video/audio file ingestion:
  1. If video (.mp4, .mov, .webm, .mkv) → extract audio track to temp WAV
  2. Transcribe audio via Whisper (runs entirely on-device)
  3. Return plain-text transcript
  4. Clean up temp files

All processing is 100% local — zero data leaves the machine.
"""

from __future__ import annotations
import whisper
import moviepy.editor as mp  # This is the line that was failing
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  Auto-detect ffmpeg and add to PATH if needed
# ------------------------------------------------------------------ #
def _ensure_ffmpeg_on_path() -> None:
    """Find ffmpeg on the system and add its directory to PATH if missing.

    Checks common install locations (winget, chocolatey, scoop, manual)
    so that Whisper and moviepy can locate the binary without the user
    needing to manually configure their system PATH.
    """
    if shutil.which("ffmpeg"):
        return  # already reachable

    # Common locations where ffmpeg may be installed on Windows
    search_roots = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages",
        Path("C:/ProgramData/chocolatey/bin"),
        Path("C:/tools/ffmpeg"),
        Path("C:/ffmpeg"),
        Path(os.environ.get("USERPROFILE", "")) / "scoop" / "shims",
    ]

    for root in search_roots:
        if not root.exists():
            continue
        for match in root.rglob("ffmpeg.exe"):
            ffmpeg_dir = str(match.parent)
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
            logger.info("✓ Found ffmpeg at %s — added to PATH", ffmpeg_dir)
            return

    logger.warning(
        "⚠ ffmpeg not found. Whisper/moviepy need ffmpeg for audio processing. "
        "Install it with:  winget install Gyan.FFmpeg"
    )


_ensure_ffmpeg_on_path()

# Supported extensions
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv", ".avi"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".wma"}
ALL_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS


@st.cache_resource(show_spinner=False)
def _load_whisper_model():
    """Load Whisper model once and cache across Streamlit reruns.

    Uses the 'base' model (~140 MB) — good balance of speed and accuracy
    for meeting recordings. Upgrade to 'small' or 'medium' if you have
    more VRAM/RAM and need better accuracy.
    """
    import whisper  # lazy import so app loads fast even if whisper isn't used

    logger.info("Loading Whisper 'base' model …")
    model = whisper.load_model("base")
    logger.info("✓ Whisper model loaded")
    return model


class AudioProcessor:
    """Transcribes audio/video files using a locally-running Whisper model."""

    def __init__(self) -> None:
        self.model = _load_whisper_model()

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #
    def transcribe_file(self, file_path: str | Path) -> str:
        """Transcribe an audio or video file and return the text.

        Parameters
        ----------
        file_path : str | Path
            Path to the media file on disk.

        Returns
        -------
        str
            The transcribed text.

        Raises
        ------
        ValueError
            If the file extension is not supported.
        RuntimeError
            If video audio-extraction or transcription fails.
        """
        file_path = Path(file_path)
        ext = file_path.suffix.lower()

        if ext not in ALL_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '{ext}'. "
                f"Accepted: {sorted(ALL_EXTENSIONS)}"
            )

        # If video → extract audio to a temp WAV first
        if ext in VIDEO_EXTENSIONS:
            wav_path = self._extract_audio(file_path)
            try:
                return self._transcribe(wav_path)
            finally:
                # Always clean up the temp WAV
                self._safe_delete(wav_path)
        else:
            return self._transcribe(str(file_path))

    # ------------------------------------------------------------------ #
    #  Private helpers
    # ------------------------------------------------------------------ #
    def _extract_audio(self, video_path: Path) -> str:
        """Extract the audio track from a video file using ffmpeg directly.

        Converts to 16 kHz mono WAV (optimal for Whisper).
        Returns the path to a temporary .wav file.
        """
        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            raise RuntimeError(
                "ffmpeg is required for video processing but was not found. "
                "Install it with:  winget install Gyan.FFmpeg"
            )

        tmp_wav = tempfile.mktemp(suffix=".wav", prefix="meeting_audio_")
        logger.info("Extracting audio from %s → %s", video_path, tmp_wav)

        try:
            result = subprocess.run(
                [
                    ffmpeg_bin,
                    "-i", str(video_path),
                    "-vn",                # drop video stream
                    "-acodec", "pcm_s16le",  # 16-bit PCM
                    "-ar", "16000",       # 16 kHz (Whisper optimal)
                    "-ac", "1",           # mono
                    "-y",                 # overwrite output
                    tmp_wav,
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 min timeout for large files
            )
            if result.returncode != 0:
                self._safe_delete(tmp_wav)
                raise RuntimeError(
                    f"ffmpeg exited with code {result.returncode}: {result.stderr[:500]}"
                )
        except subprocess.TimeoutExpired:
            self._safe_delete(tmp_wav)
            raise RuntimeError("Audio extraction timed out (>5 min)")
        except FileNotFoundError:
            self._safe_delete(tmp_wav)
            raise RuntimeError("ffmpeg binary not found at runtime")
        except RuntimeError:
            raise
        except Exception as exc:
            self._safe_delete(tmp_wav)
            raise RuntimeError(
                f"Failed to extract audio from video: {exc}"
            ) from exc

        return tmp_wav

    def _transcribe(self, audio_path: str) -> str:
        """Run Whisper inference on an audio file."""
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
        logger.info(
            "✓ Transcription complete — %d characters", len(text)
        )
        return text

    @staticmethod
    def _safe_delete(path: str | Path) -> None:
        """Delete a file without raising if it doesn't exist."""
        try:
            os.remove(path)
        except OSError:
            pass
