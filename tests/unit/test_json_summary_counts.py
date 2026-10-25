"""Regression: the JSON summary must count issues per severity."""
import json

from core import AnalysisResult, Category, Issue, Severity
from reporters import JSONReporter


def issue(sev):
    return Issue(category=Category.PERFORMANCE, severity=sev, file_path="A.java", line_number=1,
                 code_snippet="x", description="d", potential_impact="i")


def test_summary_counts_by_severity():
    result = AnalysisResult(issues=[issue(Severity.CRITICAL), issue(Severity.HIGH), issue(Severity.HIGH),
                                    issue(Severity.MEDIUM)], files_analyzed=1, total_lines=1)
    summary = json.loads(JSONReporter().report(result))["summary"]
    assert summary["total_issues"] == 4
    assert (summary["critical_issues"], summary["high_issues"], summary["medium_issues"], summary["low_issues"]) == (1, 2, 1, 0)
