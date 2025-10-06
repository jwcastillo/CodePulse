#!/usr/bin/env python3
"""
JSON Reporter - outputs analysis results in JSON format.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from core import AnalysisResult


class JSONReporter:
    """
    Formats and outputs analysis results as JSON.
    """

    def __init__(self, pretty: bool = True):
        """
        Initialize JSON reporter.

        Args:
            pretty: Whether to pretty-print JSON output
        """
        self.pretty = pretty

    def report(self, result: AnalysisResult, output_file: Optional[Path] = None) -> str:
        """
        Convert analysis results to JSON.

        Args:
            result: AnalysisResult to convert
            output_file: Optional file path to write JSON to

        Returns:
            JSON string
        """
        data = self._build_json_structure(result)
        json_str = self._serialize(data)

        if output_file:
            self._write_file(json_str, output_file)

        return json_str

    def _build_json_structure(self, result: AnalysisResult) -> dict:
        """
        Build JSON-serializable structure from result.

        Args:
            result: AnalysisResult to convert

        Returns:
            Dictionary ready for JSON serialization
        """
        return {
            "metadata": {
                **result.metadata,
                "generated_at": datetime.now().isoformat(),
                "codepulse_version": "2.0.0"
            },
            "summary": {
                "files_analyzed": result.files_analyzed,
                "total_lines": result.total_lines,
                "total_issues": len(result.issues),
                "critical_issues": len(result.get_issues_by_severity("CRITICAL")),
                "high_issues": len(result.get_issues_by_severity("HIGH")),
                "medium_issues": len(result.get_issues_by_severity("MEDIUM")),
                "low_issues": len(result.get_issues_by_severity("LOW")),
                "has_critical": result.has_critical_issues()
            },
            "statistics": result.stats,
            "issues": [issue.to_dict() for issue in result.issues]
        }

    def _serialize(self, data: dict) -> str:
        """
        Serialize data to JSON string.

        Args:
            data: Data to serialize

        Returns:
            JSON string
        """
        if self.pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)

    def _write_file(self, json_str: str, output_file: Path) -> None:
        """
        Write JSON string to file.

        Args:
            json_str: JSON content
            output_file: Path to output file
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json_str, encoding='utf-8')

    def print_to_console(self, result: AnalysisResult) -> None:
        """
        Print JSON to console.

        Args:
            result: AnalysisResult to output
        """
        json_str = self.report(result)
        print(json_str)
