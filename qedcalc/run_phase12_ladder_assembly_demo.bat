@echo off
setlocal
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe examples\phase12_ladder_assembly_trial.py
) else (
  python examples\phase12_ladder_assembly_trial.py
)
endlocal
