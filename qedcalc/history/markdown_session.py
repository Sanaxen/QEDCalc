from pathlib import Path
from datetime import datetime
from qedcalc.latex.renderer import render_latex

class MarkdownSession:
    def __init__(self, path, title="QEDCalc calculation session"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lines = [f"# {title}", "", f"Generated: {datetime.now().isoformat(timespec='seconds')}", ""]

    def text(self, heading, text):
        self.lines += [f"## {heading}", "", text, ""]

    def equation(self, heading, expr_or_latex):
        latex = expr_or_latex if isinstance(expr_or_latex, str) else render_latex(expr_or_latex)
        # Required format: one blank line immediately before and after the $$ block.
        self.lines += [f"## {heading}", "", "$$", latex, "$$", ""]

    def step(self, number, name, input_expr, output_expr, rule=None):
        self.lines += [f"## Step {number:02d}: {name}", "", "### Input", "", "$$", render_latex(input_expr), "$$", ""]
        if rule:
            self.lines += ["### Applied rule", "", rule, ""]
        self.lines += ["### Output", "", "$$", render_latex(output_expr), "$$", ""]

    def save(self):
        self.path.write_text("\n".join(self.lines).rstrip() + "\n", encoding="utf-8")
        return self.path
