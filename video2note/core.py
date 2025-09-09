"""
Core application logic for Video2Note.

This module is UI-agnostic and can be used as a library.
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config import TranscriptionConfig
from .transcriber import prepare_audio_source, run_whisper_transcription
from .utils import (calculate_eta, get_media_duration, get_run_signature,
                    load_hist, save_hist)

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Dataclass to hold the results of a transcription."""
    transcription: str
    source_file: Path
    output_file: Path
    duration: float
    elapsed_time: float


def run_pipeline(
    input_file: Path,
    config: TranscriptionConfig,
    temp_dir: Path,
    output_path: Path,
    delete_temp: bool,
) -> TranscriptionResult:
    """
    Processes a single media file through the full transcription pipeline.

    Args:
        input_file: Path to the source media file.
        config: The transcription configuration.
        temp_dir: Directory for temporary files.
        output_path: The file path to save the transcription to.
        delete_temp: Whether to delete the temporary audio file.

    Returns:
        A TranscriptionResult object containing the outcome.
    """
    logger.info(f"Начало обработки: {input_file.name}")

    audio_source = prepare_audio_source(input_file, temp_dir)
    try:
        audio_duration = get_media_duration(audio_source)
        eta = calculate_eta(config, audio_duration)

        transcription, elapsed = run_whisper_transcription(audio_source, config, eta)

        # Update history
        if audio_duration > 0:
            hist = load_hist()
            sig = get_run_signature(config)
            hist[sig].append([audio_duration, elapsed])
            hist[sig] = hist[sig][-30:]  # Keep last 30 entries
            save_hist(hist)

        # Save result
        output_path.write_text(transcription, encoding='utf-8')
        logger.info(f"Результат сохранён: {output_path}")

        return TranscriptionResult(
            transcription=transcription,
            source_file=input_file,
            output_file=output_path,
            duration=audio_duration,
            elapsed_time=elapsed,
        )
    finally:
        # Cleanup
        if audio_source != input_file and delete_temp:
            logger.debug(f"Удаляю временный файл: {audio_source.name}")
            audio_source.unlink(missing_ok=True) 