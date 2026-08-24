@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
"%PY%" examples\phase36_corner_renormalized_inner_vertex_bridge.py
exit /b %ERRORLEVEL%
