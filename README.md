## Video2Note (whisper.cpp)

Fast, accurate CLI tool to transcribe audio/video using whisper.cpp. Works on macOS and Windows.

### Clone with submodules
```
git clone --recurse-submodules <repo-url>
cd video2note
# If you already cloned without submodules:
git submodule update --init --recursive
```

### Prerequisites
- Python 3.10+
- ffmpeg in PATH
- A virtual environment in the project (`.venv`) or pyenv configured

### Setup on macOS (primary)
1) Install tools
```
brew install python ffmpeg cmake
```
2) Create and activate virtualenv
```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip wheel setuptools
python -m pip install -r requirements.txt
```
3) Build whisper.cpp
```
cd whisper.cpp
make -j
cd -
```
4) Download model(s)
```
cd whisper.cpp/models
./download-ggml-model.sh large-v3
# optional VAD model
./download-vad-model.sh
cd -
```

### Setup on Windows
1) Install tools: Python 3, ffmpeg (add to PATH), CMake, Visual Studio Build Tools
2) Create and activate virtualenv (PowerShell)
```
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip wheel setuptools
python -m pip install -r requirements.txt
```
3) Build whisper.cpp (x64 Native Tools Command Prompt for VS)
```
cd whisper.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
cd ..
```
4) Download model(s)
```
cd whisper.cpp\models
download-ggml-model.cmd large-v3
rem optional VAD model
download-vad-model.cmd
cd ..\..
```
- Windows (x64 Native Tools Command Prompt for VS):
```
cd whisper.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

#### Download models
From `whisper.cpp/models`:
- macOS/Linux: `./download-ggml-model.sh large-v3`
- Windows: `download-ggml-model.cmd large-v3`
Optionally VAD model: `download-vad-model.(sh|cmd)`

### Run
- macOS/Linux: `./run [options] [files]`
- Windows (cmd): `run.bat [options] [files]`
- Windows (PowerShell): `./run.ps1 [options] [files]`

Note: launchers require `.venv` or pyenv for this project. They do not fall back to system Python.

### Usage examples
```
./run -m large-v3 -l ru --threads 8 file1.mp3 file2.mp4
```
If no files are provided, a file picker opens.

### Output
Transcripts are saved to `transcripts/NAME.txt` next to the app.

### Troubleshooting
- whisper.cpp executable not found: ensure you built it (see above).
- Model not found: run model download scripts in `whisper.cpp/models`.
- ffmpeg not found: install and ensure it is in PATH.


