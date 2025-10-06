#!/usr/bin/env python3
"""
Example: Spring Framework Analysis

This example demonstrates how to analyze Spring applications for:
- Spring Data JPA anti-patterns
- Spring Security vulnerabilities
- Spring REST API issues
"""

from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.java.spring_data_analyzer import SpringDataAnalyzer
from analyzers.java.spring_security_analyzer import SpringSecurityAnalyzer
from analyzers.java.spring_rest_analyzer import SpringRestAnalyzer
from reporters import ConsoleReporter, HTMLReporter, JSONReporter
from core.models import AnalysisResult, Severity, Category


def analyze_spring_data(directory: Path):
    """Analyze Spring Data JPA code for performance issues."""
    print("\n" + "="*80)
    print("  Spring Data JPA Analysis")
    print("="*80 + "\n")

    analyzer = SpringDataAnalyzer()
    result = analyzer.analyze_directory(directory)

    # Show results
    reporter = ConsoleReporter(use_colors=True, verbose=True)
    reporter.report(result)

    # Show N+1 query issues specifically
    n_plus_one = [
        issue for issue in result.issues
        if 'N+1' in issue.description or 'loop' in issue.description.lower()
    ]

    if n_plus_one:
        print(f"\n⚠️  Found {len(n_plus_one)} N+1 query issues:")
        for issue in n_plus_one[:3]:  # Show first 3
            print(f"   - {issue.file_path}:{issue.line_number}")
            print(f"     {issue.description}")
            print(f"     Solution: {issue.solution}\n")

    return result


def analyze_spring_security(directory: Path):
    """Analyze Spring Security configuration for vulnerabilities."""
    print("\n" + "="*80)
    print("  Spring Security Analysis")
    print("="*80 + "\n")

    analyzer = SpringSecurityAnalyzer()
    result = analyzer.analyze_directory(directory)

    # Show results
    reporter = ConsoleReporter(use_colors=True, verbose=True)
    reporter.report(result)

    # Show critical security issues
    critical_security = result.get_issues_by_severity(Severity.CRITICAL)

    if critical_security:
        print(f"\n🔴 CRITICAL: Found {len(critical_security)} critical security issues!")
        for issue in critical_security[:5]:  # Show first 5
            print(f"\n   {issue.description}")
            print(f"   Location: {issue.file_path}:{issue.line_number}")
            print(f"   Impact: {issue.potential_impact}")
            print(f"   Solution: {issue.solution}")

    return result


def analyze_spring_rest(directory: Path):
    """Analyze Spring REST APIs for design issues."""
    print("\n" + "="*80)
    print("  Spring REST API Analysis")
    print("="*80 + "\n")

    analyzer = SpringRestAnalyzer()
    result = analyzer.analyze_directory(directory)

    # Show results
    reporter = ConsoleReporter(use_colors=True, verbose=True)
    reporter.report(result)

    # Show validation and error handling issues
    validation_issues = [
        issue for issue in result.issues
        if 'valid' in issue.description.lower() or
           'error' in issue.description.lower()
    ]

    if validation_issues:
        print(f"\n⚠️  Found {len(validation_issues)} validation/error handling issues:")
        for issue in validation_issues[:3]:  # Show first 3
            print(f"   - {issue.description}")
            print(f"     at {issue.file_path}:{issue.line_number}\n")

    return result


def analyze_all_spring(directory: Path):
    """Run all Spring analyzers and combine results."""
    print("\n" + "="*80)
    print("  Complete Spring Framework Analysis")
    print("="*80 + "\n")

    # Run all analyzers
    data_result = SpringDataAnalyzer().analyze_directory(directory)
    security_result = SpringSecurityAnalyzer().analyze_directory(directory)
    rest_result = SpringRestAnalyzer().analyze_directory(directory)

    # Combine results
    all_issues = data_result.issues + security_result.issues + rest_result.issues
    combined = AnalysisResult(issues=all_issues)

    # Statistics
    critical = combined.get_issues_by_severity(Severity.CRITICAL)
    high = combined.get_issues_by_severity(Severity.HIGH)
    medium = combined.get_issues_by_severity(Severity.MEDIUM)
    low = combined.get_issues_by_severity(Severity.LOW)

    print(f"Total Issues Found: {len(all_issues)}")
    print(f"  🔴 CRITICAL: {len(critical)}")
    print(f"  🟠 HIGH:     {len(high)}")
    print(f"  🟡 MEDIUM:   {len(medium)}")
    print(f"  🟢 LOW:      {len(low)}\n")

    # Show breakdown by category
    performance = combined.get_issues_by_category(Category.PERFORMANCE)
    security = combined.get_issues_by_category(Category.SECURITY)
    database = combined.get_issues_by_category(Category.DATABASE)

    print("Issues by Category:")
    print(f"  ⚡ Performance: {len(performance)}")
    print(f"  🔒 Security:    {len(security)}")
    print(f"  💾 Database:    {len(database)}\n")

    # Generate reports
    print("Generating reports...\n")

    # Console report
    ConsoleReporter(use_colors=True, verbose=True).report(combined)

    # HTML report
    html_path = Path("./spring-analysis-report.html")
    HTMLReporter().report(combined, html_path)
    print(f"✅ HTML report saved to: {html_path}")

    # JSON report (for CI/CD)
    json_path = Path("./spring-analysis.json")
    JSONReporter().report(combined, json_path)
    print(f"✅ JSON report saved to: {json_path}")

    return combined


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python spring_analysis.py <directory> [analyzer]")
        print("\nAnalyzers:")
        print("  data     - Spring Data JPA only")
        print("  security - Spring Security only")
        print("  rest     - Spring REST API only")
        print("  all      - All Spring analyzers (default)")
        print("\nExample:")
        print("  python spring_analysis.py ./src all")
        sys.exit(1)

    directory = Path(sys.argv[1])
    analyzer_type = sys.argv[2] if len(sys.argv) > 2 else 'all'

    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    if analyzer_type == 'data':
        result = analyze_spring_data(directory)
    elif analyzer_type == 'security':
        result = analyze_spring_security(directory)
    elif analyzer_type == 'rest':
        result = analyze_spring_rest(directory)
    elif analyzer_type == 'all':
        result = analyze_all_spring(directory)
    else:
        print(f"Error: Unknown analyzer type: {analyzer_type}")
        sys.exit(1)

    # Exit with error code if critical issues found
    critical = [i for i in result.issues if i.severity == Severity.CRITICAL]
    if critical:
        print(f"\n❌ Analysis failed: {len(critical)} CRITICAL issues must be fixed")
        sys.exit(1)
    else:
        print("\n✅ Analysis passed: No critical issues found")
        sys.exit(0)


if __name__ == '__main__':
    main()
