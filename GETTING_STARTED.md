# 🚀 Getting Started with CodePulse 2.0

## Quick Installation & Usage

### 1. Set Up Python Environment

```bash
# Navigate to project directory
cd /home/jwcastillo/Develop/2025/CodePulse

# Set Python path (required for development mode)
export PYTHONPATH=/home/jwcastillo/Develop/2025/CodePulse/src

# Or add to your .bashrc/.zshrc for permanent setup
echo 'export PYTHONPATH=/home/jwcastillo/Develop/2025/CodePulse/src' >> ~/.bashrc
```

### 2. Verify Installation

```bash
# Test imports
python3 -c "
from core import Issue, Severity, Category
from analyzers.java import JVMAnalyzer
from analyzers.javascript import NodeJSAnalyzer
from reporters import ConsoleReporter
print('✅ CodePulse 2.0 is ready!')
"
```

Expected output:
```
✅ CodePulse 2.0 is ready!
```

### 3. Run Your First Analysis

#### Analyze Java Code

```bash
python3 << 'EOF'
from pathlib import Path
from analyzers.java import JVMAnalyzer
from reporters import ConsoleReporter

# Create analyzer
analyzer = JVMAnalyzer()

# Analyze your Java project
result = analyzer.analyze_directory(Path("./examples/java"))

# Show results
reporter = ConsoleReporter()
reporter.print_quick_summary(result)
EOF
```

#### Analyze Node.js Code

```bash
python3 << 'EOF'
from pathlib import Path
from analyzers.javascript import NodeJSAnalyzer
from reporters import ConsoleReporter

analyzer = NodeJSAnalyzer()
result = analyzer.analyze_directory(Path("./examples/nodejs"))

ConsoleReporter().print_quick_summary(result)
EOF
```

#### Analyze Next.js Code

```bash
python3 << 'EOF'
from pathlib import Path
from analyzers.javascript import NextJSAnalyzer
from reporters import JSONReporter

analyzer = NextJSAnalyzer()
result = analyzer.analyze_directory(Path("./examples/next.js"))

# Export to JSON
JSONReporter().report(result, Path("./nextjs-report.json"))
print("✅ Report saved to nextjs-report.json")
EOF
```

### 4. Run Examples

```bash
# Run the comprehensive quick start guide
python3 examples/quick_start.py
```

This will demonstrate:
- Java performance analysis
- Java 21 modernization
- Node.js anti-pattern detection
- Next.js optimization
- Multiple analyzers
- Custom patterns
- Result filtering

### 5. Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_models.py -v
```

## Common Usage Patterns

### Pattern 1: Quick Analysis with Console Output

```python
from pathlib import Path
from analyzers.java import JVMAnalyzer
from reporters import ConsoleReporter

analyzer = JVMAnalyzer()
result = analyzer.analyze_directory(Path("./your-project"))

reporter = ConsoleReporter(use_colors=True, verbose=True)
reporter.report(result)
```

### Pattern 2: Generate JSON Report for CI/CD

```python
from pathlib import Path
from analyzers.java import Java21Analyzer
from reporters import JSONReporter
import sys

analyzer = Java21Analyzer()
result = analyzer.analyze_directory(Path("./src"))

# Save report
JSONReporter().report(result, Path("./codepulse-report.json"))

# Fail if critical issues found
if result.has_critical_issues():
    print("❌ Critical issues found!")
    sys.exit(1)

print("✅ No critical issues")
```

### Pattern 3: Generate HTML Report

```python
from pathlib import Path
from analyzers.javascript import NextJSAnalyzer
from reporters import HTMLReporter

analyzer = NextJSAnalyzer()
result = analyzer.analyze_directory(Path("./app"))

# Generate interactive HTML report
HTMLReporter().report(result, Path("./reports/nextjs-analysis.html"))
print("Report: ./reports/nextjs-analysis.html")
```

### Pattern 4: Multiple Analyzers

```python
from pathlib import Path
from analyzers.java import JVMAnalyzer, Java21Analyzer
from reporters import ConsoleReporter
from core import AnalysisResult

# Run multiple analyzers
analyzers = [JVMAnalyzer(), Java21Analyzer()]
all_issues = []

for analyzer in analyzers:
    result = analyzer.analyze_directory(Path("./src"))
    all_issues.extend(result.issues)

# Combine results
combined = AnalysisResult(issues=all_issues)
ConsoleReporter().report(combined)
```

### Pattern 5: Custom Filtering

```python
from pathlib import Path
from analyzers.java import JVMAnalyzer
from core import Severity, Category

analyzer = JVMAnalyzer()
result = analyzer.analyze_directory(Path("./src"))

# Get only critical issues
critical = result.get_issues_by_severity(Severity.CRITICAL)
print(f"Critical issues: {len(critical)}")

# Get performance issues
perf = result.get_issues_by_category(Category.PERFORMANCE)
print(f"Performance issues: {len(perf)}")

# Custom filtering
db_critical = [
    issue for issue in result.issues
    if issue.category == Category.DATABASE
    and issue.severity == Severity.CRITICAL
]
print(f"Critical DB issues: {len(db_critical)}")
```

### Pattern 6: Add Custom Pattern

```python
from analyzers.java import JVMAnalyzer
from core import Pattern, Category, Severity

analyzer = JVMAnalyzer()

# Add your custom pattern
custom_pattern = Pattern(
    name="system_out_usage",
    regex=r'System\.(out|err)\.print',
    category=Category.BEST_PRACTICE,
    severity=Severity.MEDIUM,
    description="Using System.out/err instead of logger",
    impact="Poor logging practices",
    solution="Use slf4j or Log4j2"
)

analyzer.add_pattern(custom_pattern)

# Now analyze
result = analyzer.analyze_directory(Path("./src"))
```

## Project Structure Reference

```
CodePulse/
├── src/                        # Source code
│   ├── core/                   # Core models and base classes
│   ├── analyzers/              # Language-specific analyzers
│   │   ├── java/              # Java analyzers
│   │   └── javascript/        # JS/TS analyzers
│   ├── reporters/             # Output formatters
│   └── cli.py                 # CLI interface
│
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
│
├── examples/                   # Example code
│   ├── quick_start.py         # Comprehensive examples
│   ├── java/                  # Java examples
│   ├── nodejs/                # Node.js examples
│   └── next.js/               # Next.js examples
│
├── docs/                       # Documentation
│   ├── API.md                 # API reference
│   └── MARKETING.md           # Marketing content
│
├── old_code/                   # Archived old implementation
│
└── setup.py                    # Package configuration
```

## Available Analyzers

### Java Analyzers

1. **JVMAnalyzer** - Performance anti-patterns
   - String concatenation in loops
   - N+1 query problems
   - Nested loops O(N²)
   - Pattern compilation in loops
   - Autoboxing issues

2. **Java17Analyzer** - Java 17 LTS features
   - Text blocks
   - Pattern matching
   - Sealed classes
   - Records

3. **Java21Analyzer** - Java 21 modernization
   - Virtual Threads
   - Pattern matching for switch
   - Sequenced Collections
   - String Templates (Preview)

### JavaScript/TypeScript Analyzers

4. **NodeJSAnalyzer** - Node.js anti-patterns
   - Event loop blocking
   - Memory leaks
   - Unhandled promises
   - Database N+1 queries
   - Security issues

5. **NextJSAnalyzer** - Next.js optimizations
   - Image optimization
   - Server vs Client Components
   - Font optimization
   - Data fetching patterns
   - Bundle size issues

## Output Formats

### Console (Terminal)
- Colored, formatted output
- Issue severity badges
- Code snippets with line numbers
- Summary statistics

### JSON
- Machine-readable format
- Perfect for CI/CD pipelines
- Includes metadata and statistics
- Easy to parse and filter

### HTML
- Interactive web report
- Visual charts and statistics
- Filterable issue list
- Code highlighting

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/code-quality.yml
name: Code Quality Analysis

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Run CodePulse Analysis
        run: |
          export PYTHONPATH=$GITHUB_WORKSPACE/src
          python3 << 'EOF'
          from pathlib import Path
          from analyzers.java import JVMAnalyzer
          from reporters import JSONReporter
          import sys

          analyzer = JVMAnalyzer()
          result = analyzer.analyze_directory(Path("./src"))

          # Save report
          JSONReporter().report(result, Path("./codepulse-report.json"))

          # Fail on critical issues
          if result.has_critical_issues():
              print("❌ Critical issues found!")
              sys.exit(1)

          print("✅ Code quality check passed")
          EOF

      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: codepulse-report
          path: codepulse-report.json
```

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'core'`

**Solution**: Set PYTHONPATH
```bash
export PYTHONPATH=/home/jwcastillo/Develop/2025/CodePulse/src
```

### No Issues Found

**Problem**: Analyzer reports 0 issues but you expect some

**Solution**: Check file extensions
```python
# View supported extensions
from analyzers.java import JVMAnalyzer
analyzer = JVMAnalyzer()
print(analyzer.get_file_extensions())  # {'.java', '.kt', '.scala'}
```

### Pattern Not Matching

**Problem**: Custom pattern doesn't find expected issues

**Solution**: Test your regex
```python
import re
pattern = r'System\.out\.print'
test_code = "System.out.println('test');"
match = re.search(pattern, test_code)
print(f"Match: {match}")  # Should show match object
```

## Next Steps

1. ✅ Read the [API Documentation](docs/API.md)
2. ✅ Explore [Examples](examples/quick_start.py)
3. ✅ Run tests: `pytest tests/`
4. ✅ Analyze your own projects
5. ✅ Create custom analyzers for your needs

## Support

- 📧 Issues: Create an issue in the repository
- 📖 Documentation: See `docs/` folder
- 💡 Examples: See `examples/` folder

---

**🎉 You're ready to use CodePulse 2.0!**

*Happy analyzing! 🔍*
