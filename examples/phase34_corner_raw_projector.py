from qedcalc.operations.corner import corner_raw_projector_polynomials
r=corner_raw_projector_polynomials()
print('Phase-34 corner raw magnetic projector')
print('term counts:',r.term_counts)
print('diagram4 base nonzero:',r.diagram4_base!=0,'transverse q0 nonzero:',r.diagram4_transverse_zero!=0)
print('diagram5 base nonzero:',r.diagram5_base!=0,'transverse q0 nonzero:',r.diagram5_transverse_zero!=0)
print('Phase-34 corner raw magnetic projector: PASS')
