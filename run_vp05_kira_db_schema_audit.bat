@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_kira_db_schema_audit
exit /b %ERRORLEVEL%
