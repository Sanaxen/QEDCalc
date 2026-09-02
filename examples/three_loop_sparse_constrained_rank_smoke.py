from __future__ import annotations

import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralIndex, specialize_ibp_system
from three_loop.modp_sparse_constrained_rank import (
    sparse_constrained_target_rank,
    sparse_constrained_target_rank_at_probe,
)
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from examples.three_loop_q01_modp_4line_sector_ordered_rank import constrained_target_rank

PRIMES = (1000003, 1000033)


def I(n: int) -> IntegralIndex:
    return IntegralIndex((n,))


def main() -> None:
    f1, f2 = I(1), I(2)
    t1, t2, t3 = I(3), I(4), I(5)
    extra = I(6)
    D = sp.Symbol("D")
    z = sp.Symbol("z")

    equations = (
        IBPEquation({f1: D + 1, t1: 2, extra: 7}, "e1"),
        IBPEquation({f2: 3, t2: z + 2}, "e2"),
        IBPEquation({f1: 2, f2: 1, t3: 5}, "e3"),
        IBPEquation({t1: 1, t2: 1, t3: 1}, "e4"),
        IBPEquation({t2: 2, t3: 3}, "e5"),
    )
    forbidden = (f1, f2)
    targets = (t1, t2, t3)
    point = {D: sp.Integer(4), z: sp.Rational(1, 7)}

    probed = specialize_ibp_system(equations, point)
    probed = _specialize_remaining_symbols_by_name(probed, point)

    print("QEDCalc sparse constrained-rank smoke test")
    for prime in PRIMES:
        dense = constrained_target_rank(probed, forbidden, targets, prime)
        sparse_ready = sparse_constrained_target_rank(probed, forbidden, targets, prime)
        sparse_stream = sparse_constrained_target_rank_at_probe(
            equations, forbidden, targets, point, prime
        )
        sparse_tuple = (
            sparse_ready.forbidden_rank,
            sparse_ready.target_rank,
            sparse_ready.conditional_free_dimension,
        )
        stream_tuple = (
            sparse_stream.forbidden_rank,
            sparse_stream.target_rank,
            sparse_stream.conditional_free_dimension,
        )
        print(
            f"prime {prime}: dense={dense}, sparse={sparse_tuple}, streamed={stream_tuple}, "
            f"projected terms={sparse_stream.projected_term_count}"
        )
        if dense != sparse_tuple or dense != stream_tuple:
            raise RuntimeError(
                f"sparse constrained rank disagrees with dense reference for prime {prime}"
            )

    print("QEDCalc sparse constrained-rank smoke test PASS")


if __name__ == "__main__":
    main()
