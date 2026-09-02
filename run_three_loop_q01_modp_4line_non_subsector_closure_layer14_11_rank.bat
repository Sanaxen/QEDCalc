@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\three_loop_q01_modp_4line_non_subsector_closure_layer14_11_rank.py
) else (
  python examples\three_loop_q01_modp_4line_non_subsector_closure_layer14_11_rank.py
)
endlocal
