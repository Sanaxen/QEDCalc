@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_full_stage_capsule_audit %*
exit /b %ERRORLEVEL%
