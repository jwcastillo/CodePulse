#!/usr/bin/env python3
"""
Example: JVM Performance Deep Analysis

Este ejemplo demuestra cómo analizar aplicaciones Java/JVM para problemas
profundos de rendimiento:
- String performance (concatenación, formateo)
- Collection performance (ArrayList, HashMap, Vector)
- Autoboxing overhead
- Pattern compilation
- I/O buffering
- Memory leaks
- Reflection overhead
- Logging performance
"""

from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.java.jvm_performance_analyzer import JVMPerformanceAnalyzer
from reporters import ConsoleReporter, HTMLReporter, JSONReporter
from core.models import Severity, Category


def analyze_string_performance(directory: Path):
    """Analizar problemas de rendimiento relacionados con Strings."""
    print("\n" + "="*80)
    print("  String Performance Analysis")
    print("="*80 + "\n")

    analyzer = JVMPerformanceAnalyzer()
    result = analyzer.analyze_directory(directory)

    # Filtrar solo issues de strings
    string_issues = [
        issue for issue in result.issues
        if 'string' in issue.description.lower()
    ]

    print(f"Found {len(string_issues)} string performance issues:\n")

    for issue in string_issues:
        print(f"{issue.severity.emoji} {issue.description}")
        print(f"   Location: {issue.file_path}:{issue.line_number}")
        print(f"   Impact: {issue.potential_impact}")
        print(f"   Solution: {issue.solution}\n")

    return string_issues


def analyze_collection_performance(directory: Path):
    """Analizar problemas de rendimiento en colecciones."""
    print("\n" + "="*80)
    print("  Collection Performance Analysis")
    print("="*80 + "\n")

    analyzer = JVMPerformanceAnalyzer()
    result = analyzer.analyze_directory(directory)

    # Filtrar issues de colecciones
    collection_issues = [
        issue for issue in result.issues
        if any(word in issue.description.lower()
               for word in ['arraylist', 'hashmap', 'vector', 'hashtable', 'linkedlist'])
    ]

    print(f"Found {len(collection_issues)} collection performance issues:\n")

    critical = [i for i in collection_issues if i.severity == Severity.CRITICAL]
    high = [i for i in collection_issues if i.severity == Severity.HIGH]

    if critical:
        print(f"🔴 CRITICAL ({len(critical)}):")
        for issue in critical:
            print(f"   - {issue.description} at {issue.file_path}:{issue.line_number}")

    if high:
        print(f"\n🟠 HIGH ({len(high)}):")
        for issue in high:
            print(f"   - {issue.description} at {issue.file_path}:{issue.line_number}")

    return collection_issues


def analyze_memory_leaks(directory: Path):
    """Analizar posibles memory leaks."""
    print("\n" + "="*80)
    print("  Memory Leak Detection")
    print("="*80 + "\n")

    analyzer = JVMPerformanceAnalyzer()
    result = analyzer.analyze_directory(directory)

    # Filtrar memory leaks
    memory_leaks = [
        issue for issue in result.issues
        if 'leak' in issue.description.lower() or
           'threadlocal' in issue.description.lower() or
           'static collection' in issue.description.lower()
    ]

    if memory_leaks:
        print(f"⚠️  Found {len(memory_leaks)} potential memory leaks:\n")
        for issue in memory_leaks:
            print(f"{issue.severity.emoji} {issue.description}")
            print(f"   Location: {issue.file_path}:{issue.line_number}")
            print(f"   Impact: {issue.potential_impact}")
            print(f"   Solution: {issue.solution}\n")
    else:
        print("✅ No memory leaks detected")

    return memory_leaks


def full_performance_analysis(directory: Path):
    """Análisis completo de rendimiento JVM."""
    print("\n" + "="*80)
    print("  Complete JVM Performance Analysis")
    print("="*80 + "\n")

    analyzer = JVMPerformanceAnalyzer()
    result = analyzer.analyze_directory(directory)

    # Estadísticas generales
    print("📊 Performance Issues Summary:")
    print(f"   Total Files Analyzed: {result.files_analyzed}")
    print(f"   Total Lines: {result.total_lines:,}")
    print(f"   Total Issues: {len(result.issues)}\n")

    # Por severidad
    critical = result.get_issues_by_severity(Severity.CRITICAL)
    high = result.get_issues_by_severity(Severity.HIGH)
    medium = result.get_issues_by_severity(Severity.MEDIUM)
    low = result.get_issues_by_severity(Severity.LOW)

    print("Severity Breakdown:")
    print(f"   🔴 CRITICAL: {len(critical)}")
    print(f"   🟠 HIGH:     {len(high)}")
    print(f"   🟡 MEDIUM:   {len(medium)}")
    print(f"   🟢 LOW:      {len(low)}\n")

    # Por categoría
    performance = result.get_issues_by_category(Category.PERFORMANCE)
    memory = result.get_issues_by_category(Category.MEMORY)
    concurrency = result.get_issues_by_category(Category.CONCURRENCY)

    print("Category Breakdown:")
    print(f"   ⚡ Performance: {len(performance)}")
    print(f"   💾 Memory:      {len(memory)}")
    print(f"   🔄 Concurrency: {len(concurrency)}\n")

    # Top 5 critical issues
    if critical:
        print("🔴 Top 5 CRITICAL Issues:")
        for i, issue in enumerate(critical[:5], 1):
            print(f"\n   {i}. {issue.description}")
            print(f"      Location: {issue.file_path}:{issue.line_number}")
            print(f"      Impact: {issue.potential_impact}")
            print(f"      Solution: {issue.solution}")

    # Generar reportes
    print("\n" + "="*80)
    print("  Generating Reports...")
    print("="*80 + "\n")

    # Console report
    ConsoleReporter(use_colors=True, verbose=False).report(result)

    # HTML report
    html_path = Path("./jvm-performance-report.html")
    HTMLReporter().report(result, html_path)
    print(f"✅ HTML report saved to: {html_path}")

    # JSON report
    json_path = Path("./jvm-performance.json")
    JSONReporter().report(result, json_path)
    print(f"✅ JSON report saved to: {json_path}")

    return result


def performance_hotspots(directory: Path):
    """Identificar los hotspots de rendimiento más críticos."""
    print("\n" + "="*80)
    print("  Performance Hotspots Detection")
    print("="*80 + "\n")

    analyzer = JVMPerformanceAnalyzer()
    result = analyzer.analyze_directory(directory)

    # Agrupar por archivo
    files_with_issues = {}
    for issue in result.issues:
        if issue.file_path not in files_with_issues:
            files_with_issues[issue.file_path] = []
        files_with_issues[issue.file_path].append(issue)

    # Ordenar por número de issues
    hotspots = sorted(
        files_with_issues.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    print("📍 Top 10 Performance Hotspots:\n")
    for i, (file_path, issues) in enumerate(hotspots[:10], 1):
        critical_count = len([i for i in issues if i.severity == Severity.CRITICAL])
        high_count = len([i for i in issues if i.severity == Severity.HIGH])

        print(f"{i:2}. {file_path}")
        print(f"    Total issues: {len(issues)} "
              f"(🔴 {critical_count} CRITICAL, 🟠 {high_count} HIGH)")

        # Mostrar el issue más crítico del archivo
        critical_issues = [i for i in issues if i.severity == Severity.CRITICAL]
        if critical_issues:
            top_issue = critical_issues[0]
            print(f"    Top issue: {top_issue.description}")
            print(f"    Impact: {top_issue.potential_impact}\n")

    return hotspots


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python jvm_performance_analysis.py <directory> [mode]")
        print("\nModes:")
        print("  strings    - Analyze string performance only")
        print("  collections - Analyze collection performance only")
        print("  memory     - Detect memory leaks only")
        print("  hotspots   - Identify performance hotspots")
        print("  full       - Complete analysis (default)")
        print("\nExample:")
        print("  python jvm_performance_analysis.py ./src full")
        sys.exit(1)

    directory = Path(sys.argv[1])
    mode = sys.argv[2] if len(sys.argv) > 2 else 'full'

    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    print(f"\n🔍 Analyzing: {directory}")
    print(f"📋 Mode: {mode}\n")

    if mode == 'strings':
        issues = analyze_string_performance(directory)
    elif mode == 'collections':
        issues = analyze_collection_performance(directory)
    elif mode == 'memory':
        issues = analyze_memory_leaks(directory)
    elif mode == 'hotspots':
        hotspots = performance_hotspots(directory)
        # Flatten issues from hotspots
        issues = [issue for _, file_issues in hotspots for issue in file_issues]
    elif mode == 'full':
        result = full_performance_analysis(directory)
        issues = result.issues
    else:
        print(f"Error: Unknown mode: {mode}")
        sys.exit(1)

    # Exit with error code if critical issues found
    critical = [i for i in issues if i.severity == Severity.CRITICAL]
    if critical:
        print(f"\n❌ Analysis failed: {len(critical)} CRITICAL performance issues found")
        print("   These issues can make your application 100-1000x slower!")
        sys.exit(1)
    else:
        print("\n✅ Analysis passed: No critical performance issues found")
        sys.exit(0)


if __name__ == '__main__':
    main()
