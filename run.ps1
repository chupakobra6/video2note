#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Windows PowerShell launcher: prefer .venv, then pyenv
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

$venvPy = Join-Path $ScriptDir '.venv\Scripts\python.exe'
if (Test-Path $venvPy) {
  & $venvPy "$ScriptDir\main.py" @args
  exit $LASTEXITCODE
}

# pyenv (if installed)
if (Get-Command pyenv -ErrorAction SilentlyContinue) {
  try {
    $pyenvPy = (& pyenv which python) 2>$null
    if ($pyenvPy) {
      & pyenv exec python "$ScriptDir\main.py" @args
      exit $LASTEXITCODE
    }
  } catch {}
}

Write-Error "Окружение не настроено. Создайте .venv или настройте pyenv для проекта. См. README.md."
exit 1

