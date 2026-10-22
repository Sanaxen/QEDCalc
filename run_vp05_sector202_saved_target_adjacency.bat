@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_saved_target_adjacency
exit /b %ERRORLEVEL%
