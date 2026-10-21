"""Inspect saved Kira logs and sector mapping files for exact target provenance.

Read-only and bounded. Enumerates original mapping file structure and extracts
the Kira initiation/selection log context; no undocumented parsing of Kira
binary mapping formats and no physical alias claims.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_weight_audit import load_codec,parse_file_integrals

FILES=("kira.log","monitored_kira.log","sectormappings/auxiliary.yaml",
"sectormappings/VP05_full/canonica","sectormappings/VP05_full/sectorRelations",
"sectormappings/VP05_full/sectorSymmetries","sectormappings/VP05_full/relations",
"sectormappings/VP05_full/symmetries","sectormappings/VP05_full/nonTrivialSector",
"sector203_monitored_kira.py")
PATTERN=re.compile(r"mandatory|select|initi|symmetr|identit|seed|r:|s:|d:|sector|reduc|triang|truncat|complete|finished|start|generat|master|warning|error",re.I)
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--codec-file",type=Path,default=Path("output/tools/pyred_weight.py"))
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_kira_symmetry_execution_trace.json"))
 a=p.parse_args()
 m=load_codec(a.codec_file);bits,ordering=m.from_kiradb(str(a.project/"results/kira.db"))
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 targets=[]
 for exponents in parse_file_integrals(a.project/"mandatory_provisional64_sector203.txt"):
  weight=int(codec.encode(exponents))
  if tuple(codec.decode(weight))!=exponents:raise RuntimeError("Codec roundtrip failed")
  targets.append({"exponents":list(exponents),"weight":weight,"weight_hex":hex(weight)})
 results=[]
 for rel in FILES:
  path=a.project/rel;item={"path":rel,"exists":path.is_file()}
  if not path.is_file():results.append(item);continue
  raw=path.read_bytes()
  item.update({"bytes":len(raw),"utf8_text":False})
  try:text=raw.decode("utf-8-sig")
  except UnicodeDecodeError:
   item["binary_or_non_utf8"]=True;results.append(item);continue
  item["utf8_text"]=True
  lines=text.splitlines();item["line_count"]=len(lines)
  item["head"]=[{"line":i,"text":s[:350]} for i,s in enumerate(lines[:18],1)]
  hits=[{"line":i,"text":s[:350]} for i,s in enumerate(lines,1) if PATTERN.search(s)]
  item["matching_line_count"]=len(hits)
  item["relevant_lines"]=hits[:110] if rel.endswith(".log") else hits[:55]
  weight_mentions=[]
  for t in targets:
   if str(t["weight"]) in text or t["weight_hex"][2:] in text.lower():
    weight_mentions.append(t["weight"])
  item["target_weight_literal_mentions"]=weight_mentions
  results.append(item)
 report={"status":"KIRA_SYMMETRY_EXECUTION_TRACE_ONLY",
   "project":str(a.project),"targets":targets,"files":results,
   "physical_alias_mapping_verified":False,
   "target_selection_execution_verified":False,
   "warning":"Absent literal weight in mapping file does not imply absent symmetry mapping; Kira-specific structured mapping decoding is still required."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_KIRA_SYMMETRY_EXECUTION_TRACE "+json.dumps({
  "status":report["status"],"targets":targets,
  "files":[{"path":x["path"],"bytes":x.get("bytes"),"utf8_text":x.get("utf8_text"),
    "line_count":x.get("line_count"),"head":x.get("head",[])[:5],
    "relevant_lines":x.get("relevant_lines",[])[:30] if x["path"].endswith(".log") else x.get("relevant_lines",[])[:8],
    "target_weight_literal_mentions":x.get("target_weight_literal_mentions",[])} for x in results],
  "output":str(a.output),"physical_alias_mapping_verified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
