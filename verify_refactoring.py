#!/usr/bin/env python3
"""
Verification script for CodePulse 2.0 refactoring.

This script verifies that all new components are properly structured
and working correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        # Core
        from core import Issue, Pattern, AnalysisResult, Severity, Category, BaseAnalyzer
        print("  ✓ Core models imported successfully")

        # Java analyzers
        from analyzers.java import JVMAnalyzer, Java17Analyzer, Java21Analyzer
        print("  ✓ Java analyzers imported successfully")

        # JavaScript analyzers
        from analyzers.javascript import NodeJSAnalyzer, NextJSAnalyzer
        print("  ✓ JavaScript analyzers imported successfully")

        # Reporters
        from reporters import ConsoleReporter, JSONReporter, HTMLReporter
        print("  ✓ Reporters imported successfully")

        return True

    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_models():
    """Test model creation and functionality."""
    print("\nTesting models...")

    try:
        from core import Issue, Pattern, AnalysisResult, Severity, Category

        # Test Severity enum
        assert Severity.CRITICAL.emoji == "🔴"
        print("  ✓ Severity enum works")

        # Test Category enum
        assert str(Category.PERFORMANCE) == "Performance"
        print("  ✓ Category enum works")

        # Test Issue creation
        issue = Issue(
            category=Category.PERFORMANCE,
            severity=Severity.HIGH,
            file_path="test.java",
            line_number=42,
            code_snippet="test code",
            description="Test issue",
            potential_impact="High impact"
        )
        assert issue.severity == Severity.HIGH
        assert issue.category == Category.PERFORMANCE
        print("  ✓ Issue creation works")

        # Test Pattern creation
        pattern = Pattern(
            name="test",
            regex=r"test",
            category=Category.SECURITY,
            severity=Severity.CRITICAL,
            description="Test",
            impact="Test impact"
        )
        assert pattern.enabled is True
        print("  ✓ Pattern creation works")

        # Test AnalysisResult
        result = AnalysisResult()
        result.add_issue(issue)
        assert len(result.issues) == 1
        assert result.has_critical_issues() is False
        print("  ✓ AnalysisResult works")

        return True

    except Exception as e:
        print(f"  ✗ Model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analyzers():
    """Test analyzer initialization."""
    print("\nTesting analyzers...")

    try:
        from analyzers.java import JVMAnalyzer, Java17Analyzer, Java21Analyzer
        from analyzers.javascript import NodeJSAnalyzer, NextJSAnalyzer

        # Test JVM Analyzer
        jvm = JVMAnalyzer()
        assert jvm.name == "JVM Performance Analyzer"
        assert len(jvm.get_file_extensions()) > 0
        patterns = jvm._init_patterns()
        assert 'string_concat_loop' in patterns
        print("  ✓ JVM Analyzer works")

        # Test Java 17 Analyzer
        j17 = Java17Analyzer()
        assert j17.name == "Java 17 LTS Modernization Analyzer"
        patterns = j17._init_patterns()
        assert 'multiline_string_concat' in patterns
        print("  ✓ Java 17 Analyzer works")

        # Test Java 21 Analyzer
        j21 = Java21Analyzer()
        assert j21.name == "Java 21 Modernization Analyzer"
        patterns = j21._init_patterns()
        assert 'platform_thread_pool' in patterns
        print("  ✓ Java 21 Analyzer works")

        # Test Node.js Analyzer
        nodejs = NodeJSAnalyzer()
        assert nodejs.name == "Node.js Anti-Pattern Analyzer"
        patterns = nodejs._init_patterns()
        assert 'sync_file_operations' in patterns
        print("  ✓ Node.js Analyzer works")

        # Test Next.js Analyzer
        nextjs = NextJSAnalyzer()
        assert nextjs.name == "Next.js Optimization Analyzer"
        patterns = nextjs._init_patterns()
        assert 'use_client_unnecessary' in patterns
        print("  ✓ Next.js Analyzer works")

        return True

    except Exception as e:
        print(f"  ✗ Analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reporters():
    """Test reporter functionality."""
    print("\nTesting reporters...")

    try:
        from reporters import ConsoleReporter, JSONReporter, HTMLReporter
        from core import AnalysisResult, Issue, Category, Severity

        # Create test result
        result = AnalysisResult()
        result.files_analyzed = 10
        result.total_lines = 1000

        issue = Issue(
            category=Category.PERFORMANCE,
            severity=Severity.CRITICAL,
            file_path="test.java",
            line_number=42,
            code_snippet="code",
            description="Test issue",
            potential_impact="High"
        )
        result.add_issue(issue)

        # Test Console Reporter
        console = ConsoleReporter(use_colors=False)
        assert console is not None
        print("  ✓ Console Reporter initialized")

        # Test JSON Reporter
        json_reporter = JSONReporter()
        json_str = json_reporter.report(result)
        assert "Test issue" in json_str
        print("  ✓ JSON Reporter works")

        # Test HTML Reporter
        html_reporter = HTMLReporter()
        assert html_reporter is not None
        print("  ✓ HTML Reporter initialized")

        return True

    except Exception as e:
        print(f"  ✗ Reporter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli():
    """Test CLI module."""
    print("\nTesting CLI...")

    try:
        from cli import CodePulseCLI

        cli = CodePulseCLI()
        assert cli is not None
        assert 'jvm' in cli.ANALYZERS
        assert 'java21' in cli.ANALYZERS
        assert 'nodejs' in cli.ANALYZERS
        assert 'nextjs' in cli.ANALYZERS
        print("  ✓ CLI initialized with all analyzers")

        return True

    except Exception as e:
        print(f"  ✗ CLI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_structure():
    """Verify directory structure."""
    print("\nVerifying directory structure...")

    base = Path(__file__).parent
    required_paths = [
        "src/core/__init__.py",
        "src/core/models.py",
        "src/core/base_analyzer.py",
        "src/analyzers/java/__init__.py",
        "src/analyzers/java/jvm_analyzer.py",
        "src/analyzers/java/java17_analyzer.py",
        "src/analyzers/java/java21_analyzer.py",
        "src/analyzers/javascript/__init__.py",
        "src/analyzers/javascript/nodejs_analyzer.py",
        "src/analyzers/javascript/nextjs_analyzer.py",
        "src/reporters/__init__.py",
        "src/reporters/console_reporter.py",
        "src/reporters/json_reporter.py",
        "src/reporters/html_reporter.py",
        "src/cli.py",
        "tests/unit/test_models.py",
        "tests/unit/test_analyzers.py",
        "examples/quick_start.py",
        "docs/API.md",
        "docs/MARKETING.md",
        "setup.py",
        "requirements.txt",
        "README.new.md",
        "REFACTORING_SUMMARY.md",
    ]

    all_exist = True
    for path_str in required_paths:
        path = base / path_str
        if path.exists():
            print(f"  ✓ {path_str}")
        else:
            print(f"  ✗ Missing: {path_str}")
            all_exist = False

    return all_exist


def main():
    """Run all verification tests."""
    print("=" * 80)
    print("CodePulse 2.0 Refactoring Verification")
    print("=" * 80)

    results = []

    results.append(("Structure", verify_structure()))
    results.append(("Imports", test_imports()))
    results.append(("Models", test_models()))
    results.append(("Analyzers", test_analyzers()))
    results.append(("Reporters", test_reporters()))
    results.append(("CLI", test_cli()))

    print("\n" + "=" * 80)
    print("Verification Summary")
    print("=" * 80)

    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\n🎉 All verifications passed! Refactoring successful!")
        print("\nNext steps:")
        print("  1. Run tests: pytest tests/")
        print("  2. Try examples: python examples/quick_start.py")
        print("  3. Test CLI: python -m src.cli analyze --help")
        return 0
    else:
        print("\n⚠️  Some verifications failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
