from collections import Counter
from dataclasses import dataclass
from qedcalc.core.expression import Gamma, Metric, QEDExpr
from qedcalc.config.symbols import LATEX_COMMAND_NAMES

@dataclass
class ValidationMessage:
    level: str
    message: str


def _display(name: str) -> str:
    return "\\" + name if name in LATEX_COMMAND_NAMES else name


def validate_indices(expr: QEDExpr):
    counter = Counter()
    for node in expr.walk():
        if isinstance(node, Gamma):
            counter[node.index.name] += 1
        elif isinstance(node, Metric):
            counter[node.left.name] += 1
            counter[node.right.name] += 1

    messages = []
    for name, count in sorted(counter.items()):
        shown = _display(name)
        if count == 1:
            messages.append(ValidationMessage(
                "INFO",
                f"{shown}: appears once; it may be a free index."
            ))
        elif count == 2:
            messages.append(ValidationMessage(
                "OK",
                f"{shown}: appears twice; it is a contraction-index candidate."
            ))
        else:
            messages.append(ValidationMessage(
                "WARNING",
                f"{shown}: appears {count} times; check the index structure."
            ))
    return messages
