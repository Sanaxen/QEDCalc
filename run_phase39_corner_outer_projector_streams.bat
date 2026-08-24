@echo off
setlocal
cd /d %~dp0
set PYTHONPATH=%CD%
python -c "from qedcalc.operations.corner import *; s=corner_outer_projector_streams(); print('Phase-39 corner finite-inner -> outer projector streams'); print('term counts:', s.term_counts); r=corner_outer_stream_denominator_residuals(); print('denominator residuals:', r); assert all(x==0 for x in r.values()); print('Phase-39: PASS')"
endlocal
