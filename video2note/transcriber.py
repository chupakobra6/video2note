"""
Core transcription logic for Video2Note.
"""
import logging
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, Tuple

from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import TranscriptionConfig
from .exceptions import FfmpegError, WhisperCppError
from .ui import ElapsedETAColumn, console
from .utils import get_safe_filename

logger = logging.getLogger(__name__)


def convert_to_standard_audio(input_path: Path, output_path: Path) -> None:
    """
    Converts any media file to a 16kHz mono FLAC file using ffmpeg.
    """
    logger.info(f"Конвертирую {input_path.name} в стандартный аудиоформат (FLAC 16kHz mono)...")
    cmd = [
        'ffmpeg', '-i', str(input_path), '-vn', '-c:a', 'flac',
        '-ar', '16000', '-ac', '1',
        # gentle EQ only, keep all silence
        '-af', 'volume=1.5,highpass=f=80,lowpass=f=8000',
        '-y', str(output_path)
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=False, check=True, timeout=600)
        try:
            logger.debug(proc.stderr.decode('utf-8', errors='ignore'))
        except Exception:
            pass
        logger.info(f"Аудио готово: {output_path.name}")
    except subprocess.TimeoutExpired as e:
        raise FfmpegError("Время ожидания истекло. Файл может быть слишком большим или поврежден.") from e
    except subprocess.CalledProcessError as e:
        raise FfmpegError(f"Ошибка конвертации аудио (ffmpeg):\n{e.stderr}") from e


def prepare_audio_source(input_file: Path, temp_dir: Path) -> Path:
    """
    Ensures an audio file is ready for transcription by converting it
    to a standardized temporary FLAC file.
    """
    safe_stem = get_safe_filename(input_file.stem)
    temp_audio_path = temp_dir / f"{safe_stem}_audio.flac"

    if temp_audio_path.exists():
        try:
            if temp_audio_path.stat().st_mtime >= input_file.stat().st_mtime and temp_audio_path.stat().st_size > 1024:
                logger.info(f"Кэш аудио актуален: {temp_audio_path.name}")
                return temp_audio_path
        except OSError:
            pass

    convert_to_standard_audio(input_file, temp_audio_path)
    return temp_audio_path


def run_whisper_transcription(audio_path: Path, config: TranscriptionConfig, eta: Optional[float]) -> Tuple[str, float]:
    """
    Executes the whisper.cpp process to transcribe the given audio file.
    """
    logger.info(f"Запуск whisper.cpp с моделью {config.model_path.name}...")

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
        output_file = Path(tmp.name)
    
    output_prefix = str(output_file.with_suffix(''))

    try:
        # Build whisper.cpp command with conditional VAD support
        cmd = [
            str(config.whisper_bin), "--model", str(config.model_path),
            "--file", str(audio_path), "--language", config.language,
            "--threads", str(config.threads),
        ]

        # Try to enable VAD only if a VAD model is available
        vad_model_candidates = [
            config.models_dir / "ggml-silero-v5.1.2.bin",
            config.models_dir / "for-tests-silero-v5.1.2-ggml.bin",
        ]
        if config.models_dir.exists():
            try:
                for p in config.models_dir.glob("*silero*ggml*.bin"):
                    vad_model_candidates.append(p)
                for p in config.models_dir.glob("*vad*.bin"):
                    vad_model_candidates.append(p)
            except OSError:
                pass

        vad_model_path = next((p for p in vad_model_candidates if p.exists()), None)
        if vad_model_path:
            cmd += ["--vad", "--vad-model", str(vad_model_path)]
        else:
            logger.info("VAD модель не найдена в каталоге моделей whisper.cpp — продолжаю без --vad.")

        # General decoding and segmentation controls
        cmd += [
            # more sensitive to quiet speech even without VAD
            "--no-speech-thold", "0.6",
            # allow longer segments for coherence
            "--max-len", "100",
            # re-enable limited context to stabilize decoding
            "--max-context", "32",
            # balanced decoding parameters
            "--beam-size", "5", "--best-of", "5", "--temperature", "0.5",
            # entropy threshold near default
            "--entropy-thold", "2.4",
            # keep other thresholds and outputs
            "--logprob-thold", "-1.0", "--output-txt",
            "--output-file", output_prefix, "--no-prints",
        ]

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), ElapsedETAColumn(eta), console=console) as progress:
            progress.add_task("🗣️  Транскрибирую...", total=None)
            start_time = time.perf_counter()
            proc = subprocess.run(cmd, capture_output=True, text=False, check=True, timeout=3600)
            try:
                logger.debug(proc.stderr.decode('utf-8', errors='ignore'))
            except Exception:
                pass
            elapsed = time.perf_counter() - start_time

        try:
            transcription_bytes = output_file.read_bytes()
            transcription = transcription_bytes.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            logger.warning(f"Не удалось прочитать файл транскрипции как UTF-8: {e}")
            transcription = ""
        if not transcription:
            logger.warning("Получена пустая транскрипция. Проверьте исходный файл.")

        return transcription, elapsed

    except subprocess.TimeoutExpired as e:
        raise WhisperCppError("Время ожидания истекло. Файл может быть слишком длинным.") from e
    except subprocess.CalledProcessError as e:
        raise WhisperCppError(f"Ошибка выполнения whisper.cpp:\n{e.stderr}") from e
    finally:
        if output_file.exists():
            output_file.unlink(missing_ok=True) 