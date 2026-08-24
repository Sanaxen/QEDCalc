from qedcalc.operations.corner import corner_raw_pair_audit
r=corner_raw_pair_audit()
print('Phase-32 corner raw pair bridge')
for d in (r.diagram4,r.diagram5):
    print('diagram',d.diagram,'labels=',d.electron_labels,'q0 powers=',d.q0_denominator_powers,'inner side=',d.inner_vertex_side,'inner props=',d.inner_vertex_propagators)
print('renormalized template:',r.renormalized_outer_template)
print('Phase-32 corner raw pair bridge: PASS')
