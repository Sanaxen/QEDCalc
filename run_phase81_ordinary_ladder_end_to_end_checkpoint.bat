@echo off
setlocal
cd /d %~dp0
set PYTHONPATH=%CD%
python examples\phase81_ordinary_ladder_end_to_end_checkpoint.py
endlocal
