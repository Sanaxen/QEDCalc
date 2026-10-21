@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_exact_target_engine %*
exit /b %ERRORLEVEL%
