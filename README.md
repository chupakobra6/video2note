# 🇷🇺 Video2Note (на базе whisper.cpp)

> Быстрый и точный CLI-инструмент для транскрибации аудио/видео с помощью whisper.cpp. Работает на macOS и Windows.

## Установка

### 1. Клонирование репозитория

Репозиторий включает `whisper.cpp` как сабмодуль. Клонируйте его правильно:
```bash
git clone --recurse-submodules https://github.com/YourUsername/video2note.git
cd video2note

# Если вы уже клонировали без флага --recurse-submodules:
git submodule update --init --recursive
```

### 2. Настройка окружения (macOS)

> **macOS является основной платформой для разработки.**

**A. Установите инструменты через Homebrew:**
```bash
brew install python ffmpeg cmake
```

**B. Создайте виртуальное окружение и установите зависимости:**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```
> 💡 **Совет:** После установки вы можете выйти из окружения (`deactivate`). Скрипты запуска (`./run`) автоматически найдут и используют `.venv`.

**C. Соберите `whisper.cpp`:**
```bash
cd whisper.cpp
make -j
cd ..
```

**D. Скачайте модели транскрибации:**
```bash
cd whisper.cpp/models
# Скачайте основную модель (например, large-v3)
./download-ggml-model.sh large-v3
# (Опционально) Скачайте модель для детекции голоса (VAD) для лучшего разбиения на сегменты
./download-vad-model.sh
cd ../..
```

### 3. Настройка окружения (Windows)

**A. Установите инструменты:**
- [Python 3](https://www.python.org/downloads/) (убедитесь, что `py` есть в PATH)
- [ffmpeg](https://ffmpeg.org/download.html) (добавьте в PATH)
- [CMake](https://cmake.org/download/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (выберите "C++ build tools")

**B. Создайте виртуальное окружение и установите зависимости (в PowerShell):**
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
```

**C. Соберите `whisper.cpp` (в `x64 Native Tools Command Prompt for VS`):**
```cmd
cd whisper.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
cd ..
```

**D. Скачайте модели транскрибации:**
```cmd
cd whisper.cpp\models
download-ggml-model.cmd large-v3
rem (Опционально) VAD модель
download-vad-model.cmd
cd ..\..
```

## Использование

Скрипты запуска автоматически используют ваше виртуальное окружение (`.venv`).

- **macOS/Linux:**
  ```bash
  ./run [ПАРАМЕТРЫ] [ФАЙЛЫ...]
  ```
- **Windows (CMD):**
  ```cmd
  run.bat [ПАРАМЕТРЫ] [ФАЙЛЫ...]
  ```
- **Windows (PowerShell):**
  ```powershell
  .\run.ps1 [ПАРАМЕТРЫ] [ФАЙЛЫ...]
  ```

> 💬 Если файлы не указаны в командной строке, откроется системный диалог для выбора файлов.

### Примеры

- Транскрибировать файл с русским языком, используя 8 потоков CPU:
  ```bash
  ./run -m large-v3 -l ru --threads 8 my_video.mp4
  ```
- Транскрибировать несколько файлов с моделью `medium`:
  ```bash
  ./run -m medium lecture.mp3 meeting.m4a
  ```

### Результат

Готовые текстовые файлы сохраняются в директорию `transcripts/`.

---
<br>

# 🇬🇧 Video2Note (whisper.cpp based)

> A fast and accurate CLI tool to transcribe audio/video using whisper.cpp. Works on macOS and Windows.

## Setup

### 1. Clone the Repository

This repository includes `whisper.cpp` as a submodule. Clone it correctly:
```bash
git clone --recurse-submodules https://github.com/YourUsername/video2note.git
cd video2note

# If you already cloned without the --recurse-submodules flag:
git submodule update --init --recursive
```

### 2. Environment Setup (macOS)

> **macOS is the primary development platform.**

**A. Install Tools with Homebrew:**
```bash
brew install python ffmpeg cmake
```

**B. Create a Virtual Environment and Install Dependencies:**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```
> 💡 **Tip:** You can `deactivate` the environment after setup. The runner scripts (`./run`) will automatically find and use the `.venv`.

**C. Build `whisper.cpp`:**
```bash
cd whisper.cpp
make -j
cd ..
```

**D. Download Transcription Models:**
```bash
cd whisper.cpp/models
# Download a primary model (e.g., large-v3)
./download-ggml-model.sh large-v3
# (Optional) Download a Voice Activity Detection (VAD) model for better segmentation
./download-vad-model.sh
cd ../..
```

### 3. Environment Setup (Windows)

**A. Install Tools:**
- [Python 3](https://www.python.org/downloads/) (ensure `py` is in your PATH)
- [ffmpeg](https://ffmpeg.org/download.html) (add to PATH)
- [CMake](https://cmake.org/download/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (select "C++ build tools")

**B. Create a Virtual Environment and Install Dependencies (in PowerShell):**
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
```

**C. Build `whisper.cpp` (in `x64 Native Tools Command Prompt for VS`):**
```cmd
cd whisper.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
cd ..
```

**D. Download Transcription Models:**
```cmd
cd whisper.cpp\models
download-ggml-model.cmd large-v3
rem (Optional) VAD model
download-vad-model.cmd
cd ..\..
```

## Usage

The launcher scripts automatically use your project's virtual environment (`.venv`).

- **macOS/Linux:**
  ```bash
  ./run [OPTIONS] [FILES...]
  ```
- **Windows (CMD):**
  ```cmd
  run.bat [OPTIONS] [FILES...]
  ```
- **Windows (PowerShell):**
  ```powershell
  .\run.ps1 [OPTIONS] [FILES...]
  ```

> 💬 If no files are provided in the command line, a native file picker dialog will open.

### Examples

- Transcribe a Russian file using 8 CPU threads:
  ```bash
  ./run -m large-v3 -l ru --threads 8 my_video.mp4
  ```
- Transcribe multiple files with the `medium` model:
  ```bash
  ./run -m medium lecture.mp3 meeting.m4a
  ```

### Output

Completed transcripts are saved to the `transcripts/` directory.


