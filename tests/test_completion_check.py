"""Prevent syntax checks from being reported as project completion."""

from pathlib import Path
import sys

import nbformat
import pytest

from scripts import check_project
from scripts.check_project import inspect_notebook

ROOT = Path(__file__).resolve().parents[1]


def test_unfinished_notebook_fails_the_completion_gate(tmp_path, monkeypatch, capsys):
    notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell('prompt = "**********"')])
    nbformat.write(notebook, tmp_path / "project_starter.ipynb")
    (tmp_path / "project_lib.py").write_text("value = 1", encoding="utf-8")
    monkeypatch.setattr(check_project, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["check_project.py", "--require-complete"])
    assert check_project.main() == 1
    assert "PENDING:" in capsys.readouterr().out


def test_invalid_python_is_rejected_even_without_todo_markers(tmp_path):
    notebook_path = tmp_path / "broken.ipynb"
    notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("def broken(")])
    nbformat.write(notebook, notebook_path)
    with pytest.raises(SyntaxError):
        inspect_notebook(notebook_path)


def test_complete_syntax_is_not_a_rubric_claim(tmp_path):
    notebook_path = tmp_path / "simple.ipynb"
    nbformat.write(nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("value = 1")]), notebook_path)
    assert inspect_notebook(notebook_path) == []
