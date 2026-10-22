import json
from pathlib import Path
import pytest
import sympy as sp
from three_loop.vp05_verified_reduction import (
    TARGET, MASTER_6, MASTER_5, load_verified_vp05_rule, reduce_if_verified,
)
EQUATION=("z*VP05_full[1,1,0,1,0,0,1,1,0,0,0,0] - "
"2*VP05_full[1,1,-1,1,0,0,1,1,0,0,0,0] + "
"2*VP05_full[1,0,0,1,0,0,1,1,0,0,0,0] = 0")
CHECKS=("exact_400_columns","all_166_lineage_exact","raw_kira_system_replay",
"hashes_match","preferred_input_matches_saved","target_keys_present",
"preferred_job_reference")
def payload():
    return {"status":"EXACT_SAVED_KIRA_PROJECT_REDUCTION",
        "checks":{k:True for k in CHECKS},
        "target":{"key":[10,203],"exponents":list(TARGET)},
        "right_hand_side":[
            {"key":[6,203],"exponents":list(MASTER_6),"coefficient":"2/z"},
            {"key":[5,201],"exponents":list(MASTER_5),"coefficient":"-2/z"}],
        "equation":EQUATION,
        "historical_kira_binary_version_verified":False,
        "diagram_momentum_routing_independently_verified":False}
def write(tmp_path,data):
    f=tmp_path/"attestation.json";f.write_text(json.dumps(data));return f
def test_opt_in_verified_reduction(tmp_path):
    f=write(tmp_path,payload())
    terms=reduce_if_verified("VP05_full",TARGET,f)
    z=sp.Symbol("z")
    assert terms==((MASTER_6,2/z),(MASTER_5,-2/z))
    assert sp.cancel(z*terms[0][1]-2)==0
    assert sp.cancel(z*terms[1][1]+2)==0
def test_other_target_never_uses_rule(tmp_path):
    missing=tmp_path/"not_present.json"
    assert reduce_if_verified("VP05_full",(0,)*12,missing) is None
    assert reduce_if_verified("other",TARGET,missing) is None
@pytest.mark.parametrize("field,value",[
    ("status","SAMPLES_ONLY"),("equation","false"),("historical_kira_binary_version_verified",True)])
def test_corrupt_metadata_rejected(tmp_path,field,value):
    d=payload();d[field]=value
    with pytest.raises(ValueError):load_verified_vp05_rule(write(tmp_path,d))
def test_missing_proof_check_rejected(tmp_path):
    d=payload();d["checks"]["all_166_lineage_exact"]=False
    with pytest.raises(ValueError):load_verified_vp05_rule(write(tmp_path,d))
def test_changed_terms_rejected(tmp_path):
    d=payload();d["right_hand_side"][1]["coefficient"]="+2/z"
    with pytest.raises(ValueError):load_verified_vp05_rule(write(tmp_path,d))
