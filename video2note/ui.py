"""
User interface elements for Video2Note, including Rich components and GUI dialogs.
"""
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import ProgressColumn, Task
from rich.text import Text

# Rich Console and Logger
console = Console()
rich_handler = RichHandler(markup=True, rich_tracebacks=True, show_path=False)


class ElapsedETAColumn(ProgressColumn):
    """Custom Rich progress column showing 'elapsed / total_eta'."""
    def __init__(self, eta: Optional[float]):
        super().__init__()
        self.eta = eta

    def render(self, task: "Task") -> Text:
        """Render the column."""
        elapsed_str = time.strftime('%M:%S', time.gmtime(task.elapsed or 0))
        if self.eta:
            eta_str = time.strftime('%M:%S', time.gmtime(self.eta))
            return Text(f"{elapsed_str} / {eta_str}", style="progress.elapsed")
        return Text(elapsed_str, style="progress.elapsed")


def _open_file_dialog_macos() -> Optional[list[Path]]:
    """Opens a native file selection dialog on macOS."""
    try:
        cmd = '''
            try
                set chosen_files to choose file with prompt "Выберите один или несколько аудио/видео файлов" with multiple selections allowed
                set posix_paths to {}
                repeat with a_file in chosen_files
                    set end of posix_paths to POSIX path of a_file
                end repeat
                set {oldDelims, AppleScript's text item delimiters} to {AppleScript's text item delimiters, linefeed}
                set joined to posix_paths as text
                set AppleScript's text item delimiters to oldDelims
                return joined
            on error number -128
                return ""
            end try
        '''
        path_str = subprocess.run(
            ["osascript", "-e", cmd],
            capture_output=True, text=True, timeout=300, check=True
        ).stdout.strip()
        return [Path(p) for p in path_str.splitlines() if p] if path_str else None
    except Exception as e:
        console.print(f"[yellow]Не удалось открыть нативный диалог выбора файла: {e}[/yellow]")
        return None


def _open_file_dialog_fallback() -> Optional[list[Path]]:
    """Opens a fallback file selection dialog using tkinter."""
    try:
        import tkinter
        from tkinter import filedialog
        root = tkinter.Tk()
        root.withdraw()  # Hide the main window
        filepaths = filedialog.askopenfilenames(
            title="Выберите один или несколько аудио/видео файлов"
        )
        return [Path(p) for p in filepaths] if filepaths else None
    except ImportError:
        console.print("[red]Ошибка: для отображения диалога выбора файла требуется библиотека Tkinter.[/red]")
        return None
    except Exception as e:
        console.print(f"[yellow]Не удалось открыть диалог выбора файла: {e}[/yellow]")
        return None


def open_file_dialog() -> Optional[list[Path]]:
    """
    Opens a native file selection dialog, with a fallback for non-macOS systems.
    Returns a list of selected paths or None.
    """
    # Do not open GUI dialogs in CI/SSH environments
    if os.getenv("CI") or os.getenv("SSH_TTY"):
        return None

    console.print("📁 Открываю диалог выбора файла (можно выбрать несколько)...")
    
    if platform.system() == "Darwin":
        return _open_file_dialog_macos()
    else:
        return _open_file_dialog_fallback() 