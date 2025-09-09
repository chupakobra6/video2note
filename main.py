#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Video2Note - Быстрая и качественная транскрипция через whisper.cpp
Оптимизирован для максимальной производительности и точности на macOS.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Iterable, Optional

import click
from rich.markup import escape
from rich.panel import Panel

from video2note.config import (ALL_SUPPORTED_FORMATS, TEMP_DIR_NAME,
                               TRANSCRIPTS_DIR_NAME, TranscriptionConfig)
from video2note.core import run_pipeline
from video2note.exceptions import Video2NoteError
from video2note.ui import console, open_file_dialog, rich_handler
from video2note.utils import get_safe_filename, is_nonempty_text_file

# --- Logging Configuration ---
# Set up a logger for the application.
# By default, the handler only shows warnings and above.
# The logger itself is set to DEBUG to capture all levels.
logger = logging.getLogger("video2note")
logger.setLevel(logging.DEBUG)  # Capture all messages
rich_handler.setLevel(logging.WARNING)  # Default console output level
logger.addHandler(rich_handler)


# --- UI Layer ---

def show_intro(files: list[Path], config: TranscriptionConfig):
    """Displays the initial configuration panel."""
    file_list = "\n".join(f"- [green]{f.name}[/green]" for f in files)
    panel_content = (
        f"📄 [bold]Файлы для обработки:[/bold]\n{file_list}\n"
        f"🎯 [bold]Модель:[/bold] [cyan]{config.model_path.name}[/cyan]\n"
        f"🗣️  [bold]Язык:[/bold] [cyan]{config.language}[/cyan]  "
        f"[bold]Потоки:[/bold] [cyan]{config.threads}[/cyan]"
    )
    console.print(Panel(panel_content, title="💿 Конфигурация", border_style="green"))


def show_summary(result):
    """Displays a summary panel for a single transcription result."""
    console.print(f"\n✅ [bold]Готово:[/bold] [link=file://{result.output_file.resolve()}]{result.output_file}[/link]")
    preview = result.transcription[:300] + "..." if len(result.transcription) > 300 else result.transcription
    console.print("\n📝 [bold]Превью:[/bold]")
    console.print(f"[italic dim]{escape(preview)}[/italic dim]")


# --- Main CLI Interface ---

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('input_files', type=click.Path(exists=True, path_type=Path), required=False, nargs=-1)
@click.option('-o', '--output', type=click.Path(path_type=Path), help='Путь для сохранения результата (для одного файла).')
@click.option('-m', '--model', default='large-v3', show_default=True, type=click.Choice(['tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3']), help='Модель whisper.cpp.')
@click.option('-l', '--language', default='ru', show_default=True, help='Язык аудио (ru, en, etc.).')
@click.option('--threads', default=os.cpu_count() or 4, show_default=True, type=int, help='Количество потоков CPU.')
@click.option('--delete-temp/--keep-temp', 'delete_temp', default=True, show_default=True, help='Удалять или сохранять временный аудиофайл.')
@click.option('--overwrite/--no-overwrite', 'overwrite', default=False, show_default=True, help='Перезаписывать существующие транскрипции.')
@click.option('-v', '--verbose', is_flag=True, help='Подробный вывод для отладки.')
def main(input_files: Iterable[Path], output: Optional[Path], model: str, language: str, threads: int, delete_temp: bool, overwrite: bool, verbose: bool):
    """Быстрая и качественная транскрипция аудио/видео файлов через whisper.cpp."""
    if verbose:
        # If verbose mode is on, show all logs from DEBUG level
        rich_handler.setLevel(logging.DEBUG)
    
    console.rule("[bold green]🚀 Video2Note (whisper.cpp)[/bold green]")

    try:
        files_to_process = list(input_files)
        if not files_to_process:
            chosen_files = open_file_dialog()
            if not chosen_files:
                console.print("❌ Файлы не выбраны."); return
            files_to_process = chosen_files

        if output and len(files_to_process) > 1:
            console.print("[yellow]Опция --output/-o используется только при обработке одного файла и будет проигнорирована.[/yellow]")
            output = None
            
        for file in files_to_process:
            if file.suffix.lower() not in ALL_SUPPORTED_FORMATS:
                console.print(f"❌ [bold red]Неподдерживаемый формат:[/bold red] {file.name} - файл пропущен.")
                continue

        config = TranscriptionConfig(model_name=model, language=language, threads=threads)
        show_intro(files_to_process, config)

        script_dir = Path(__file__).parent.resolve()
        temp_dir = script_dir / TEMP_DIR_NAME
        output_dir = script_dir / TRANSCRIPTS_DIR_NAME
        temp_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        
        for input_file in files_to_process:
            console.rule(f"[bold blue]Обработка: {input_file.name}[/bold blue]")
            output_path = output if output else output_dir / f"{get_safe_filename(input_file.stem)}.txt"

            # Skip if transcript exists and overwrite disabled
            if not overwrite and is_nonempty_text_file(output_path):
                console.print(f"[yellow]Пропуск:[/yellow] уже есть транскрипция → {output_path.name}")
                continue
            
            try:
                result = run_pipeline(input_file, config, temp_dir, output_path, delete_temp)
                show_summary(result)
            except Video2NoteError as e:
                logger.error(f"Не удалось обработать файл {input_file.name}: {e}", exc_info=verbose)
                console.print(f"❌ [bold red]Ошибка при обработке {input_file.name}:[/bold red] {escape(str(e))}")

        # --- Final Cleanup ---
        if delete_temp:
            try:
                if temp_dir.is_dir() and not any(temp_dir.iterdir()):
                    logger.info(f"Удаляю пустую временную директорию: {temp_dir.name}")
                    temp_dir.rmdir()
                    console.print(f"🧹 Временная директория {temp_dir.name} удалена.")
            except OSError as e:
                logger.warning(f"Не удалось удалить временную директорию {temp_dir.name}: {e}")

    except Video2NoteError as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=verbose)
        console.print(f"❌ [bold red]Критическая ошибка:[/bold red] {escape(str(e))}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Непредвиденная ошибка: {e}", exc_info=True)
        console.print(f"❌ [bold red]Непредвиденная ошибка:[/bold red] {escape(str(e))}")
        sys.exit(1)

    console.rule("[bold green]✅ Все задачи выполнены[/bold green]")


if __name__ == '__main__':
    main() 