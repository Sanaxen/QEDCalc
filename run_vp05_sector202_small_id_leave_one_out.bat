@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_small_id_leave_one_out
exit /b %ERRORLEVEL%
