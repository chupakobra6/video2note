"""
Utility functions for Video2Note.
"""
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import ffmpeg
import numpy as np

from .config import HISTORY_FILE, TranscriptionConfig

logger = logging.getLogger(__name__)


# --- History and ETA Calculation ---

def load_hist() -> Dict[str, List[List[float]]]:
    """Loads transcription history from the JSON file."""
    if not HISTORY_FILE.exists():
        return defaultdict(list)
    try:
        hist_data = json.loads(HISTORY_FILE.read_text())
        # Basic validation
        clean_hist = defaultdict(list)
        for key, values in hist_data.items():
            if values and isinstance(values, list) and len(values) > 0 and isinstance(values[0], list):
                clean_hist[key] = values
        return clean_hist
    except (json.JSONDecodeError, TypeError):
        return defaultdict(list)

def save_hist(hist: Dict[str, List[List[float]]]) -> None:
    """Saves transcription history to the JSON file."""
    try:
        HISTORY_FILE.write_text(json.dumps(hist, indent=2))
    except IOError as e:
        logger.warning(f"Could not save history file: {e}")


def get_run_signature(config: TranscriptionConfig) -> str:
    """Creates a unique signature for a transcription run configuration."""
    return f"{config.model_name}|cpu|{config.threads}"


def calculate_eta(config: TranscriptionConfig, audio_duration: float) -> Optional[float]:
    """Predicts the execution time based on historical data."""
    hist = load_hist()
    sig = get_run_signature(config)
    samples = hist.get(sig, [])

    if not samples or len(samples) < 1 or len(samples[0]) != 2:
        return None

    durs, runs = np.array(samples).T
    if not np.any(durs) or not np.any(runs):
        return None

    eta = None
    try:
        # Weighted average of the overall slope and the most recent slope
        slope = np.mean(runs) / np.mean(durs)
        eta = slope * audio_duration
        if len(samples) > 1:
            last_slope = runs[-1] / durs[-1]
            last_eta = last_slope * audio_duration
            eta = 0.7 * eta + 0.3 * last_eta  # Weight recent performance more
    except (np.linalg.LinAlgError, ZeroDivisionError):
        return None

    return eta if eta and eta > 0 else None


# --- File and Media Utilities ---

def get_safe_filename(name: str) -> str:
    """Sanitizes a string to be a safe filename."""
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    return safe_name.replace(' ', '_')


def get_media_duration(media_path: Path) -> float:
    """Returns the duration of a media file in seconds."""
    try:
        probe = ffmpeg.probe(str(media_path))
        return float(probe.get('format', {}).get('duration', 0))
    except Exception as e:
        logger.warning(f"Could not get media duration for {media_path.name}: {e}")
        return 0.0 


def is_nonempty_text_file(path: Path) -> bool:
    """Returns True if path exists, is a file, and has non-whitespace content.

    Uses a small read to avoid loading huge files into memory.
    """
    try:
        if not path.exists() or not path.is_file():
            return False
        # quick size check
        if path.stat().st_size == 0:
            return False
        with path.open('rb') as f:
            chunk = f.read(4096)
        # try to decode safely and check for any non-whitespace
        text = chunk.decode('utf-8', errors='ignore')
        return any(not c.isspace() for c in text)
    except Exception:
        return False