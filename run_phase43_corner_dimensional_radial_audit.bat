@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
set "PYTHONPATH=%CD%"
"%PY%" examples\phase43_corner_dimensional_radial_audit.py
exit /b %ERRORLEVEL%
