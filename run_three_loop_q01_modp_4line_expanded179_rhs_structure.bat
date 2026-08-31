@echo off
setlocal
cd /d %~dp0
set PYTHONPATH=%CD%;%PYTHONPATH%
python examples\three_loop_q01_modp_4line_expanded179_rhs_structure.py
endlocal
