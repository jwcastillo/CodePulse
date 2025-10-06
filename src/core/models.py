#!/usr/bin/env python3
"""
Core data models for CodePulse analyzer.

This module defines the fundamental data structures used across all analyzers.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

    def __str__(self) -> str:
        return self.value

    @property
    def emoji(self) -> str:
        """Get emoji representation for severity."""
        emoji_map = {
            Severity.CRITICAL: "🔴",
            Severity.HIGH: "🟠",
            Severity.MEDIUM: "🟡",
            Severity.LOW: "🟢",
            Severity.INFO: "ℹ️"
        }
        return emoji_map.get(self, "")


class Category(Enum):
    """Issue categories for classification."""
    PERFORMANCE = "Performance"
    MEMORY = "Memory"
    SECURITY = "Security"
    DATABASE = "Database"
    CONCURRENCY = "Concurrency"
    CODE_SMELL = "Code Smell"
    BEST_PRACTICE = "Best Practice"
    MODERNIZATION = "Modernization"
    BUNDLE_SIZE = "Bundle Size"
    EVENT_LOOP = "Event Loop"
    API_DESIGN = "API Design"

    def __str__(self) -> str:
        return self.value


@dataclass
class Issue:
    """
    Represents a code quality issue found during analysis.

    Attributes:
        category: The issue category (performance, security, etc.)
        severity: The severity level of the issue
        file_path: Path to the file containing the issue
        line_number: Line number where the issue was found
        code_snippet: The problematic code snippet
        description: Human-readable description of the issue
        potential_impact: Expected impact if the issue is fixed
        solution: Recommended solution or fix (optional)
        metadata: Additional context-specific data (optional)
    """
    category: Category
    severity: Severity
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    potential_impact: str
    solution: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize issue data."""
        # Convert string severity to Severity enum if needed
        if isinstance(self.severity, str):
            self.severity = Severity[self.severity.upper()]

        # Convert string category to Category enum if needed
        if isinstance(self.category, str):
            # Try to match by value first, then by name
            try:
                self.category = next(c for c in Category if c.value == self.category)
            except StopIteration:
                self.category = Category[self.category.upper().replace(" ", "_")]

    @property
    def severity_emoji(self) -> str:
        """Get emoji representation of severity."""
        return self.severity.emoji

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary for serialization."""
        return {
            "category": str(self.category),
            "severity": str(self.severity),
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "description": self.description,
            "potential_impact": self.potential_impact,
            "solution": self.solution,
            "metadata": self.metadata
        }


@dataclass
class Pattern:
    """
    Represents a detection pattern for code analysis.

    Attributes:
        name: Unique identifier for the pattern
        regex: Regular expression pattern to match
        category: Issue category this pattern detects
        severity: Severity level for issues found by this pattern
        description: Description of what this pattern detects
        impact: Expected impact/improvement if addressed
        solution: Recommended solution (optional)
        enabled: Whether this pattern is active (default: True)
        metadata: Additional pattern-specific configuration
    """
    name: str
    regex: str
    category: Category
    severity: Severity
    description: str
    impact: str
    solution: str = ""
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize pattern data."""
        if isinstance(self.severity, str):
            self.severity = Severity[self.severity.upper()]
        if isinstance(self.category, str):
            try:
                self.category = next(c for c in Category if c.value == self.category)
            except StopIteration:
                self.category = Category[self.category.upper().replace(" ", "_")]


@dataclass
class AnalysisResult:
    """
    Contains the complete results of a code analysis run.

    Attributes:
        issues: List of all issues found
        files_analyzed: Number of files analyzed
        total_lines: Total lines of code analyzed
        stats: Statistics grouped by category and severity
        metadata: Additional analysis metadata (duration, config, etc.)
    """
    issues: List[Issue] = field(default_factory=list)
    files_analyzed: int = 0
    total_lines: int = 0
    stats: Dict[str, Dict[str, int]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_issue(self, issue: Issue) -> None:
        """Add an issue and update statistics."""
        self.issues.append(issue)

        # Update stats
        cat_str = str(issue.category)
        sev_str = str(issue.severity)

        if cat_str not in self.stats:
            self.stats[cat_str] = {}
        if sev_str not in self.stats[cat_str]:
            self.stats[cat_str][sev_str] = 0

        self.stats[cat_str][sev_str] += 1

    def get_issues_by_severity(self, severity: Severity) -> List[Issue]:
        """Get all issues of a specific severity level."""
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_category(self, category: Category) -> List[Issue]:
        """Get all issues in a specific category."""
        return [issue for issue in self.issues if issue.category == category]

    def has_critical_issues(self) -> bool:
        """Check if any critical issues were found."""
        return any(issue.severity == Severity.CRITICAL for issue in self.issues)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "issues": [issue.to_dict() for issue in self.issues],
            "files_analyzed": self.files_analyzed,
            "total_lines": self.total_lines,
            "stats": self.stats,
            "metadata": self.metadata
        }
