#!/usr/bin/env python3
"""
CodePulse Quick Start Example

This example demonstrates how to use CodePulse programmatically
to analyze code and get results.
"""

from pathlib import Path
from src.analyzers.java import JVMAnalyzer, Java21Analyzer
from src.analyzers.javascript import NodeJSAnalyzer, NextJSAnalyzer
from src.reporters import ConsoleReporter, JSONReporter, HTMLReporter


def example_java_analysis():
    """Example: Analyze Java code for performance issues."""
    print("=" * 80)
    print("Example 1: Java Performance Analysis")
    print("=" * 80)

    # Create analyzer
    analyzer = JVMAnalyzer()

    # Analyze directory
    project_path = Path("./examples/java")
    result = analyzer.analyze_directory(project_path)

    # Output to console
    reporter = ConsoleReporter(use_colors=True, verbose=False)
    reporter.report(result)

    print(f"\nAnalyzed {result.files_analyzed} files with {len(result.issues)} issues found")


def example_java21_modernization():
    """Example: Analyze Java code for Java 21 modernization opportunities."""
    print("\n" + "=" * 80)
    print("Example 2: Java 21 Modernization Analysis")
    print("=" * 80)

    # Create analyzer
    analyzer = Java21Analyzer()

    # Analyze directory
    project_path = Path("./examples/java21.java")
    result = analyzer.analyze_directory(project_path.parent)

    # Quick summary
    reporter = ConsoleReporter(use_colors=True)
    reporter.print_quick_summary(result)


def example_nodejs_analysis():
    """Example: Analyze Node.js code for anti-patterns."""
    print("\n" + "=" * 80)
    print("Example 3: Node.js Anti-Pattern Analysis")
    print("=" * 80)

    # Create analyzer
    analyzer = NodeJSAnalyzer()

    # Analyze directory
    project_path = Path("./examples/nodejs")
    result = analyzer.analyze_directory(project_path)

    # Output to JSON file
    json_reporter = JSONReporter(pretty=True)
    output_file = Path("./reports/nodejs-analysis.json")
    json_reporter.report(result, output_file)

    print(f"JSON report saved to: {output_file}")


def example_nextjs_analysis():
    """Example: Analyze Next.js code for optimization opportunities."""
    print("\n" + "=" * 80)
    print("Example 4: Next.js Optimization Analysis")
    print("=" * 80)

    # Create analyzer
    analyzer = NextJSAnalyzer()

    # Analyze directory
    project_path = Path("./examples/next.js")
    result = analyzer.analyze_directory(project_path)

    # Generate HTML report
    html_reporter = HTMLReporter()
    output_file = Path("./reports/nextjs-report.html")
    html_reporter.report(result, output_file)

    print(f"HTML report saved to: {output_file}")


def example_multiple_analyzers():
    """Example: Run multiple analyzers on the same codebase."""
    print("\n" + "=" * 80)
    print("Example 5: Multiple Analyzers")
    print("=" * 80)

    # Create multiple analyzers
    analyzers = [
        JVMAnalyzer(),
        Java21Analyzer(),
    ]

    # Analyze with all analyzers
    project_path = Path("./examples/java")
    all_results = []

    for analyzer in analyzers:
        print(f"\nRunning {analyzer.name}...")
        result = analyzer.analyze_directory(project_path)
        all_results.append(result)

    # Combine results
    total_issues = sum(len(r.issues) for r in all_results)
    print(f"\nTotal issues found across all analyzers: {total_issues}")


def example_custom_patterns():
    """Example: Add custom detection patterns."""
    print("\n" + "=" * 80)
    print("Example 6: Custom Patterns")
    print("=" * 80)

    from src.core import Pattern, Category, Severity

    # Create analyzer
    analyzer = JVMAnalyzer()

    # Add custom pattern
    custom_pattern = Pattern(
        name="custom_logger_usage",
        regex=r'System\.(out|err)\.print',
        category=Category.BEST_PRACTICE,
        severity=Severity.MEDIUM,
        description="Using System.out/err instead of logger",
        impact="Poor logging practices, hard to control output",
        solution="Use slf4j or Log4j2 for proper logging"
    )

    analyzer.add_pattern(custom_pattern)

    print(f"Added custom pattern: {custom_pattern.name}")
    print(f"Total patterns: {len(analyzer.patterns)}")


def example_filtering_results():
    """Example: Filter and process analysis results."""
    print("\n" + "=" * 80)
    print("Example 7: Filtering Results")
    print("=" * 80)

    from src.core import Severity, Category

    # Analyze
    analyzer = JVMAnalyzer()
    project_path = Path("./examples/java")
    result = analyzer.analyze_directory(project_path)

    # Filter critical issues only
    critical_issues = result.get_issues_by_severity(Severity.CRITICAL)
    print(f"Critical issues: {len(critical_issues)}")

    # Filter by category
    perf_issues = result.get_issues_by_category(Category.PERFORMANCE)
    print(f"Performance issues: {len(perf_issues)}")

    # Custom filtering
    db_issues = [i for i in result.issues if 'repository' in i.description.lower()]
    print(f"Database-related issues: {len(db_issues)}")


def main():
    """Run all examples."""
    print("\n🔍 CodePulse Examples - Quick Start Guide\n")

    try:
        example_java_analysis()
        example_java21_modernization()
        example_nodejs_analysis()
        example_nextjs_analysis()
        example_multiple_analyzers()
        example_custom_patterns()
        example_filtering_results()

        print("\n" + "=" * 80)
        print("✓ All examples completed successfully!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
