#!/usr/bin/env python3
"""
Unit tests for core models.
"""

import pytest
from src.core.models import Issue, Pattern, AnalysisResult, Severity, Category


class TestSeverity:
    """Test Severity enum."""

    def test_severity_values(self):
        """Test severity enum values."""
        assert str(Severity.CRITICAL) == "CRITICAL"
        assert str(Severity.HIGH) == "HIGH"
        assert str(Severity.MEDIUM) == "MEDIUM"
        assert str(Severity.LOW) == "LOW"

    def test_severity_emoji(self):
        """Test severity emoji property."""
        assert Severity.CRITICAL.emoji == "🔴"
        assert Severity.HIGH.emoji == "🟠"
        assert Severity.MEDIUM.emoji == "🟡"
        assert Severity.LOW.emoji == "🟢"


class TestCategory:
    """Test Category enum."""

    def test_category_values(self):
        """Test category enum values."""
        assert str(Category.PERFORMANCE) == "Performance"
        assert str(Category.MEMORY) == "Memory"
        assert str(Category.SECURITY) == "Security"
        assert str(Category.DATABASE) == "Database"


class TestIssue:
    """Test Issue dataclass."""

    def test_issue_creation(self):
        """Test creating an issue."""
        issue = Issue(
            category=Category.PERFORMANCE,
            severity=Severity.HIGH,
            file_path="test.java",
            line_number=42,
            code_snippet="for(int i=0; i<n; i++)",
            description="Test issue",
            potential_impact="High impact",
            solution="Fix it"
        )

        assert issue.category == Category.PERFORMANCE
        assert issue.severity == Severity.HIGH
        assert issue.file_path == "test.java"
        assert issue.line_number == 42

    def test_issue_from_strings(self):
        """Test creating issue from string values."""
        issue = Issue(
            category="Performance",
            severity="HIGH",
            file_path="test.java",
            line_number=1,
            code_snippet="code",
            description="desc",
            potential_impact="impact"
        )

        assert isinstance(issue.category, Category)
        assert isinstance(issue.severity, Severity)
        assert issue.severity == Severity.HIGH

    def test_issue_to_dict(self):
        """Test converting issue to dictionary."""
        issue = Issue(
            category=Category.SECURITY,
            severity=Severity.CRITICAL,
            file_path="app.js",
            line_number=10,
            code_snippet="eval()",
            description="Dangerous eval",
            potential_impact="Code injection",
            solution="Never use eval"
        )

        data = issue.to_dict()
        assert data['category'] == "Security"
        assert data['severity'] == "CRITICAL"
        assert data['file_path'] == "app.js"
        assert data['line_number'] == 10


class TestPattern:
    """Test Pattern dataclass."""

    def test_pattern_creation(self):
        """Test creating a pattern."""
        pattern = Pattern(
            name="test_pattern",
            regex=r"test.*pattern",
            category=Category.CODE_SMELL,
            severity=Severity.LOW,
            description="Test pattern",
            impact="Low impact",
            solution="Refactor"
        )

        assert pattern.name == "test_pattern"
        assert pattern.regex == r"test.*pattern"
        assert pattern.enabled is True

    def test_pattern_disabled(self):
        """Test disabled pattern."""
        pattern = Pattern(
            name="disabled",
            regex=r"test",
            category=Category.PERFORMANCE,
            severity=Severity.MEDIUM,
            description="Disabled",
            impact="None",
            enabled=False
        )

        assert pattern.enabled is False


class TestAnalysisResult:
    """Test AnalysisResult dataclass."""

    def test_empty_result(self):
        """Test empty analysis result."""
        result = AnalysisResult()

        assert len(result.issues) == 0
        assert result.files_analyzed == 0
        assert result.total_lines == 0
        assert result.has_critical_issues() is False

    def test_add_issue(self):
        """Test adding issues to result."""
        result = AnalysisResult()

        issue1 = Issue(
            category=Category.PERFORMANCE,
            severity=Severity.CRITICAL,
            file_path="test.java",
            line_number=1,
            code_snippet="code",
            description="Issue 1",
            potential_impact="High"
        )

        issue2 = Issue(
            category=Category.MEMORY,
            severity=Severity.HIGH,
            file_path="test.java",
            line_number=2,
            code_snippet="code",
            description="Issue 2",
            potential_impact="Medium"
        )

        result.add_issue(issue1)
        result.add_issue(issue2)

        assert len(result.issues) == 2
        assert result.has_critical_issues() is True

    def test_get_issues_by_severity(self):
        """Test filtering issues by severity."""
        result = AnalysisResult()

        critical_issue = Issue(
            category=Category.SECURITY,
            severity=Severity.CRITICAL,
            file_path="test.java",
            line_number=1,
            code_snippet="code",
            description="Critical",
            potential_impact="High"
        )

        low_issue = Issue(
            category=Category.CODE_SMELL,
            severity=Severity.LOW,
            file_path="test.java",
            line_number=2,
            code_snippet="code",
            description="Low",
            potential_impact="Low"
        )

        result.add_issue(critical_issue)
        result.add_issue(low_issue)

        critical_issues = result.get_issues_by_severity(Severity.CRITICAL)
        assert len(critical_issues) == 1
        assert critical_issues[0].description == "Critical"

        low_issues = result.get_issues_by_severity(Severity.LOW)
        assert len(low_issues) == 1

    def test_get_issues_by_category(self):
        """Test filtering issues by category."""
        result = AnalysisResult()

        perf_issue = Issue(
            category=Category.PERFORMANCE,
            severity=Severity.HIGH,
            file_path="test.java",
            line_number=1,
            code_snippet="code",
            description="Performance",
            potential_impact="High"
        )

        security_issue = Issue(
            category=Category.SECURITY,
            severity=Severity.CRITICAL,
            file_path="test.java",
            line_number=2,
            code_snippet="code",
            description="Security",
            potential_impact="Critical"
        )

        result.add_issue(perf_issue)
        result.add_issue(security_issue)

        perf_issues = result.get_issues_by_category(Category.PERFORMANCE)
        assert len(perf_issues) == 1
        assert perf_issues[0].description == "Performance"

    def test_statistics(self):
        """Test statistics calculation."""
        result = AnalysisResult()

        issue = Issue(
            category=Category.PERFORMANCE,
            severity=Severity.CRITICAL,
            file_path="test.java",
            line_number=1,
            code_snippet="code",
            description="Test",
            potential_impact="High"
        )

        result.add_issue(issue)

        assert "Performance" in result.stats
        assert "CRITICAL" in result.stats["Performance"]
        assert result.stats["Performance"]["CRITICAL"] == 1

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = AnalysisResult()
        result.files_analyzed = 10
        result.total_lines = 1000

        data = result.to_dict()
        assert data['files_analyzed'] == 10
        assert data['total_lines'] == 1000
        assert 'issues' in data
        assert 'stats' in data
