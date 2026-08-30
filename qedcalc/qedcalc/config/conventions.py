from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}


def _parse_bool(value: str, *, key: str) -> bool:
    v = value.strip().lower()
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False
    raise ValueError(f'Invalid boolean for "{key}": {value!r}. Use true or false.')


def _normalize_scheme(value: str) -> str:
    v = value.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "onshell": "on_shell",
        "on_shell": "on_shell",
        "os": "on_shell",
        "ms": "MS",
        "msbar": "MSbar",
        "ms_bar": "MSbar",
        "overline_ms": "MSbar",
        "bphz": "BPHZ",
    }
    if v not in aliases:
        raise ValueError(
            f'Unsupported renormalization_scheme {value!r}. '
            'Supported values are on_shell, MS, MSbar, and BPHZ.'
        )
    return aliases[v]


def _normalize_dimreg_subtraction(value: str) -> str:
    v = value.strip().lower().replace("-", "").replace("_", "")
    if v == "ms":
        return "MS"
    if v in {"msbar", "overlinems"}:
        return "MSbar"
    if v in {"none", "off"}:
        return "none"
    raise ValueError(
        f'Unsupported dimreg_subtraction {value!r}. '
        'Supported values are MS, MSbar, and none.'
    )


@dataclass(frozen=True)
class QEDConventions:
    metric_signature: str = "+---"
    gauge: str = "feynman"
    renormalization_scheme: str = "on_shell"
    dimreg_dimension: str = "4 - 2*epsilon"
    dimreg_subtraction: str = "MSbar"
    msbar_factor: bool = True
    subdiagram_include_coupling: bool = True
    subdiagram_include_loop_measure: bool = True
    subdiagram_include_i: bool = True
    coupling_symbol: str = "e"
    loop_measure_denominator_latex: str = r"(2\pi)^4"
    loop_i_factor_latex: str = "i"
    source_path: Path | None = None

    def validate(self) -> "QEDConventions":
        if self.metric_signature not in {"+---", "-+++"}:
            raise ValueError('metric_signature must be "+---" or "-+++".')
        if self.gauge not in {"feynman", "covariant"}:
            raise ValueError('gauge must be "feynman" or "covariant".')
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", self.coupling_symbol):
            raise ValueError("coupling_symbol must be a simple identifier such as e.")
        if not self.loop_measure_denominator_latex.strip():
            raise ValueError("loop_measure_denominator_latex must not be empty.")
        if self.subdiagram_include_i and not self.loop_i_factor_latex.strip():
            raise ValueError("loop_i_factor_latex must not be empty when subdiagram_include_i=true.")
        return self

    @property
    def is_feynman_gauge(self) -> bool:
        return self.gauge == "feynman"

    @staticmethod
    def _pow_latex(base: str, power: int) -> str:
        if power <= 0:
            return ""
        if power == 1:
            return base
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", base):
            return rf"{base}^{{{power}}}"
        return rf"\left({base}\right)^{{{power}}}"

    def _normalization_latex(self, coupling_power: int, measure_power: int, i_power: int) -> str:
        numerator = self._pow_latex(self.coupling_symbol, coupling_power) or "1"
        denominator_parts = []
        if measure_power > 0:
            denominator_parts.append(self._pow_latex(self.loop_measure_denominator_latex, measure_power))
        if i_power > 0:
            denominator_parts.append(self._pow_latex(self.loop_i_factor_latex, i_power))
        if not denominator_parts:
            return numerator
        return rf"\frac{{{numerator}}}{{{' '.join(denominator_parts)}}}"

    def standard_loop_prefactor_latex(self, loop_order: int = 1) -> str:
        """Return the project's standard QED loop normalization for ``loop_order``.

        Under the default convention, one loop is ``e^2/((2\\pi)^4 i)`` and
        two loops are ``e^4/((2\\pi)^8 i^2)``.
        """
        loop_order = int(loop_order)
        if loop_order < 0:
            raise ValueError("loop_order must be non-negative.")
        return self._normalization_latex(2 * loop_order, loop_order, loop_order)

    def subdiagram_prefactor_latex(self, loop_order: int = 1) -> str:
        """Return the normalization owned by a contracted subdiagram."""
        loop_order = int(loop_order)
        return self._normalization_latex(
            2 * loop_order if self.subdiagram_include_coupling else 0,
            loop_order if self.subdiagram_include_loop_measure else 0,
            loop_order if self.subdiagram_include_i else 0,
        )

    def compact_outer_prefactor_latex(self, total_loop_order: int = 2, contracted_loop_order: int = 1) -> str:
        """Return the normalization left after contracting a subdiagram.

        This is computed from normalization ownership rather than by parsing a
        raw LaTeX prefactor.  With the default settings a two-loop diagram with
        a one-loop contracted subdiagram leaves ``e^2/((2\\pi)^4 i)``.
        """
        total_loop_order = int(total_loop_order)
        contracted_loop_order = int(contracted_loop_order)
        if total_loop_order < contracted_loop_order or contracted_loop_order < 0:
            raise ValueError("Require total_loop_order >= contracted_loop_order >= 0.")
        coupling_power = 2 * total_loop_order
        measure_power = total_loop_order
        i_power = total_loop_order
        if self.subdiagram_include_coupling:
            coupling_power -= 2 * contracted_loop_order
        if self.subdiagram_include_loop_measure:
            measure_power -= contracted_loop_order
        if self.subdiagram_include_i:
            i_power -= contracted_loop_order
        return self._normalization_latex(coupling_power, measure_power, i_power)

    def compact_outer_one_loop_prefactor_latex(self) -> str:
        return self.compact_outer_prefactor_latex(2, 1)

    def to_markdown(self) -> str:
        rows = [
            ("metric_signature", self.metric_signature),
            ("gauge", self.gauge),
            ("renormalization_scheme", self.renormalization_scheme),
            ("dimreg_dimension", self.dimreg_dimension),
            ("dimreg_subtraction", self.dimreg_subtraction),
            ("msbar_factor", str(self.msbar_factor).lower()),
            ("subdiagram_include_coupling", str(self.subdiagram_include_coupling).lower()),
            ("subdiagram_include_loop_measure", str(self.subdiagram_include_loop_measure).lower()),
            ("subdiagram_include_i", str(self.subdiagram_include_i).lower()),
            ("coupling_symbol", self.coupling_symbol),
            ("loop_measure_denominator_latex", self.loop_measure_denominator_latex),
            ("loop_i_factor_latex", self.loop_i_factor_latex),
        ]
        return "\n".join(f"- **{k}:** `{v}`" for k, v in rows)


def default_conventions_path() -> Path:
    return Path(__file__).resolve().parents[2] / "conventions.txt"


def load_conventions(path: str | Path | None = None) -> QEDConventions:
    path = Path(path) if path is not None else default_conventions_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Convention definition file was not found: {path}\n"
            "Place conventions.txt in the project root directory."
        )

    raw: dict[str, str] = {}
    current_section = None
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip().lower()
            continue
        if "=" not in line:
            raise ValueError(f"conventions.txt line {lineno}: expected key = value.")
        key, value = (x.strip() for x in line.split("=", 1))
        if not key:
            raise ValueError(f"conventions.txt line {lineno}: empty key.")
        # Section prefixes are accepted for readability, but keys stay globally unique.
        raw[key.lower()] = value

    allowed = {
        "metric_signature", "gauge", "renormalization_scheme",
        "dimreg_dimension", "dimreg_subtraction", "msbar_factor",
        "subdiagram_include_coupling", "subdiagram_include_loop_measure",
        "subdiagram_include_i", "coupling_symbol",
        "loop_measure_denominator_latex", "loop_i_factor_latex",
    }
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ValueError("Unknown convention key(s): " + ", ".join(unknown))

    gauge = raw.get("gauge", "feynman").strip().lower().replace("-", "_")
    if gauge in {"feynman_gauge", "feynman"}:
        gauge = "feynman"
    elif gauge in {"covariant", "general_covariant", "general_covariant_gauge"}:
        gauge = "covariant"

    cfg = QEDConventions(
        metric_signature=raw.get("metric_signature", "+---").strip(),
        gauge=gauge,
        renormalization_scheme=_normalize_scheme(raw.get("renormalization_scheme", "on_shell")),
        dimreg_dimension=raw.get("dimreg_dimension", "4 - 2*epsilon").strip(),
        dimreg_subtraction=_normalize_dimreg_subtraction(raw.get("dimreg_subtraction", "MSbar")),
        msbar_factor=_parse_bool(raw.get("msbar_factor", "true"), key="msbar_factor"),
        subdiagram_include_coupling=_parse_bool(raw.get("subdiagram_include_coupling", "true"), key="subdiagram_include_coupling"),
        subdiagram_include_loop_measure=_parse_bool(raw.get("subdiagram_include_loop_measure", "true"), key="subdiagram_include_loop_measure"),
        subdiagram_include_i=_parse_bool(raw.get("subdiagram_include_i", "true"), key="subdiagram_include_i"),
        coupling_symbol=raw.get("coupling_symbol", "e").strip(),
        loop_measure_denominator_latex=raw.get("loop_measure_denominator_latex", r"(2\pi)^4").strip(),
        loop_i_factor_latex=raw.get("loop_i_factor_latex", "i").strip(),
        source_path=path,
    )
    return cfg.validate()
