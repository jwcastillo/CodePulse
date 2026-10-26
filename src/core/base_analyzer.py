#!/usr/bin/env python3
"""
Base analyzer class providing common functionality for all code analyzers.

This module defines the abstract base class that all language-specific
analyzers should inherit from.
"""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional, Set
from collections import defaultdict

from .models import Issue, Pattern, AnalysisResult, Severity, Category


class BaseAnalyzer(ABC):
    """
    Abstract base class for all code analyzers.

    Provides common functionality for file scanning, pattern matching,
    and result aggregation. Language-specific analyzers should extend
    this class and implement the abstract methods.
    """

    def __init__(self, name: str):
        """
        Initialize the analyzer.

        Args:
            name: Human-readable name for this analyzer
        """
        self.name = name
        self.patterns: Dict[str, Pattern] = {}
        self.result = AnalysisResult()
        self.file_extensions: Set[str] = set()

    @abstractmethod
    def _init_patterns(self) -> Dict[str, Pattern]:
        """
        Initialize detection patterns for this analyzer.

        Returns:
            Dictionary mapping pattern names to Pattern objects

        This method must be implemented by subclasses to define
        the specific patterns they want to detect.
        """
        pass

    @abstractmethod
    def get_file_extensions(self) -> Set[str]:
        """
        Get the file extensions this analyzer handles.

        Returns:
            Set of file extensions (e.g., {'.java', '.kt'})
        """
        pass

    def analyze_directory(self, directory: Path) -> AnalysisResult:
        """
        Analyze all relevant files in a directory.

        Args:
            directory: Path to the directory to analyze

        Returns:
            AnalysisResult containing all found issues
        """
        self.result = AnalysisResult()
        self.result.metadata['analyzer'] = self.name
        self.result.metadata['directory'] = str(directory)

        # Initialize patterns
        self.patterns = self._init_patterns()
        self.file_extensions = self.get_file_extensions()

        # Scan and analyze files
        files = self._scan_files(directory)
        for file_path in files:
            self._analyze_file(file_path)

        return self.result

    def _scan_files(self, directory: Path) -> List[Path]:
        """
        Recursively scan directory for relevant files.

        Args:
            directory: Directory to scan

        Returns:
            List of file paths to analyze
        """
        files = []
        for ext in self.file_extensions:
            files.extend(directory.rglob(f"*{ext}"))
        return sorted(files)

    def _analyze_file(self, file_path: Path) -> None:
        """
        Analyze a single file for issues.

        Args:
            file_path: Path to the file to analyze
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            self.result.files_analyzed += 1
            self.result.total_lines += len(lines)

            # Apply all enabled patterns
            for pattern_name, pattern in self.patterns.items():
                if pattern.enabled:
                    self._apply_pattern(file_path, lines, content, pattern)

        except Exception as e:
            # Log error but continue with other files
            if 'errors' not in self.result.metadata:
                self.result.metadata['errors'] = []
            self.result.metadata['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })

    @staticmethod
    def _display_path(file_path: Path) -> str:
        """Path relative to the cwd when possible; absolute otherwise.

        Analyzing a directory outside the cwd (or passing a relative path) used to raise
        ValueError here, which _analyze_file swallowed: the file was reported with 0 issues.
        """
        resolved = file_path.resolve()
        try:
            return str(resolved.relative_to(Path.cwd().resolve()))
        except ValueError:
            return str(resolved)

    def _apply_pattern(
        self,
        file_path: Path,
        lines: List[str],
        content: str,
        pattern: Pattern
    ) -> None:
        """
        Apply a detection pattern to file content.

        Args:
            file_path: Path to the file being analyzed
            lines: File content split into lines
            content: Full file content as string
            pattern: Pattern to apply
        """
        try:
            regex = re.compile(pattern.regex, re.MULTILINE | re.DOTALL)
            matches = regex.finditer(content)

            for match in matches:
                # Find line number of the match
                line_num = content[:match.start()].count('\n') + 1

                # Extract code snippet (current line + context)
                snippet = self._extract_snippet(lines, line_num)

                # Create issue
                issue = Issue(
                    category=pattern.category,
                    severity=pattern.severity,
                    file_path=self._display_path(file_path),
                    line_number=line_num,
                    code_snippet=snippet,
                    description=pattern.description,
                    potential_impact=pattern.impact,
                    solution=pattern.solution,
                    metadata={'pattern': pattern.name, **pattern.metadata}
                )

                self.result.add_issue(issue)

        except re.error as e:
            # Log regex compilation errors
            if 'pattern_errors' not in self.result.metadata:
                self.result.metadata['pattern_errors'] = []
            self.result.metadata['pattern_errors'].append({
                'pattern': pattern.name,
                'error': str(e)
            })

    def _extract_snippet(
        self,
        lines: List[str],
        line_num: int,
        context: int = 2
    ) -> str:
        """
        Extract code snippet with context lines.

        Args:
            lines: All lines in the file
            line_num: Target line number (1-indexed)
            context: Number of context lines before/after

        Returns:
            Code snippet as string
        """
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)

        snippet_lines = []
        for i in range(start, end):
            prefix = "→ " if i == line_num - 1 else "  "
            snippet_lines.append(f"{prefix}{lines[i]}")

        return '\n'.join(snippet_lines)

    def add_pattern(self, pattern: Pattern) -> None:
        """
        Add a detection pattern to this analyzer.

        Args:
            pattern: Pattern to add
        """
        self.patterns[pattern.name] = pattern

    def remove_pattern(self, pattern_name: str) -> None:
        """
        Remove a detection pattern.

        Args:
            pattern_name: Name of the pattern to remove
        """
        if pattern_name in self.patterns:
            del self.patterns[pattern_name]

    def disable_pattern(self, pattern_name: str) -> None:
        """
        Disable a pattern without removing it.

        Args:
            pattern_name: Name of the pattern to disable
        """
        if pattern_name in self.patterns:
            self.patterns[pattern_name].enabled = False

    def enable_pattern(self, pattern_name: str) -> None:
        """
        Enable a previously disabled pattern.

        Args:
            pattern_name: Name of the pattern to enable
        """
        if pattern_name in self.patterns:
            self.patterns[pattern_name].enabled = True

    def get_summary(self) -> Dict[str, any]:
        """
        Get a summary of analysis results.

        Returns:
            Dictionary with summary statistics
        """
        return {
            'analyzer': self.name,
            'files_analyzed': self.result.files_analyzed,
            'total_lines': self.result.total_lines,
            'total_issues': len(self.result.issues),
            'critical_issues': len(self.result.get_issues_by_severity(Severity.CRITICAL)),
            'high_issues': len(self.result.get_issues_by_severity(Severity.HIGH)),
            'medium_issues': len(self.result.get_issues_by_severity(Severity.MEDIUM)),
            'low_issues': len(self.result.get_issues_by_severity(Severity.LOW)),
            'has_critical': self.result.has_critical_issues()
        }
