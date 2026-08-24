from qedcalc import parse_latex, render_latex
from qedcalc.operations.algebra import expand_expression
from qedcalc.operations.dirac import contract_gamma
from qedcalc.validation.validator import validate_indices

source = r"""
\gamma^\rho
(
m+\rlap{/}p-\rlap{/}k
)
\gamma^\mu
(
m+\rlap{/}p-\rlap{/}k
)
\gamma_\rho
"""

print("=== Input LaTeX ===")
print(source)

expr = parse_latex(source)

print("\n=== Parsed -> LaTeX ===")
print(render_latex(expr))

print("\n=== Validation ===")
for msg in validate_indices(expr):
    print(f"[{msg.level}] {msg.message}")

expanded = expand_expression(expr)

print("\n=== Expanded ===")
print(render_latex(expanded))

reduced = contract_gamma(expanded)

print("\n=== Gamma contraction (v0.1 rules) ===")
print(render_latex(reduced))
