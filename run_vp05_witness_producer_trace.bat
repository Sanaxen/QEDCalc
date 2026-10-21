@echo off
setlocal
cd /d "%~dp0"
echo [VP05] Identify producer code for original 528-row witness.
python -m examples.three_loop_sector203_witness_producer_trace
exit /b %ERRORLEVEL%
