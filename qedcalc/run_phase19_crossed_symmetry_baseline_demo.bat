@echo off
setlocal
cd /d %~dp0
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe examples\phase19_crossed_symmetry_baseline_trial.py
) else (
  python examples\phase19_crossed_symmetry_baseline_trial.py
)
endlocal
