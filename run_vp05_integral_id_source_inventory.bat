@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_integral_id_source_inventory %*
exit /b %ERRORLEVEL%
