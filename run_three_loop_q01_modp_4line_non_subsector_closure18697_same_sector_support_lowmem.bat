@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "QEDCALC_PROCESSES=1"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\three_loop_q01_modp_4line_non_subsector_closure18697_same_sector_support_lowmem.py
) else (
  python examples\three_loop_q01_modp_4line_non_subsector_closure18697_same_sector_support_lowmem.py
)
endlocal
