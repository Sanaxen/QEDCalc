@echo off
setlocal
cd /d "%~dp0"
echo [VP05] Replay 528 original witness rows against correct L2 2678-equation SYSTEM source.
python -m examples.three_loop_sector203_original_raw_system_exact_replay
exit /b %ERRORLEVEL%
