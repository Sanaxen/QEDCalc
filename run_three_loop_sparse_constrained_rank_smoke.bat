@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\three_loop_sparse_constrained_rank_smoke.py
) else (
  python examples\three_loop_sparse_constrained_rank_smoke.py
)
endlocal
