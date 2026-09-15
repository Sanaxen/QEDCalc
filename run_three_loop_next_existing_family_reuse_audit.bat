@echo off
setlocal
cd /d %~dp0
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe -m examples.three_loop_next_existing_family_reuse_audit
) else (
  python -m examples.three_loop_next_existing_family_reuse_audit
)
if errorlevel 1 exit /b %errorlevel%
endlocal
