@echo off
setlocal
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe examples\phase24_crossed_raw_q_kernel_trial.py
) else (
  python examples\phase24_crossed_raw_q_kernel_trial.py
)
endlocal
