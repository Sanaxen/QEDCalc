@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_greedy_small_id_set
exit /b %ERRORLEVEL%
