"""
Configuration for Video2Note.
"""
from dataclasses import dataclass, field
import platform
from pathlib import Path

import click

# --- Constants ---
SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'}
SUPPORTED_VIDEO_FORMATS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
ALL_SUPPORTED_FORMATS = SUPPORTED_AUDIO_FORMATS | SUPPORTED_VIDEO_FORMATS

TEMP_DIR_NAME = "temp"
TRANSCRIPTS_DIR_NAME = "transcripts"
WHISPER_CPP_PATH = "whisper.cpp"
HISTORY_FILE = Path(__file__).parent.parent / ".video2note_hist.json"


# --- Helper Functions for Config ---

def check_whisper_cpp() -> tuple[Path, Path]:
    """Checks for whisper.cpp binary and models directory."""
    script_dir = Path(__file__).parent.parent.resolve()
    whisper_dir = script_dir / WHISPER_CPP_PATH
    
    # Try to find the binary in a few common build paths (handles Windows .exe)
    exe_suffix = ".exe" if platform.system() == "Windows" else ""
    binary_name = f"whisper-cli{exe_suffix}"
    possible_paths = [
        whisper_dir / "build" / "bin" / binary_name,
        whisper_dir / "build" / "Release" / binary_name,
        whisper_dir / binary_name,
    ]
    
    whisper_bin = next((p for p in possible_paths if p.exists()), None)
    
    models_dir = whisper_dir / "models"

    if not whisper_bin:
        hint = (
            "Please build whisper.cpp first. On Windows, open 'x64 Native Tools Command Prompt for VS', then:\n"
            "  cd whisper.cpp\n  cmake -B build -DCMAKE_BUILD_TYPE=Release\n  cmake --build build --config Release\n"
        ) if platform.system() == "Windows" else (
            "Please build whisper.cpp first:\n  cd whisper.cpp && cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j"
        )
        raise click.ClickException(
            "whisper.cpp executable not found in expected paths:\n" +
            "\n".join(f"- {p}" for p in possible_paths) +
            f"\n{hint}"
        )

    return whisper_bin, models_dir

def check_model(models_dir: Path, model_name: str) -> Path:
    """Checks if a model file exists and returns its path."""
    model_path = models_dir / f"ggml-{model_name}.bin"
    if not model_path.exists():
        en_model_path = models_dir / f"ggml-{model_name}.en.bin"
        if en_model_path.exists():
            return en_model_path
        raise click.ClickException(
            f"Model not found: {model_path}\n"
            f"Please download it: cd {models_dir.parent} && ./models/download-ggml-model.sh {model_name}"
        )
    return model_path


# --- Main Configuration Class ---

@dataclass
class TranscriptionConfig:
    """Configuration for the transcription process."""
    model_name: str
    language: str
    threads: int

    whisper_bin: Path = field(init=False)
    models_dir: Path = field(init=False)
    model_path: Path = field(init=False)

    def __post_init__(self):
        """Checks paths and model after initialization."""
        self.whisper_bin, self.models_dir = check_whisper_cpp()
        self.model_path = check_model(self.models_dir, self.model_name) 