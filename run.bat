@echo off
setlocal enabledelayedexpansion
REM Windows launcher: prefer .venv\Scripts\python.exe, then pyenv

set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

set VENV_PY=%SCRIPT_DIR%\.venv\Scripts\python.exe
if exist "%VENV_PY%" (
  "%VENV_PY%" "%SCRIPT_DIR%\main.py" %*
  exit /b %ERRORLEVEL%
)

REM Try pyenv if available
where pyenv >nul 2>nul
if %ERRORLEVEL%==0 (
  for /f "usebackq tokens=*" %%i in (`pyenv which python 2^>nul`) do set PYENV_PY=%%i
  if defined PYENV_PY (
    pyenv exec python "%SCRIPT_DIR%\main.py" %*
    exit /b %ERRORLEVEL%
  )
)

echo Окружение не настроено. Создайте .venv или настройте pyenv для проекта. См. README.md.
exit /b 1

