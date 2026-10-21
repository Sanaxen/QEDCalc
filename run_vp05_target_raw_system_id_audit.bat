@echo off
setlocal
cd /d "%~dp0"
echo [VP05] Trace small target IDs to saved Kira SYSTEM records.
python -m examples.three_loop_sector203_target_raw_system_id_audit
exit /b %ERRORLEVEL%
