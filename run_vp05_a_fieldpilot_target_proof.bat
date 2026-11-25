@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_a_fieldpilot_target_proof %*
exit /b %errorlevel%
