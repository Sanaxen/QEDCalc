"""Q01 projected-amplitude -> final60 coefficients using the validated d+1 FireFly reduction.

The r9s4d0 FireFly boundary run has 125 masters, so its 65 non-final60 masters
must not be expected to disappear by amplitude-level coefficient cancellation.
The validated d+1 run r9s3d1 has masters.final = 60 and all final60 forms remain
masters.  Therefore this wrapper redirects the exact Fermat coefficient
synthesis to that reduction table.
"""
from __future__ import annotations

import examples.three_loop_q01_projected_amplitude_master_coefficients as base
import examples.three_loop_q01_projected_amplitude_master_coefficients_fermat as impl
import examples.three_loop_q01_projected_amplitude_master_coefficients_fermat_stdio as stdio_patch

# Select the already validated d+1 FireFly reduction, whose masters.final is
# exactly the finalized 60-master Q01 basis.
base.ALT_ROOT = base.PROJECT / "exact944_r9s3d1_firefly"
base.RESULT_DIR = base.ALT_ROOT / "results" / base.FAMILY
base.TARGET_FILE = base.PROJECT / "q01_exact944_r9s3d1_firefly_boundary_targets"

# Keep this checkpoint separate from the failed/diagnostic r9s4d0 125-master
# synthesis.  The output names are the canonical final60 coefficient artifacts.
impl.CHECKPOINT = base.PROJECT / "q01_projected_amplitude_final60_coefficients_fermat_d1_checkpoint.json"
impl.OUTPUT_JSON = base.PROJECT / "q01_projected_amplitude_final60_coefficients.json"
impl.OUTPUT_TXT = base.PROJECT / "q01_projected_amplitude_final60_coefficients.txt"

# The stdio module has already installed the direct-stdio Fermat runner onto
# impl._run_fermat_sum as an import side effect.

if __name__ == "__main__":
    impl.main()
