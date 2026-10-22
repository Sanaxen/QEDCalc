"""Integration tests for opt-in VP05 rule in the master coefficient resolver."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
import sympy as sp
import three_loop.master_coefficient_api as api
from three_loop.vp05_verified_reduction import TARGET,MASTER_6,MASTER_5

EQUATION=("z*VP05_full[1,1,0,1,0,0,1,1,0,0,0,0] - "
"2*VP05_full[1,1,-1,1,0,0,1,1,0,0,0,0] + "
"2*VP05_full[1,0,0,1,0,0,1,1,0,0,0,0] = 0")
class FakeBackend:
    def self_test(self):pass
    def canonical_sum(self,parts,progress=None):
        val=sp.cancel(sum(parts,sp.Integer(0)))
        return sp.sstr(val),tuple(sorted(str(x) for x in val.free_symbols))
def fixture(tmp_path):
    checks={k:True for k in ("exact_400_columns","all_166_lineage_exact",
        "raw_kira_system_replay","hashes_match","preferred_input_matches_saved",
        "target_keys_present","preferred_job_reference")}
    obj={"status":"EXACT_SAVED_KIRA_PROJECT_REDUCTION","checks":checks,
        "target":{"key":[10,203],"exponents":list(TARGET)},
        "right_hand_side":[
            {"key":[6,203],"exponents":list(MASTER_6),"coefficient":"2/z"},
            {"key":[5,201],"exponents":list(MASTER_5),"coefficient":"-2/z"}],
        "equation":EQUATION,"historical_kira_binary_version_verified":False,
        "diagram_momentum_routing_independently_verified":False}
    f=tmp_path/"verified.json";f.write_text(json.dumps(obj));return f
def run(monkeypatch,path=None,masters=None,rules=None,family="VP05_full"):
    monkeypatch.setattr(api,"load_reduction_graph",
        lambda *args:(set(masters if masters is not None else [MASTER_6,MASTER_5]),
                     dict(rules or {}),set()))
    def bridge(_):
        return SimpleNamespace(terms=[SimpleNamespace(kira_indices=TARGET,coefficient=sp.Integer(1))])
    conf=api.MasterCoefficientConfig(family=family,form_export=Path("unused"),
        masters_file=Path("unused"),final_basis=frozenset([MASTER_6,MASTER_5]),
        verified_vp05_artifact=path)
    return api.synthesize_master_coefficients([(TARGET,sp.Integer(1))],
        bridge,conf,progress=None,backend=FakeBackend())
def test_integrated_opt_in(monkeypatch,tmp_path):
    res=run(monkeypatch,fixture(tmp_path))
    assert res.passed
    got={r.indices:sp.sympify(r.coefficient) for r in res.rows}
    z=sp.Symbol("z")
    assert sp.cancel(got[MASTER_6]-2/z)==0
    assert sp.cancel(got[MASTER_5]+2/z)==0
def test_default_does_not_apply(monkeypatch):
    res=run(monkeypatch)
    assert not res.passed
    assert res.unresolved_integrals==(TARGET,)
def test_reject_conflicting_rule(monkeypatch,tmp_path):
    with pytest.raises(RuntimeError,match="conflicts"):
        run(monkeypatch,fixture(tmp_path),rules={TARGET:((sp.Integer(1),MASTER_6),)})
def test_reject_unverified_artifact(monkeypatch,tmp_path):
    missing=tmp_path/"missing.json"
    with pytest.raises(FileNotFoundError):run(monkeypatch,missing)
def test_reject_other_family(monkeypatch,tmp_path):
    with pytest.raises(ValueError,match="only"):
        run(monkeypatch,fixture(tmp_path),family="Q01")
