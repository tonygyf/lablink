@echo off
setlocal
set "LABLINK_PYTHON=%LOCALAPPDATA%\LabLink\venv\Scripts\python.exe"
if not exist "%LABLINK_PYTHON%" (
  echo Run scripts\install.ps1 first.
  exit /b 1
)
"%LABLINK_PYTHON%" -m lablink %*
exit /b %ERRORLEVEL%
