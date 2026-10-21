@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_raw_integer_id_audit %*
exit /b %ERRORLEVEL%
