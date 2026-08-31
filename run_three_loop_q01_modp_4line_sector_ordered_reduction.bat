@echo off
setlocal
cd /d %~dp0
set PYTHONPATH=%CD%;%PYTHONPATH%
python examples\three_loop_q01_modp_4line_sector_ordered_reduction.py
endlocal
