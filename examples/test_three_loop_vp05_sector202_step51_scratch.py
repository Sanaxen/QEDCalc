"""Offline, synthetic unit tests for exact sector202 intra-step51 scratch.

Does not need Kira source files or modify existing project checkpoints.
"""
from __future__ import annotations
import copy
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_step51_scratch import (
    atomic_save, compute_one, key_id, modular_check, scratch_config,
    source_context, verify_scratch, summarize, seal_data, seal_matches, verify_or_seal,
)

class Step51ScratchTests(unittest.TestCase):
    def setUp(self):
        self.target={
            "steps":50,
            "config":{"target":"A","max_expression_chars":7500},
            "remaining":[[[1,73],"z+1"],[[2,73],"z+3"]],
            "source":[[11,"d-1"]],
        }
        self.pivot={"pivots":[{
            "lead":[1,73],
            "row":[[[1,73],"1"],[[2,73],"z+2"],[[3,73],"-1/2"]],
            "trace":[[11,"1/2"],[12,"-1"]],
        }]}
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"source_pivots.json"
        self.path.write_text(json.dumps(self.pivot),encoding="utf-8")

    def test_coefficient_arithmetic_and_order(self):
        original=copy.deepcopy(self.target)
        lead,pivot,jobs=source_context(self.target,self.path)
        self.assertEqual(lead,(1,73))
        self.assertEqual([k for _,k,_ in jobs][:3],[[1,73],[2,73],[3,73]])
        self.assertEqual(len(jobs),5)
        for kind,key,_ in jobs:
            value=compute_one(self.target,self.path,kind,key)
            modular_check(self.target,pivot,kind,key,value)
        z,d=sp.symbols("z d")
        self.assertEqual(sp.cancel(sp.sympify(compute_one(self.target,self.path,
                       "remainder",[2,73]))-((z+3)-(z+1)*(z+2))),0)
        self.assertEqual(sp.cancel(sp.sympify(compute_one(self.target,self.path,
                       "source_trace",11))-(d-1+(z+1)/2)),0)
        self.assertEqual(self.target,original)
        self.assertEqual(json.loads(self.path.read_text()),self.pivot)

    def test_immutability_resume_and_tamper_guard(self):
        lead,pivot,jobs=source_context(self.target,self.path)
        statepath=Path(self.tmp.name)/"target.json"
        statepath.write_text(json.dumps(self.target),encoding="utf-8")
        source=Path(self.tmp.name)/"rows"
        cert=Path(self.tmp.name)/"cert"
        source.write_bytes(b"original source")
        cert.write_bytes(b"certificate")
        cfg=scratch_config(statepath,self.path,source,cert,self.target,lead,jobs,9000)
        scratch={"version":1,"status":"INTRA_STEP51_SCRATCH_NOT_PROOF",
                 "config":cfg,"done":[],"exact_target_proven":False}
        file=Path(self.tmp.name)/"scratch.json"
        atomic_save(file,scratch,False)
        with self.assertRaises(FileExistsError): atomic_save(file,scratch,False)
        kind,key,_=jobs[0]
        value=compute_one(self.target,self.path,kind,key)
        scratch["done"].append({"id":key_id(kind,key),"value":value,"chars":len(value)})
        atomic_save(file,scratch,True)
        self.assertEqual(len(json.loads(file.read_text())["done"]),1)
        verify_scratch(json.loads(file.read_text()),cfg,self.target,pivot,jobs)
        stats=summarize(scratch,self.target,pivot,jobs)
        self.assertFalse(stats["complete"])
        tampered=copy.deepcopy(scratch)
        tampered["done"][0]["value"]="9"
        tampered["done"][0]["chars"]=1
        with self.assertRaises(AssertionError):
            verify_scratch(tampered,cfg,self.target,pivot,jobs)
        with self.assertRaises(RuntimeError):
            verify_scratch(scratch,{**cfg,"target_state_sha256":"bad"},
                           self.target,pivot,jobs)


    def test_sealed_prefix_skips_redundant_modular_work_and_rejects_changed_file(self):
        lead,pivot,jobs=source_context(self.target,self.path)
        statepath=Path(self.tmp.name)/"target.json"
        statepath.write_text(json.dumps(self.target),encoding="utf-8")
        source=Path(self.tmp.name)/"rows"
        cert=Path(self.tmp.name)/"cert"
        source.write_bytes(b"source")
        cert.write_bytes(b"certificate")
        cfg=scratch_config(statepath,self.path,source,cert,self.target,lead,jobs,9000)
        scratch={"version":1,"status":"INTRA_STEP51_SCRATCH_NOT_PROOF",
                 "config":cfg,"done":[],"exact_target_proven":False}
        kind,key,_=jobs[0]
        value=compute_one(self.target,self.path,kind,key)
        scratch["done"].append({"id":key_id(kind,key),"value":value,"chars":len(value)})
        path=Path(self.tmp.name)/"scratch.json"
        seal=Path(self.tmp.name)/"seal.json"
        atomic_save(path,scratch,False)
        self.assertFalse(seal_matches(seal,path,cfg,scratch))
        self.assertEqual(verify_or_seal(scratch,cfg,self.target,pivot,jobs,path,seal),
                         "FULL_MODULAR_PREFIX_VERIFIED_NOT_PROOF")
        self.assertTrue(seal_matches(seal,path,cfg,scratch))
        with patch("examples.three_loop_vp05_sector202_step51_scratch.modular_check",
                   side_effect=AssertionError("unexpected expensive re-verification")):
            self.assertEqual(verify_or_seal(scratch,cfg,self.target,pivot,jobs,path,seal),
                             "HASH_VERIFIED_MODULAR_PREFIX_NOT_PROOF")
        altered=copy.deepcopy(scratch)
        altered["done"][0]["value"]="9"
        altered["done"][0]["chars"]=1
        atomic_save(path,altered,True)
        self.assertFalse(seal_matches(seal,path,cfg,altered))
        with self.assertRaises(AssertionError):
            verify_or_seal(altered,cfg,self.target,pivot,jobs,path,seal)
        self.assertEqual(json.loads(seal.read_text())["verified_count"],1)

    def test_string_metrics_match_existing_synthetic_metrics(self):
        lead,pivot,jobs=source_context(self.target,self.path)
        cfg={"target_max_expression_chars":7500}
        scratch={"config":cfg,"done":[]}
        for kind,key,_ in jobs:
            value=compute_one(self.target,self.path,kind,key)
            scratch["done"].append({"id":key_id(kind,key),"value":value,"chars":len(value)})
        stat=summarize(scratch,self.target,pivot,jobs)
        self.assertTrue(stat["complete"])
        self.assertEqual(stat["remainder_terms"],2)
        self.assertEqual(stat["original_support"],2)
        self.assertEqual(stat["lead"],[2,73])

    def test_strict_operation_identity(self):
        self.assertEqual(key_id("remainder",[1,73]),"remainder:1,73")
        self.assertEqual(key_id("source_trace",11),"source_trace:11")
        lead,pivot,jobs=source_context(self.target,self.path)
        cfg={"operation_ids":[key_id(kind,k) for kind,k,_ in jobs],
             "scratch_max_expression_chars":9000}
        scratch={"version":1,"config":cfg,"status":"INTRA_STEP51_SCRATCH_NOT_PROOF",
                 "exact_target_proven":False,"done":[{"id":"bad","value":"0","chars":1}]}
        with self.assertRaisesRegex(RuntimeError,"order"):
            verify_scratch(scratch,cfg,self.target,pivot,jobs)

if __name__=="__main__":unittest.main()
