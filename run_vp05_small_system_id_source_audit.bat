@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_small_system_id_source_audit
exit /b %ERRORLEVEL%
