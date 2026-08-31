@echo off
setlocal
cd /d "%~dp0"
python examples\three_loop_q01_modp_4line_all_higher_sector_rank.py
if errorlevel 1 exit /b 1
endlocal
