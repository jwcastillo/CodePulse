"""Regression: every console_scripts entry point must import a module that setup() installs."""
import runpy
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]


def test_console_scripts_modules_are_installed():
    with mock.patch("setuptools.setup") as setup:
        runpy.run_path(str(ROOT / "setup.py"))
    kwargs = setup.call_args.kwargs
    installed = set(kwargs.get("py_modules", [])) | {p.split(".")[0] for p in kwargs.get("packages", [])}
    for script in kwargs["entry_points"]["console_scripts"]:
        module = script.split("=")[1].split(":")[0].strip().split(".")[0]
        assert module in installed, f"{script!r} imports {module!r}, which setup() does not install"
