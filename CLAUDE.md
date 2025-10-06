# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CodePulse 2.0** is a professional static analysis toolkit that detects performance anti-patterns, security vulnerabilities, and modernization opportunities in Java, JavaScript, and TypeScript codebases.

**Current Version:** 2.0.0 (Complete Refactoring - October 2025)

## Core Architecture

The project follows a modular, professional Python package structure:

### Source Code (`/src/`)

```
src/
├── core/                    # Shared foundation
│   ├── models.py           # Issue, Pattern, AnalysisResult, Severity, Category
│   ├── base_analyzer.py    # Abstract base class for all analyzers
│   └── __init__.py
├── analyzers/              # Language-specific analyzers
│   ├── java/
│   │   ├── jvm_analyzer.py         # JVM performance anti-patterns
│   │   ├── java17_analyzer.py      # Java 17 LTS features
│   │   └── java21_analyzer.py      # Java 21 modernization
│   └── javascript/
│       ├── nodejs_analyzer.py      # Node.js anti-patterns
│       └── nextjs_analyzer.py      # Next.js optimizations
├── reporters/              # Output formatters
│   ├── console_reporter.py # Colored terminal output
│   ├── json_reporter.py    # JSON for CI/CD
│   └── html_reporter.py    # Interactive HTML reports
└── cli.py                  # Command-line interface
```

### Testing (`/tests/`)
- **Unit tests**: `tests/unit/test_models.py`, `tests/unit/test_analyzers.py`
- **Integration tests**: `tests/integration/` (ready for expansion)
- **Coverage**: 85%+ across all modules

### Documentation (`/docs/`)
- **API Reference**: `docs/API.md` - Complete API documentation
- **Guides**: `docs/guides/` - Framework-specific guides
- **Marketing**: `docs/MARKETING.md` - Use cases and storytelling
- **Articles**: `docs/articles/` - Blog posts and social media content

### Examples (`/examples/`)
- **Quick Start**: `examples/quick_start.py` - 7 working examples
- **Sample Code**: `examples/java/`, `examples/nodejs/`, `examples/next.js/`

## Common Development Commands

### Installation

```bash
# Install in development mode
pip install -e .

# Or use PYTHONPATH for development
export PYTHONPATH=/path/to/CodePulse/src
```

### Running Analyzers (Python API)

```python
# Java Analysis
from pathlib import Path
from analyzers.java import JVMAnalyzer, Java21Analyzer
from reporters import ConsoleReporter

analyzer = JVMAnalyzer()
result = analyzer.analyze_directory(Path("./your-project"))
ConsoleReporter().report(result)

# Node.js Analysis
from analyzers.javascript import NodeJSAnalyzer

analyzer = NodeJSAnalyzer()
result = analyzer.analyze_directory(Path("./your-nodejs-app"))
ConsoleReporter().report(result)

# Next.js Analysis with HTML report
from analyzers.javascript import NextJSAnalyzer
from reporters import HTMLReporter

analyzer = NextJSAnalyzer()
result = analyzer.analyze_directory(Path("./your-nextjs-app"))
HTMLReporter().report(result, Path("./report.html"))
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_models.py -v

# Run specific test
pytest tests/unit/test_models.py::TestIssue::test_issue_creation -v
```

### Running Examples

```bash
# Run comprehensive examples
python3 examples/quick_start.py

# Or individual examples
python3 -c "
from pathlib import Path
from analyzers.java import JVMAnalyzer
from reporters import ConsoleReporter

analyzer = JVMAnalyzer()
result = analyzer.analyze_directory(Path('./examples/java'))
ConsoleReporter().print_quick_summary(result)
"
```

## Analysis Severity Levels

Issues are categorized into severity levels with clear visual indicators:

- **🔴 CRITICAL**: Severe performance/security issues (e.g., N+1 queries, SQL injection, event loop blocking)
- **🟠 HIGH**: Significant problems (e.g., memory leaks, unnecessary client components, autoboxing)
- **🟡 MEDIUM**: Moderate issues (e.g., missing optimizations, pattern compilation in loops)
- **🟢 LOW**: Minor improvements (e.g., code style, records opportunities)

## Available Analyzers

### Java Analyzers

1. **JVMAnalyzer** - Performance anti-patterns
   - String concatenation in loops
   - N+1 query problems
   - Nested loops O(N²)
   - Memory leaks in static collections
   - File extensions: `.java`, `.kt`, `.scala`

2. **Java17Analyzer** - Java 17 LTS modernization
   - Text blocks opportunities
   - Pattern matching for instanceof
   - Records candidates
   - Sealed classes
   - File extensions: `.java`

3. **Java21Analyzer** - Java 21 feature adoption
   - Virtual Threads opportunities
   - Pattern matching for switch
   - Sequenced Collections
   - String Templates (Preview)
   - File extensions: `.java`

### JavaScript/TypeScript Analyzers

4. **NodeJSAnalyzer** - Node.js anti-patterns
   - Event loop blocking (sync operations)
   - Memory leaks (listeners, intervals)
   - Unhandled promises
   - N+1 database queries
   - Security issues (eval, SQL injection)
   - File extensions: `.js`, `.ts`, `.mjs`, `.cjs`

5. **NextJSAnalyzer** - Next.js optimizations
   - Image optimization (next/image)
   - Server vs Client Components
   - Font optimization (next/font)
   - Bundle size issues
   - Data fetching patterns
   - File extensions: `.js`, `.jsx`, `.ts`, `.tsx`

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Code Quality Check
on: [push, pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install CodePulse
        run: pip install -e .
      - name: Run Analysis
        run: |
          python3 << 'EOF'
          from pathlib import Path
          from analyzers.java import JVMAnalyzer
          from reporters import JSONReporter
          from core import Severity
          import sys

          analyzer = JVMAnalyzer()
          result = analyzer.analyze_directory(Path('./src'))

          # Save report
          JSONReporter().report(result, Path('./codepulse-report.json'))

          # Fail on critical issues
          critical = result.get_issues_by_severity(Severity.CRITICAL)
          if critical:
              print(f"❌ Found {len(critical)} critical issues!")
              sys.exit(1)
          print("✅ Code quality check passed")
          EOF
```

## Development Workflow

1. **Install**: `pip install -e .`
2. **Analyze**: Use Python API or run examples
3. **Fix Critical Issues**: Address 🔴 CRITICAL first
4. **Run Tests**: `pytest tests/`
5. **Commit**: Changes are ready when tests pass

## Key Files

- **README.md**: Main project documentation
- **GETTING_STARTED.md**: Quick start guide
- **docs/API.md**: Complete API reference
- **docs/guides/**: Framework-specific guides
- **examples/quick_start.py**: Working examples
- **SUCCESS.md**: Transformation summary