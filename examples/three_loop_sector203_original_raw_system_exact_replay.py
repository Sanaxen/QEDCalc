"""Exact source-transcription replay: 528 selected VP05 witness rows vs original 2678 Kira SYSTEM records.

Compares original row_index, file, equation_id, ordered (weight,sector) keys
and exact coefficient strings. Uses the producer's ORIGINAL r6s6d1 L2
project default, not the older r5s6d0 project. Read-only; no Kira execution.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT as PRODUCER_PROJECT
from examples.three_loop_sector203_target_scope_preflight import DEFAULT as COMPRESSED,TARGET

OUT=Path("output/three_loop_integral_family_audit/vp05_original_witness_raw_system_exact_replay.json")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project",type=Path,default=PRODUCER_PROJECT)
    ap.add_argument("--compressed",type=Path,default=COMPRESSED)
    ap.add_argument("--output",type=Path,default=OUT)
    a=ap.parse_args()
    packed=json.loads(a.compressed.read_text(encoding="utf-8-sig"))
    original=Path(packed["source"])
    raw=original.read_bytes()
    witness=json.loads(raw.decode("utf-8-sig"))
    rows=witness["rows"]
    if len(rows)!=528:ap.error("Expected 528 witness records")
    index_map={}
    for j,row in enumerate(rows):
        i=int(row["row_index"])
        if i in index_map:ap.error(f"Duplicate row_index {i}")
        index_map[i]=(j,row)
    folder=a.project.resolve()/"tmp/VP05_full"
    files=sorted(folder.glob("SYSTEM_VP05_full_*.gz"))
    if not files:ap.error("Missing raw SYSTEM files in correct L2 project")
    count=0;terms_checked=0;mismatches=[];matched=0
    raw_target_counts={k:0 for k in TARGET}
    raw_target_selected={k:0 for k in TARGET}
    for file in files:
        with gzip.open(file,"rt",encoding="utf-8") as stream:
            while (marker:=stream.readline()):
                if marker.strip()!="Eq":raise ValueError(f"Malformed Eq marker file={file.name} record={count}")
                eqid=stream.readline().strip()
                n=int(stream.readline().strip())
                selected=index_map.get(count)
                if selected:
                    _,saved=selected
                    if saved["file"]!=file.name or saved["equation_id"]!=eqid or len(saved["terms"])!=n:
                        mismatches.append({"row_index":count,"reason":"file/equation_id/term-count mismatch",
                            "source_file":file.name,"source_eqid":eqid,"source_terms":n})
                for j in range(n):
                    fields=stream.readline().split()
                    if len(fields)<4:raise ValueError("Malformed SYSTEM term")
                    key=(int(fields[2]),int(fields[3]))
                    if key in raw_target_counts:raw_target_counts[key]+=1
                    if selected:
                        _,saved=selected
                        if j<len(saved["terms"]):
                            term=saved["terms"][j]
                            if term["key"]!=list(key) or term["coefficient"]!=fields[1]:
                                if len(mismatches)<20:mismatches.append({
                                    "row_index":count,"term_index":j,"source_key":list(key),
                                    "saved_key":term["key"],"source_coefficient":fields[1],
                                    "saved_coefficient":term["coefficient"]})
                        terms_checked+=1
                        if key in raw_target_selected:raw_target_selected[key]+=1
                if selected:matched+=1
                count+=1
    if count!=2678:ap.error(f"Wrong project SYSTEM record count: {count} != 2678")
    if matched!=528 or any(i>=count for i in index_map):
        ap.error(f"Missing saved row indices, matched {matched}/528")
    verified=not mismatches
    report={"summary":{"project":str(a.project.resolve()),"system_files":len(files),
      "system_equations":count,"witness_rows":len(rows),"matched_rows":matched,
      "matched_terms":terms_checked,"mismatches":len(mismatches),
      "exact_source_transcription_verified":verified,
      "raw_target_occurrences":{str(k):v for k,v in raw_target_counts.items()},
      "selected_raw_target_occurrences":{str(k):v for k,v in raw_target_selected.items()},
      "original_sha256":hashlib.sha256(raw).hexdigest(),
      "physical_exponent_mapping_verified":False,"fermat_executed":False,
      "kira_executed":False},"mismatch_examples":mismatches}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_ORIGINAL_RAW_SYSTEM_REPLAY "+json.dumps({**report["summary"],
        "mismatch_examples":mismatches[:5],"output":str(a.output)}),flush=True)
    if not verified:raise SystemExit(1)

if __name__=="__main__":main()
