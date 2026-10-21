@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_single_nonmaster_guard_review %*
exit /b %ERRORLEVEL%
