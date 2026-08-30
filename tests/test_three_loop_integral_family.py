import sympy as sp

from three_loop import (
    Q01_FAMILY_SIZE,
    Q01_PHYSICAL_DENOMINATOR_COUNT,
    Q01_SEED,
    q01_family_checkpoint,
    q01_integral_family,
    q01_scalar_product_rules,
)
from qedcalc.operations.ibp import generate_ibp_equation, sp_atom


def test_q01_family_has_nine_physical_and_three_auxiliary_denominators():
    family = q01_integral_family()
    checkpoint = q01_family_checkpoint()
    assert family.size == Q01_FAMILY_SIZE == 12
    assert Q01_PHYSICAL_DENOMINATOR_COUNT == 9
    assert checkpoint["auxiliary_denominator_count"] == 3
    assert family.loop_momenta == ("k", "l", "r")
    assert family.external_momenta == ("p", "q")
    assert Q01_SEED.as_tuple() == (1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)


def test_q01_family_scalar_product_rules_span_all_loop_products():
    rules = q01_scalar_product_rules()
    required = {
        sp_atom("k", "k"), sp_atom("l", "l"), sp_atom("r", "r"),
        sp_atom("k", "l"), sp_atom("k", "r"), sp_atom("l", "r"),
        sp_atom("k", "p"), sp_atom("l", "p"), sp_atom("p", "r"),
        sp_atom("k", "q"), sp_atom("l", "q"), sp_atom("q", "r"),
    }
    assert required.issubset(rules)
    denominator_symbols = {sp.Symbol(f"D{i}") for i in range(1, 13)}
    for atom in required:
        leftovers = {
            s for s in rules[atom].free_symbols
            if str(s).startswith("SP__")
        }
        assert not leftovers
        assert rules[atom].free_symbols <= denominator_symbols | {sp.Symbol("m"), sp.Symbol("z")}


def test_q01_existing_ibp_engine_generates_finite_q_identity():
    family = q01_integral_family()
    equation = generate_ibp_equation(family, Q01_SEED, "k", "k")
    assert equation.terms
    assert equation.label == "d/dk · k"
    assert Q01_SEED in equation.terms
    assert equation.coefficient(Q01_SEED).has(sp.Symbol("D"))
    for coeff in equation.terms.values():
        assert not any(str(s).startswith("SP__") for s in coeff.free_symbols)
