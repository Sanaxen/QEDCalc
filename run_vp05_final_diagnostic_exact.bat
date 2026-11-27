@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_final_diagnostic_exact %*
exit /b %errorlevel%
