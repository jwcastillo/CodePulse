#!/usr/bin/env python3
"""
Console Reporter - outputs analysis results to terminal with color and formatting.
"""

from typing import List
from collections import defaultdict

from core import AnalysisResult, Issue, Severity, Category


class ConsoleReporter:
    """
    Formats and outputs analysis results to console with colors and structure.
    """

    # ANSI color codes
    COLORS = {
        'CRITICAL': '\033[91m',  # Red
        'HIGH': '\033[93m',      # Yellow
        'MEDIUM': '\033[94m',    # Blue
        'LOW': '\033[92m',       # Green
        'INFO': '\033[96m',      # Cyan
        'RESET': '\033[0m',
        'BOLD': '\033[1m',
        'DIM': '\033[2m',
    }

    def __init__(self, use_colors: bool = True, verbose: bool = False):
        """
        Initialize console reporter.

        Args:
            use_colors: Whether to use ANSI colors
            verbose: Whether to show detailed information
        """
        self.use_colors = use_colors
        self.verbose = verbose

    def report(self, result: AnalysisResult) -> None:
        """
        Output analysis results to console.

        Args:
            result: AnalysisResult to display
        """
        self._print_header(result)
        self._print_summary(result)
        self._print_issues_by_severity(result)

        if self.verbose:
            self._print_issues_by_category(result)

        self._print_footer(result)

    def _print_header(self, result: AnalysisResult) -> None:
        """Print report header."""
        analyzer_name = result.metadata.get('analyzer', 'Code Analyzer')
        directory = result.metadata.get('directory', 'N/A')

        print(self._colorize("\n" + "=" * 80, 'BOLD'))
        print(self._colorize(f"  CodePulse Analysis Report - {analyzer_name}", 'BOLD'))
        print(self._colorize("=" * 80, 'BOLD'))
        print(f"  Directory: {directory}")
        print(f"  Files Analyzed: {result.files_analyzed}")
        print(f"  Total Lines: {result.total_lines:,}")
        print()

    def _print_summary(self, result: AnalysisResult) -> None:
        """Print summary statistics."""
        print(self._colorize("SUMMARY", 'BOLD'))
        print(self._colorize("-" * 80, 'DIM'))

        critical = len(result.get_issues_by_severity(Severity.CRITICAL))
        high = len(result.get_issues_by_severity(Severity.HIGH))
        medium = len(result.get_issues_by_severity(Severity.MEDIUM))
        low = len(result.get_issues_by_severity(Severity.LOW))
        total = len(result.issues)

        print(f"  {Severity.CRITICAL.emoji}  CRITICAL: {self._colorize(str(critical), 'CRITICAL')}")
        print(f"  {Severity.HIGH.emoji}  HIGH:     {self._colorize(str(high), 'HIGH')}")
        print(f"  {Severity.MEDIUM.emoji}  MEDIUM:   {self._colorize(str(medium), 'MEDIUM')}")
        print(f"  {Severity.LOW.emoji}  LOW:      {self._colorize(str(low), 'LOW')}")
        print(self._colorize("-" * 80, 'DIM'))
        print(f"  Total Issues: {self._colorize(str(total), 'BOLD')}")
        print()

    def _print_issues_by_severity(self, result: AnalysisResult) -> None:
        """Print issues grouped by severity."""
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            issues = result.get_issues_by_severity(severity)
            if not issues:
                continue

            print(self._colorize(f"\n{severity.emoji}  {severity.value} ISSUES ({len(issues)})", 'BOLD'))
            print(self._colorize("=" * 80, 'DIM'))

            for i, issue in enumerate(issues, 1):
                self._print_issue(issue, i)

    def _print_issue(self, issue: Issue, number: int) -> None:
        """Print a single issue."""
        print(f"\n  {number}. {self._colorize(issue.description, 'BOLD')}")
        print(f"     Category: {issue.category}")
        print(f"     Location: {issue.file_path}:{issue.line_number}")
        print(f"     Impact: {issue.potential_impact}")

        if issue.solution:
            print(f"     Solution: {issue.solution}")

        if self.verbose and issue.code_snippet:
            print("\n     Code:")
            for line in issue.code_snippet.split('\n'):
                print(f"       {self._colorize(line, 'DIM')}")

    def _print_issues_by_category(self, result: AnalysisResult) -> None:
        """Print issues grouped by category (verbose mode)."""
        print(self._colorize("\n\nISSUES BY CATEGORY", 'BOLD'))
        print(self._colorize("=" * 80, 'DIM'))

        category_counts = defaultdict(int)
        for issue in result.issues:
            category_counts[issue.category] += 1

        for category in sorted(category_counts.keys(), key=lambda c: str(c)):
            count = category_counts[category]
            print(f"  {category}: {count}")

    def _print_footer(self, result: AnalysisResult) -> None:
        """Print report footer."""
        print(self._colorize("\n" + "=" * 80, 'DIM'))

        if result.has_critical_issues():
            print(self._colorize("  ⚠️  CRITICAL ISSUES FOUND - Action Required!", 'CRITICAL'))
        else:
            print(self._colorize("  ✓ No critical issues found", 'LOW'))

        print(self._colorize("=" * 80 + "\n", 'DIM'))

    def _colorize(self, text: str, color_key: str) -> str:
        """
        Apply color to text.

        Args:
            text: Text to colorize
            color_key: Color key from COLORS dict

        Returns:
            Colorized text (or plain text if colors disabled)
        """
        if not self.use_colors:
            return text

        color = self.COLORS.get(color_key, '')
        reset = self.COLORS['RESET']
        return f"{color}{text}{reset}"

    def print_quick_summary(self, result: AnalysisResult) -> None:
        """
        Print a quick one-line summary.

        Args:
            result: AnalysisResult to summarize
        """
        critical = len(result.get_issues_by_severity(Severity.CRITICAL))
        high = len(result.get_issues_by_severity(Severity.HIGH))
        medium = len(result.get_issues_by_severity(Severity.MEDIUM))
        low = len(result.get_issues_by_severity(Severity.LOW))

        summary = f"Found {len(result.issues)} issues: "
        summary += f"{Severity.CRITICAL.emoji}{critical} "
        summary += f"{Severity.HIGH.emoji}{high} "
        summary += f"{Severity.MEDIUM.emoji}{medium} "
        summary += f"{Severity.LOW.emoji}{low}"

        print(summary)
