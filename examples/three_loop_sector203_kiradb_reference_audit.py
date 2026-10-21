"""Read-only inspection of Kira SQLite database for small-ID reference metadata.

Uses SQLite mode=ro; no tables are modified and no binary blobs are printed.
Schema is inspected before bounded text/number samples are emitted.
"""
from __future__ import annotations
import argparse,json,sqlite3
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_kiradb_reference_audit.json"))
 a=p.parse_args();db=(a.project/"results/kira.db").resolve()
 if not db.is_file():p.error("kira.db not found")
 con=sqlite3.connect(db.as_uri()+"?mode=ro",uri=True)
 try:
  tables=con.execute("SELECT name,type,sql FROM sqlite_master WHERE type IN ('table','view') ORDER BY name").fetchall()
  result=[]
  for name,typ,ddl in tables:
   escaped='"'+name.replace('"','""')+'"'
   cols=con.execute(f"PRAGMA table_info({escaped})").fetchall()
   entry={"name":name,"type":typ,"ddl":ddl,
    "columns":[{"name":x[1],"type":x[2],"primary_key":bool(x[5])} for x in cols]}
   try:
    entry["row_count"]=con.execute(f"SELECT COUNT(*) FROM {escaped}").fetchone()[0]
    rows=con.execute(f"SELECT * FROM {escaped} LIMIT 8").fetchall()
    entry["sample"]=[[{"kind":"blob","bytes":len(v)} if isinstance(v,bytes) else
      (str(v)[:180] if isinstance(v,str) else v) for v in row] for row in rows]
   except sqlite3.DatabaseError as exc:entry["error"]=str(exc)
   result.append(entry)
 finally:con.close()
 report={"status":"KIRADB_SCHEMA_ONLY","database":str(db),"tables":result,
  "physical_weight_mapping_verified":False,
  "warning":"Schema and a few rows alone do not authorize interpreting small SYSTEM integer IDs as propagator powers."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_KIRADB_REFERENCE "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
