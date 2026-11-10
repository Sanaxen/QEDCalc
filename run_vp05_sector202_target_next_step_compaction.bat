@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_target_next_step_compaction %*
exit /b %ERRORLEVEL%
