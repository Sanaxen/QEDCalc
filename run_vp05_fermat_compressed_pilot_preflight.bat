@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_fermat_gaussian_pilot --equations "output\three_loop_integral_family_audit\vp05_target_symbolic_compressed.equations.json" --rows 166 --max-rows 166 --max-array-cells 32000 --preflight-only --verify-last-rows 1 --analyze-row-lifetimes --sparse-array-rows --packed-sparse-maps --reuse-packed-maps --loop-control-rows --prune-dead-rows --prune-eliminated-pivots --auto-points %*
exit /b %ERRORLEVEL%
