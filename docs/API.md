# CodePulse API Documentation

## Overview

CodePulse provides both a CLI interface and a Python API for code analysis. This document covers the programmatic API.

## Installation

```bash
pip install codepulse
```

## Quick Start

```python
from pathlib import Path
from codepulse.analyzers.java import JVMAnalyzer
from codepulse.reporters import ConsoleReporter

# Create analyzer
analyzer = JVMAnalyzer()

# Analyze directory
result = analyzer.analyze_directory(Path("./my-project"))

# Display results
reporter = ConsoleReporter()
reporter.report(result)
```

## Core Components

### Models

#### Severity

Enum representing issue severity levels.

```python
from codepulse.core import Severity

Severity.CRITICAL  # 🔴 Most severe issues
Severity.HIGH      # 🟠 Significant problems
Severity.MEDIUM    # 🟡 Moderate issues
Severity.LOW       # 🟢 Minor improvements
Severity.INFO      # ℹ️ Informational
```

#### Category

Enum for issue categorization.

```python
from codepulse.core import Category

Category.PERFORMANCE      # Performance issues
Category.MEMORY          # Memory leaks and optimization
Category.SECURITY        # Security vulnerabilities
Category.DATABASE        # Database access patterns
Category.CONCURRENCY     # Threading and concurrency
Category.CODE_SMELL      # Code quality issues
Category.BEST_PRACTICE   # Best practice violations
Category.MODERNIZATION   # Upgrade opportunities
Category.BUNDLE_SIZE     # Bundle size optimization
Category.EVENT_LOOP      # Event loop blocking (Node.js)
```

#### Issue

Represents a single code quality issue.

```python
from codepulse.core import Issue, Category, Severity

issue = Issue(
    category=Category.PERFORMANCE,
    severity=Severity.HIGH,
    file_path="src/main/java/App.java",
    line_number=42,
    code_snippet="for(int i=0; i<n; i++) { str += 'x'; }",
    description="String concatenation in loop",
    potential_impact="Reduces allocations from ~50MB to ~200KB per 10K iterations",
    solution="Use StringBuilder outside the loop"
)

# Access properties
print(issue.severity_emoji)  # 🟠
print(issue.to_dict())      # Convert to dictionary
```

#### Pattern

Defines a detection pattern for code analysis.

```python
from codepulse.core import Pattern, Category, Severity

pattern = Pattern(
    name="my_custom_pattern",
    regex=r"System\.out\.print",
    category=Category.BEST_PRACTICE,
    severity=Severity.MEDIUM,
    description="Using System.out instead of logger",
    impact="Poor logging practices",
    solution="Use slf4j or Log4j2",
    enabled=True,
    metadata={"docs_url": "https://..."}
)
```

#### AnalysisResult

Container for analysis results.

```python
from codepulse.core import AnalysisResult, Severity, Category

result = AnalysisResult()

# Add issues
result.add_issue(issue)

# Query results
critical = result.get_issues_by_severity(Severity.CRITICAL)
perf_issues = result.get_issues_by_category(Category.PERFORMANCE)
has_critical = result.has_critical_issues()

# Statistics
print(f"Files analyzed: {result.files_analyzed}")
print(f"Total lines: {result.total_lines}")
print(f"Total issues: {len(result.issues)}")
print(f"Stats: {result.stats}")

# Export
data = result.to_dict()
```

### Base Analyzer

Abstract base class for all analyzers.

```python
from codepulse.core import BaseAnalyzer, Pattern
from typing import Dict, Set

class MyAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__(name="My Custom Analyzer")

    def get_file_extensions(self) -> Set[str]:
        return {'.py', '.pyw'}

    def _init_patterns(self) -> Dict[str, Pattern]:
        return {
            'pattern1': Pattern(...),
            'pattern2': Pattern(...),
        }

# Use custom analyzer
analyzer = MyAnalyzer()
result = analyzer.analyze_directory(Path("./project"))
```

#### Methods

- `analyze_directory(directory: Path) -> AnalysisResult`: Analyze all files in directory
- `add_pattern(pattern: Pattern)`: Add new detection pattern
- `remove_pattern(pattern_name: str)`: Remove pattern
- `disable_pattern(pattern_name: str)`: Disable pattern without removing
- `enable_pattern(pattern_name: str)`: Re-enable disabled pattern
- `get_summary() -> Dict`: Get summary statistics

## Analyzers

### Java Analyzers

#### JVMAnalyzer

Detects JVM performance anti-patterns.

```python
from codepulse.analyzers.java import JVMAnalyzer

analyzer = JVMAnalyzer()
result = analyzer.analyze_directory(Path("./java-project"))

# Detects:
# - String concatenation in loops
# - Autoboxing in collections
# - Pattern compilation in loops
# - Nested loops O(N²)
# - N+1 query problems
# - Static collections without limits
# - Thread.sleep in loops
# - Exception flow control
# - Large synchronized blocks
# - Date/Calendar in loops
```

**File extensions**: `.java`, `.kt`, `.scala`

#### Java17Analyzer

Java 17 LTS modernization opportunities.

```python
from codepulse.analyzers.java import Java17Analyzer

analyzer = Java17Analyzer()
result = analyzer.analyze_directory(Path("./java-project"))

# Detects opportunities for:
# - Text blocks (multi-line strings)
# - Sealed classes
# - Pattern matching for instanceof
# - Enhanced random number generators
# - Stream.toList()
# - Switch expressions
# - Records
```

**File extensions**: `.java`

#### Java21Analyzer

Java 21 feature adoption suggestions.

```python
from codepulse.analyzers.java import Java21Analyzer

analyzer = Java21Analyzer()
result = analyzer.analyze_directory(Path("./java-project"))

# Detects opportunities for:
# - Virtual Threads
# - Pattern matching for switch
# - Records
# - Sequenced Collections
# - Scoped Values
# - String Templates (Preview)
# - Structured Concurrency (Preview)
# - Unnamed variables
```

**File extensions**: `.java`

### JavaScript/TypeScript Analyzers

#### NodeJSAnalyzer

Node.js anti-patterns and best practices.

```python
from codepulse.analyzers.javascript import NodeJSAnalyzer

analyzer = NodeJSAnalyzer()
result = analyzer.analyze_directory(Path("./nodejs-app"))

# Detects:
# - Event loop blocking (sync operations)
# - Memory leaks (listeners, intervals, globals)
# - Unhandled promises
# - Callback hell
# - Stream misuse
# - N+1 database queries
# - Missing connection pools
# - Security issues (eval, SQL injection)
# - Regex compilation in loops
# - CPU-intensive operations in main thread
```

**File extensions**: `.js`, `.ts`, `.mjs`, `.cjs`

#### NextJSAnalyzer

Next.js optimization opportunities.

```python
from codepulse.analyzers.javascript import NextJSAnalyzer

analyzer = NextJSAnalyzer()
result = analyzer.analyze_directory(Path("./nextjs-app"))

# Detects:
# - Unnecessary 'use client' directives
# - Client-side data fetching
# - Missing Image optimization
# - Font optimization issues
# - Data fetching anti-patterns
# - Missing metadata
# - Internal navigation with <a>
# - Bundle size issues
# - API route security
# - Configuration problems
```

**File extensions**: `.js`, `.jsx`, `.ts`, `.tsx`

## Reporters

### ConsoleReporter

Outputs results to terminal with colors.

```python
from codepulse.reporters import ConsoleReporter

reporter = ConsoleReporter(
    use_colors=True,    # Enable ANSI colors
    verbose=False       # Show detailed info
)

# Full report
reporter.report(result)

# Quick summary
reporter.print_quick_summary(result)
```

### JSONReporter

Exports results as JSON.

```python
from codepulse.reporters import JSONReporter
from pathlib import Path

reporter = JSONReporter(pretty=True)

# To file
reporter.report(result, Path("./report.json"))

# To console
reporter.print_to_console(result)

# Get JSON string
json_str = reporter.report(result)
```

### HTMLReporter

Generates interactive HTML reports.

```python
from codepulse.reporters import HTMLReporter
from pathlib import Path

reporter = HTMLReporter()

# Generate report
reporter.report(result, Path("./report.html"))
```

## Advanced Usage

### Multiple Analyzers

```python
from codepulse.analyzers.java import JVMAnalyzer, Java21Analyzer
from codepulse.core import AnalysisResult

analyzers = [JVMAnalyzer(), Java21Analyzer()]
all_issues = []

for analyzer in analyzers:
    result = analyzer.analyze_directory(Path("./project"))
    all_issues.extend(result.issues)

# Create combined result
combined = AnalysisResult(issues=all_issues)
```

### Custom Filtering

```python
# Filter by severity
critical = [i for i in result.issues if i.severity == Severity.CRITICAL]

# Filter by file
app_issues = [i for i in result.issues if 'App.java' in i.file_path]

# Complex filtering
db_critical = [
    i for i in result.issues
    if i.category == Category.DATABASE
    and i.severity in [Severity.CRITICAL, Severity.HIGH]
]
```

### CI/CD Integration

```python
from codepulse.analyzers.java import JVMAnalyzer
from codepulse.reporters import JSONReporter
import sys

analyzer = JVMAnalyzer()
result = analyzer.analyze_directory(Path("."))

# Save report
JSONReporter().report(result, Path("./codepulse-report.json"))

# Fail build on critical issues
if result.has_critical_issues():
    print("❌ Critical issues found!")
    sys.exit(1)

print("✅ No critical issues")
sys.exit(0)
```

## Error Handling

```python
try:
    result = analyzer.analyze_directory(Path("./project"))
except FileNotFoundError:
    print("Directory not found")
except Exception as e:
    print(f"Analysis failed: {e}")

# Check for errors in result
if 'errors' in result.metadata:
    print(f"Errors encountered: {result.metadata['errors']}")
```

## Best Practices

1. **Use appropriate analyzers**: Choose analyzers that match your technology stack
2. **Start with critical issues**: Address CRITICAL and HIGH severity issues first
3. **Customize patterns**: Add project-specific patterns for better coverage
4. **Integrate with CI/CD**: Fail builds on critical issues
5. **Track progress**: Use JSON reports to track improvements over time
6. **Combine analyzers**: Use multiple analyzers for comprehensive analysis

## Examples

See the [examples/](../examples/) directory for complete working examples.
