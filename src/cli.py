#!/usr/bin/env python3
"""
CodePulse CLI - Command-line interface for code analysis.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

from core import BaseAnalyzer
from analyzers.java import JVMAnalyzer, Java17Analyzer, Java21Analyzer
from analyzers.javascript import NodeJSAnalyzer, NextJSAnalyzer
from reporters import ConsoleReporter, JSONReporter, HTMLReporter


class CodePulseCLI:
    """Main CLI application for CodePulse."""

    ANALYZERS = {
        'jvm': JVMAnalyzer,
        'java17': Java17Analyzer,
        'java21': Java21Analyzer,
        'nodejs': NodeJSAnalyzer,
        'nextjs': NextJSAnalyzer,
    }

    def __init__(self):
        """Initialize CLI."""
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description='CodePulse - Advanced Code Quality Analysis Tool',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Analyze Java code with JVM optimizer
  codepulse analyze --analyzer jvm /path/to/java/project

  # Analyze with Java 21 modernization suggestions
  codepulse analyze --analyzer java21 /path/to/project

  # Analyze Node.js code
  codepulse analyze --analyzer nodejs /path/to/nodejs/app

  # Analyze Next.js code with HTML report
  codepulse analyze --analyzer nextjs --output report.html /path/to/nextjs/app

  # Run multiple analyzers
  codepulse analyze --analyzer jvm,java21 /path/to/project

  # JSON output for CI/CD
  codepulse analyze --analyzer jvm --format json --output results.json /path/to/project
            """
        )

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze code')
        analyze_parser.add_argument(
            'directory',
            type=Path,
            help='Directory to analyze'
        )
        analyze_parser.add_argument(
            '-a', '--analyzer',
            required=True,
            help=f'Analyzer to use (comma-separated): {", ".join(self.ANALYZERS.keys())}'
        )
        analyze_parser.add_argument(
            '-f', '--format',
            choices=['console', 'json', 'html'],
            default='console',
            help='Output format (default: console)'
        )
        analyze_parser.add_argument(
            '-o', '--output',
            type=Path,
            help='Output file (for json/html formats)'
        )
        analyze_parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Verbose output'
        )
        analyze_parser.add_argument(
            '--no-color',
            action='store_true',
            help='Disable colored output'
        )
        analyze_parser.add_argument(
            '--fail-on-critical',
            action='store_true',
            help='Exit with code 1 if critical issues found (for CI)'
        )

        # List command
        list_parser = subparsers.add_parser('list', help='List available analyzers')

        # Version command
        version_parser = subparsers.add_parser('version', help='Show version')

        return parser

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run CLI application.

        Args:
            args: Command-line arguments (defaults to sys.argv[1:])

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        parsed_args = self.parser.parse_args(args)

        if not parsed_args.command:
            self.parser.print_help()
            return 0

        if parsed_args.command == 'analyze':
            return self._handle_analyze(parsed_args)
        elif parsed_args.command == 'list':
            return self._handle_list()
        elif parsed_args.command == 'version':
            return self._handle_version()

        return 0

    def _handle_analyze(self, args) -> int:
        """Handle analyze command."""
        # Validate directory
        if not args.directory.exists():
            print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
            return 1

        if not args.directory.is_dir():
            print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
            return 1

        # Parse analyzers
        analyzer_names = [name.strip() for name in args.analyzer.split(',')]
        analyzers = []

        for name in analyzer_names:
            if name not in self.ANALYZERS:
                print(f"Error: Unknown analyzer: {name}", file=sys.stderr)
                print(f"Available analyzers: {', '.join(self.ANALYZERS.keys())}", file=sys.stderr)
                return 1
            analyzers.append(self.ANALYZERS[name]())

        # Run analysis
        all_issues = []
        total_files = 0
        total_lines = 0

        for analyzer in analyzers:
            if args.verbose:
                print(f"Running {analyzer.name}...")

            result = analyzer.analyze_directory(args.directory)
            all_issues.extend(result.issues)
            total_files = max(total_files, result.files_analyzed)
            total_lines = max(total_lines, result.total_lines)

        # Create combined result
        from core import AnalysisResult
        combined_result = AnalysisResult(
            issues=all_issues,
            files_analyzed=total_files,
            total_lines=total_lines
        )
        combined_result.metadata['analyzers'] = [a.name for a in analyzers]
        combined_result.metadata['directory'] = str(args.directory)

        # Output results
        if args.format == 'console':
            reporter = ConsoleReporter(
                use_colors=not args.no_color,
                verbose=args.verbose
            )
            reporter.report(combined_result)

        elif args.format == 'json':
            reporter = JSONReporter(pretty=True)
            if args.output:
                reporter.report(combined_result, args.output)
                print(f"JSON report written to: {args.output}")
            else:
                reporter.print_to_console(combined_result)

        elif args.format == 'html':
            if not args.output:
                print("Error: --output required for HTML format", file=sys.stderr)
                return 1
            reporter = HTMLReporter()
            reporter.report(combined_result, args.output)

        # Check for critical issues
        if args.fail_on_critical and combined_result.has_critical_issues():
            return 1

        return 0

    def _handle_list(self) -> int:
        """Handle list command."""
        print("Available Analyzers:\n")
        for name, analyzer_class in self.ANALYZERS.items():
            analyzer = analyzer_class()
            extensions = ', '.join(sorted(analyzer.get_file_extensions()))
            print(f"  {name:12} - {analyzer.name}")
            print(f"               Files: {extensions}\n")
        return 0

    def _handle_version(self) -> int:
        """Handle version command."""
        print("CodePulse v2.0.0")
        print("Advanced Code Quality Analysis Tool")
        return 0


def main():
    """Main entry point."""
    cli = CodePulseCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
