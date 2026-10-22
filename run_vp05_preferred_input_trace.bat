@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_preferred_input_trace
exit /b %ERRORLEVEL%
