@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_c_retention_probe
exit /b %errorlevel%
