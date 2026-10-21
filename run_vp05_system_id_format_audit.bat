@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_system_id_format_audit %*
exit /b %ERRORLEVEL%
