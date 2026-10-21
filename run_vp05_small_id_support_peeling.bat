@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_small_id_support_peeling %*
exit /b %ERRORLEVEL%
