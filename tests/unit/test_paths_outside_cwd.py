"""Regression: analyzing a directory outside the cwd must still report issues."""
import os
from pathlib import Path

from analyzers.java.jvm_analyzer import JVMAnalyzer

JAVA = """public class S {
    String join(java.util.List<String> xs) {
        String out = "";
        for (String x : xs) { out += x + ","; }
        return out;
    }
}
"""


def test_directory_outside_cwd(tmp_path, monkeypatch):
    (tmp_path / "S.java").write_text(JAVA)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)  # target dir is NOT under the cwd
    result = JVMAnalyzer().analyze_directory(tmp_path)
    assert "errors" not in result.metadata, result.metadata.get("errors")
    assert any(i.metadata.get("pattern") == "string_concat_loop" for i in result.issues)


def test_relative_directory(tmp_path, monkeypatch):
    (tmp_path / "S.java").write_text(JAVA)
    monkeypatch.chdir(tmp_path)
    result = JVMAnalyzer().analyze_directory(Path("."))
    assert "errors" not in result.metadata, result.metadata.get("errors")
    assert result.issues
