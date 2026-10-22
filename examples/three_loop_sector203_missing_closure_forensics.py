"""Read-only forensic inspection of VP05 unfinished whole-family closure.

This is a diagnostic; it never treats a sector-local proof as full closure.
"""
from __future__ import annotations
import json
from pathlib import Path
from three_loop.master_basis_batch import AUDIT_DIR

PREFIX="three_loop_vp05_full_masters_r8s3d0"
BASIS_SEED="r8s5d2"
MISSING=("r8s6d2","r8s5d3")

def read(path):
    try:return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError,ValueError):return {}

def main():
    closure_path=AUDIT_DIR/f"{PREFIX}_candidate_{BASIS_SEED}_closure_audit.json"
    manifest_path=AUDIT_DIR/f"{PREFIX}_candidate_{BASIS_SEED}_closure_manifest.json"
    closure=read(closure_path);manifest=read(manifest_path)
    related=[]
    for path in sorted(AUDIT_DIR.glob("*vp05*")):
        if path.suffix.lower() not in (".json",".txt"):continue
        if not any(seed in path.name for seed in MISSING):continue
        if path.suffix==".json":
            data=read(path)
            related.append({"file":path.name,"stage":data.get("stage"),"audit_pass":data.get("audit_pass"),
                "status":data.get("status"),"keys":list(data)[:35]})
        else:related.append({"file":path.name,"type":"text","size_bytes":path.stat().st_size})
    fields=("candidate_master_count","required_envelope","boundary_rows","errors",
        "stable_under_one_axis_extensions","audit_pass","candidate_masters","source_target_file")
    report={"status":"VP05_STAGE2_MISSING_CLOSURE_FORENSICS",
        "original_closure_audit":str(closure_path),"closure_present":closure_path.exists(),
        "original_closure_fields":{k:closure.get(k) for k in fields if k in closure},
        "original_manifest":str(manifest_path),"manifest_present":manifest_path.exists(),
        "manifest_keys":list(manifest.keys()),
        "manifest":manifest,
        "missing_boundary_seeds":list(MISSING),"matching_local_artifacts":related[:100],
        "matching_artifact_count":len(related),
        "whole_family_closure_pass":bool(closure.get("audit_pass") and closure.get("stable_under_one_axis_extensions")),
        "promote_or_resume_allowed":False,"kira_executed":False,"files_modified":False}
    print("VP05_STAGE2_MISSING_CLOSURE "+json.dumps(report,ensure_ascii=False,default=str),flush=True)

if __name__=="__main__":main()
