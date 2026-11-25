@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_subsector_truncate_batch %*
exit /b %errorlevel%
