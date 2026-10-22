@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_all_system_target_search
exit /b %ERRORLEVEL%
