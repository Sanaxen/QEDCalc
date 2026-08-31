@echo off
setlocal
cd /d %~dp0
set PYTHONPATH=%CD%
python examples\three_loop_q01_modp_4line_sector_ordered_rhs_structure.py
if errorlevel 1 exit /b 1
endlocal
