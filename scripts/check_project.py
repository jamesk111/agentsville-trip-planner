"""Inspect notebook completion without executing its cells or calling APIs."""

import argparse
import ast
from pathlib import Path
import re
import sys

import nbformat

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def inspect_notebook(notebook_path: Path) -> list[int]:
    """Validate notebook format and syntax; return cells with TODO markers."""
    notebook = nbformat.read(notebook_path, as_version=4)
    nbformat.validate(notebook)
    pending = []
    for number, cell in enumerate(notebook.cells, start=1):
        if cell.cell_type != "code":
            continue
        ast.parse(cell.source, filename=f"notebook cell {number}")
        if re.search(r"\*{8,}", cell.source):
            pending.append(number)
    return pending


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true",
                        help="Exit unsuccessfully if notebook TODO markers remain.")
    args = parser.parse_args()
    try:
        pending = inspect_notebook(PROJECT_ROOT / "project_starter.ipynb")
        ast.parse((PROJECT_ROOT / "project_lib.py").read_text(encoding="utf-8"))
    except (OSError, ValueError, SyntaxError, nbformat.ValidationError) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: notebook format and Python syntax; helper library syntax.")
    if pending:
        print("PENDING: notebook TODO cells " + ", ".join(map(str, pending)))
        print("The project is unfinished. Syntax checks do not establish rubric completion.")
        return 1 if args.require_complete else 0
    print("No TODO markers remain. Review docs/rubric-checklist.md and run behavioral checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
