@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_saved_project_api_smoke
exit /b %ERRORLEVEL%
