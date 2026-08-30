from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

SECTION_MAP = {
    "scalar": "Scalar",
    "constants": "Constants",
    "constant": "Constants",
    "vector": "Vector",
    "index": "Index",
}


def normalize_latex_symbol(token: str) -> str:
    token = token.strip()
    if token.startswith("\\"):
        return token[1:]
    return token


@dataclass(frozen=True)
class SymbolTable:
    scalar: frozenset[str]
    constants: frozenset[str]
    vector: frozenset[str]
    index: frozenset[str]
    source_path: Path | None = None

    def entries(self, category: str) -> frozenset[str]:
        key = category.lower()
        if key == "scalar":
            return self.scalar
        if key in ("constant", "constants"):
            return self.constants
        if key == "vector":
            return self.vector
        if key == "index":
            return self.index
        raise KeyError(category)

    def has(self, token: str, category: str) -> bool:
        return normalize_latex_symbol(token) in self.entries(category)

    def require(self, token: str, category: str, *, context: str = "") -> str:
        name = normalize_latex_symbol(token)
        if name not in self.entries(category):
            latex = token if token.startswith("\\") else token
            suffix = f" ({context})" if context else ""
            raise ValueError(
                f'Undefined {category} symbol "{latex}" is used{suffix}.'
                f' Add it to [{category}] in symbols.txt.'
            )
        return name

    def classify_bare(self, token: str) -> str:
        """Classify a token appearing as an ordinary expression atom.

        Index is intentionally excluded here: index context is explicit in gamma/metric.
        """
        name = normalize_latex_symbol(token)
        found = []
        if name in self.scalar:
            found.append("Scalar")
        if name in self.constants:
            found.append("Constants")
        if name in self.vector:
            found.append("Vector")
        if not found:
            raise ValueError(
                f'Undefined symbol "{token}" is used.'
                ' Add it to exactly one of [Scalar], [Constants], or [Vector] in symbols.txt.'
            )
        if len(found) > 1:
            raise ValueError(
                f'Symbol "{token}" has an ambiguous category: {", ".join(found)}.'
                ' For ordinary expression atoms, define a symbol in only one of [Scalar], [Constants], or [Vector].'
            )
        return found[0]

    def to_markdown(self) -> str:
        def latex_name(name: str) -> str:
            return "\\" + name if name in LATEX_COMMAND_NAMES else name
        groups = [
            ("Scalar", self.scalar),
            ("Constants", self.constants),
            ("Vector", self.vector),
            ("Index", self.index),
        ]
        lines = []
        for title, vals in groups:
            lines.append(f"- **{title}:** " + ", ".join(latex_name(x) for x in sorted(vals)))
        return "\n".join(lines)


LATEX_COMMAND_NAMES = frozenset({
    # lower-case Greek
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta",
    "theta", "vartheta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron",
    "pi", "varpi", "rho", "varrho", "sigma", "varsigma", "tau", "upsilon", "phi",
    "varphi", "chi", "psi", "omega",
    # upper-case Greek commands commonly used by LaTeX
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon", "Phi", "Psi", "Omega",
    # common named mathematical constants/symbols that may be configured
    "hbar", "ell",
})


def default_symbol_table_path() -> Path:
    return Path(__file__).resolve().parents[2] / "symbols.txt"


def load_symbol_table(path: str | Path | None = None) -> SymbolTable:
    path = Path(path) if path is not None else default_symbol_table_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Symbol definition file was not found: {path}\n"
            "Place symbols.txt in the project root directory."
        )

    data = {"Scalar": set(), "Constants": set(), "Vector": set(), "Index": set()}
    current = None
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            key = line[1:-1].strip().lower()
            if key not in SECTION_MAP:
                raise ValueError(f"symbols.txt line {lineno}: unknown section [{line[1:-1]}]")
            current = SECTION_MAP[key]
            continue
        if current is None:
            raise ValueError(f"symbols.txt line {lineno}: symbols must be written inside a section such as [Scalar].")
        # One per line is recommended, but comma-separated entries are accepted too.
        for item in (x.strip() for x in line.split(",")):
            if item:
                data[current].add(normalize_latex_symbol(item))

    return SymbolTable(
        scalar=frozenset(data["Scalar"]),
        constants=frozenset(data["Constants"]),
        vector=frozenset(data["Vector"]),
        index=frozenset(data["Index"]),
        source_path=path,
    )
