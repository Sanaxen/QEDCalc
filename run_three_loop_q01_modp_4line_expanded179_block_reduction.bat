@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python examples\three_loop_q01_modp_4line_expanded179_block_reduction.py
if errorlevel 1 exit /b %errorlevel%
endlocal
