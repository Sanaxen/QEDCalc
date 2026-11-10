"""Offline unit tests of the overnight loop resource and progress guards."""
from __future__ import annotations
import argparse
import unittest
from examples.three_loop_vp05_sector202_step51_overnight import (
    parse_free,unsafe,progress_from_output,GIB,
)

class OvernightGuardsTests(unittest.TestCase):
    def setUp(self):
        self.args=argparse.Namespace(min_windows_ram_gib=2.0,
            min_wsl_ram_gib=1.5,max_swap_used_gib=190.0,
            min_swap_free_gib=20.0,min_disk_free_gib=15.0)

    def test_parse_wsl_free(self):
        text=("              total        used        free      shared  buff/cache   available\n"
              "Mem:       30000000000  20000000000  1000000000  100000000  9000000000  10000000000\n"
              "Swap:     250000000000 100000000000 150000000000\n")
        data=parse_free(text)
        self.assertEqual(data["wsl_mem_available_bytes"],10000000000)
        self.assertEqual(data["wsl_swap_used_bytes"],100000000000)
        self.assertEqual(data["wsl_swap_free_bytes"],150000000000)
        with self.assertRaises(ValueError):
            parse_free("Mem: 1 2 3")

    def test_resource_guards(self):
        healthy={"windows_mem_available_bytes":4*GIB,
                 "wsl_mem_available_bytes":3*GIB,
                 "wsl_swap_used_bytes":100*GIB,
                 "wsl_swap_free_bytes":140*GIB,
                 "disk_free_bytes":25*GIB}
        self.assertEqual(unsafe(healthy,self.args),[])
        failing={**healthy,"wsl_mem_available_bytes":GIB,
                 "wsl_swap_used_bytes":195*GIB,
                 "wsl_swap_free_bytes":10*GIB,
                 "disk_free_bytes":GIB}
        self.assertEqual(unsafe(failing,self.args),
            ["wsl_low_ram","swap_used_high","swap_free_low","disk_free_low"])

    def test_scratch_result_parsing(self):
        line='VP05_SECTOR202_STEP51_SCRATCH_RESULT {"status":"INTRA_STEP51_SCRATCH_NOT_PROOF","coefficients_this_run":1,"saved_coefficient_count":4,"total_coefficients":288}'
        result=progress_from_output("noise\n"+line+"\n")
        self.assertEqual(result["saved_coefficient_count"],4)
        with self.assertRaises(RuntimeError):
            progress_from_output("unrelated")
        with self.assertRaises(RuntimeError):
            progress_from_output(line+"\n"+line)

if __name__=="__main__":
    unittest.main()
