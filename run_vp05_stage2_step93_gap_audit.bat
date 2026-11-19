@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_stage2_step93_gap_audit
exit /b %ERRORLEVEL%
