"""Read-only SQLite metadata inventory for tiny VP05 SYSTEM integral IDs.

Inspects original Kira database schema and bounded column samples, without
assuming undocumented table semantics. Does not alter SQLite or Kira files.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
def quote(s): return '"'+s.replace('"','""')+'"'
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT)
 p.add_argument("--max-tables",type=int,default=80)
 p.add_argument("--max-columns",type=int,default=64)
 a=p.parse_args()
 if not 1<=a.max_tables<=100 or not 1<=a.max_columns<=100:p.error("Invalid limits")
 db=a.project/"results/kira.db"
 if not db.is_file():p.error("Missing saved kira.db")
 uri=db.resolve().as_uri()+"?mode=ro&immutable=1"
 conn=sqlite3.connect(uri,uri=True)
 try:
  schema=conn.execute("SELECT name,type,sql FROM sqlite_master WHERE type IN ('table','view') ORDER BY name LIMIT ?",(a.max_tables+1,)).fetchall()
  if len(schema)>a.max_tables:raise SystemExit("Database has more tables than audit cap")
  tables=[]
  for name,typ,sql in schema:
   cols=conn.execute("PRAGMA table_info("+quote(name)+")").fetchall()
   if len(cols)>a.max_columns:raise SystemExit("Column cap exceeded for "+name)
   try:
    sample=conn.execute("SELECT * FROM "+quote(name)+" LIMIT 2").fetchall()
    safe=[[str(v)[:180] if v is not None else None for v in row] for row in sample]
   except sqlite3.DatabaseError as exc:
    safe=[["QUERY_ERROR",str(exc)[:180]]]
   tables.append({"table":name,"type":typ,"columns":[{"name":c[1],"type":c[2],"pk":c[5]} for c in cols],
    "sample_first_two_rows":safe,"schema_sql_excerpt":(sql or "")[:450]})
  out={"status":"SQLITE_SCHEMA_EVIDENCE_ONLY","db_sha256":hashlib.sha256(db.read_bytes()).hexdigest(),
       "project":str(a.project.resolve()),"tables":tables,
       "small_weight_semantics_verified":False,"master_numbering_verified":False,
       "physical_exponent_mapping_verified":False,"sqlite_open_mode":"ro_immutable",
       "source_files_modified":False,"kira_executed":False}
  print("VP05_KIRA_DB_SCHEMA_AUDIT "+json.dumps(out,ensure_ascii=False),flush=True)
 finally:conn.close()
if __name__=="__main__":main()
