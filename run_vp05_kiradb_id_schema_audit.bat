@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_kiradb_id_schema_audit
exit /b %ERRORLEVEL%
