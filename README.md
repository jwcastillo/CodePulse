# 🔍 CodePulse

**Advanced Code Quality Analysis for Java, JavaScript, and TypeScript**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

> **Version 1.0.0** - [See Changelog](CHANGELOG.md)

CodePulse is a powerful static analysis tool that detects performance anti-patterns, security vulnerabilities, and modernization opportunities in your codebase—issues that traditional linters often miss.

## ✨ Key Features

- 🎯 **Multi-Language Support**: Java, JavaScript, TypeScript, Kotlin, Scala
- 🚀 **Performance Analysis**: N+1 queries, event loop blocking, memory leaks
- 🔧 **Modernization**: Java 21 features, React Server Components, Next.js optimizations
- 📊 **Multiple Outputs**: Console, JSON, HTML reports
- 🔌 **Zero Dependencies**: Pure Python stdlib—no external dependencies
- ⚡ **Fast**: Analyzes thousands of files in seconds
- 🛠️ **Extensible**: Add custom patterns easily

## 🚀 Quick Start

### Installation

```bash
pip install codepulse
```

### CLI Usage

```bash
# Analyze Java code for performance issues
codepulse analyze --analyzer jvm /path/to/java/project

# Analyze with Java 21 modernization suggestions
codepulse analyze --analyzer java21 /path/to/project

# Analyze Node.js code
codepulse analyze --analyzer nodejs /path/to/nodejs/app

# Analyze Next.js with HTML report
codepulse analyze --analyzer nextjs --output report.html /path/to/nextjs/app

# Security scan (secrets, injection, weak crypto, XSS sinks, TLS/JWT/CORS) + Spring Security config
codepulse analyze --analyzer security,spring-security --format json /path/to/project

# Multiple analyzers + JSON for CI/CD
codepulse analyze --analyzer jvm,java21 --format json --output results.json /path/to/project
```

### Python API

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

## 📋 What It Detects

### Java/JVM Analysis

**Performance Issues:**
- 🔴 String concatenation in loops → Use StringBuilder (50MB → 200KB)
- 🔴 N+1 query problems → Use batch queries (100x faster)
- 🔴 Nested loops O(N²) → Use HashMaps (1000x faster)
- 🟠 Pattern compilation in loops → Compile once (90% less CPU)
- 🟠 Autoboxing in collections → Use primitive collections (75% less memory)

**Java 21 Modernization:**
- Virtual Threads for I/O-bound tasks (4K → 1M+ concurrent threads)
- Pattern Matching for cleaner type checks
- Records for immutable data classes
- Sequenced Collections for better APIs
- String Templates for safer string interpolation

### Security Analysis

`--analyzer security` works on Java/Kotlin/Scala, JavaScript/TypeScript and config files (`.properties`, `.yml`, `.env`, `.json`, `.xml`). It skips `node_modules`, build output, `vendor`/`third-party` folders and minified `*.min.*` bundles. Every finding carries its CWE.

| Pattern | Severity | CWE |
|---|---|---|
| AWS access key, private key, GitHub token | 🔴 Critical | CWE-798 / CWE-321 |
| Slack token, hardcoded password/secret/API key (placeholders like `changeme` or `${VAR}` are ignored) | 🟠 High | CWE-798 |
| SQL built with `+` or a template literal | 🔴 Critical | CWE-89 |
| Shell command built from concatenated input | 🔴 Critical | CWE-78 |
| JWT accepting the `none` algorithm | 🔴 Critical | CWE-347 |
| `eval()` / `new Function()` | 🟠 High | CWE-95 |
| TLS certificate or hostname verification disabled | 🟠 High | CWE-295 |
| `dangerouslySetInnerHTML`, `innerHTML =` | 🟡 Medium | CWE-79 |
| MD5/SHA-1 (only a problem for security uses) | 🟡 Medium | CWE-328 |
| CORS `*` | 🟡 Medium | CWE-942 |
| Java `ObjectInputStream` deserialization | 🟡 Medium | CWE-502 |

`--analyzer spring-security` checks Spring Security configuration: CSRF, CORS, session management, JWT settings, password encoders, security headers.

Like the other analyzers these are regex patterns with no data-flow tracking: treat findings as leads to review, and pair CodePulse with a dedicated SAST tool for audits.

### JavaScript/TypeScript Analysis

**Node.js Anti-Patterns:**
- 🔴 Synchronous file operations → Use async (100x faster)
- 🔴 Unhandled promises → Add .catch() handlers
- 🔴 N+1 database queries → Use batch operations
- 🟠 Event listeners without cleanup → Memory leaks
- 🟠 CPU-intensive operations in main thread → Use Worker Threads

**Next.js Optimizations:**
- 🟠 Missing Image optimization → Use next/image
- 🟠 Unnecessary 'use client' → Server Components (50KB less bundle)
- 🟠 Client-side data fetching → Server-side fetching
- 🟡 Missing font optimization → Use next/font
- 🟡 Large library imports → Tree shaking opportunities

## 📊 Example Output

```
================================================================================
  CodePulse Analysis Report - JVM Performance Analyzer
================================================================================
  Directory: /home/user/my-java-app
  Files Analyzed: 156
  Total Lines: 24,583

SUMMARY
--------------------------------------------------------------------------------
  🔴  CRITICAL: 3
  🟠  HIGH:     8
  🟡  MEDIUM:   12
  🟢  LOW:      5
--------------------------------------------------------------------------------
  Total Issues: 28

🔴  CRITICAL ISSUES (3)
================================================================================

  1. N+1 Query Problem - database calls in loop
     Category: Database
     Location: UserRepository.java:42
     Impact: From N+1 queries to 1 query - reduces latency by ~100x
     Solution: Use batch query with IN clause or fetch join

     Code:
       for(User u : users) {
     →   Order o = orderRepo.findByUserId(u.id);
       }

  2. Nested loops with O(N²) complexity
     Category: Performance
     Location: DataProcessor.java:128
     Impact: From O(N×M) to O(N+M) - 1000x faster with proper data structures
     Solution: Use HashSet/HashMap for lookups instead of nested iteration
```

## 🏗️ Architecture

CodePulse is built with a modular, extensible architecture:

```
src/
├── core/                    # Core models and base classes
│   ├── models.py           # Issue, Pattern, AnalysisResult
│   ├── base_analyzer.py    # Abstract base analyzer
│   └── __init__.py
├── analyzers/
│   ├── java/               # Java analyzers
│   │   ├── jvm_analyzer.py
│   │   ├── java17_analyzer.py
│   │   └── java21_analyzer.py
│   └── javascript/         # JS/TS analyzers
│       ├── nodejs_analyzer.py
│       └── nextjs_analyzer.py
├── reporters/              # Output formatters
│   ├── console_reporter.py
│   ├── json_reporter.py
│   └── html_reporter.py
└── cli.py                  # Command-line interface
```

## 🎓 Use Cases

### Development Teams

**Catch issues before code review:**
```bash
# Pre-commit hook
codepulse analyze --analyzer jvm,java21 --fail-on-critical ./src
```

### Tech Leads

**Plan modernization efforts:**
```bash
# Generate modernization roadmap
codepulse analyze --analyzer java21 --format html --output roadmap.html ./src
```

### DevOps/CI Integration

```yaml
# GitHub Actions
- name: Code Quality Analysis
  run: |
    pip install codepulse
    codepulse analyze \
      --analyzer jvm \
      --format json \
      --output codepulse-report.json \
      --fail-on-critical \
      ./src
```

## 📚 Documentation

- [API Documentation](docs/API.md) - Complete API reference
- [Examples](examples/) - Working code examples
- [Guides](guides/) - Framework-specific guides
- [Marketing Content](docs/MARKETING.md) - Use cases and testimonials

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src tests/

# Specific test file
pytest tests/unit/test_models.py
```

## 🤝 Contributing

We welcome contributions! Areas where you can help:

1. **New Analyzers**: Spring Boot 3.3+, React Native, Vue.js
2. **Additional Patterns**: Framework-specific anti-patterns
3. **Language Support**: Python, Go, Rust analyzers
4. **Documentation**: Examples, guides, translations
5. **Reporters**: Markdown, SARIF formats

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🌟 Real-World Impact

### Performance Improvements

- **100x** faster database queries (N+1 elimination)
- **75%** memory reduction (primitive collections)
- **90%** less CPU usage (pattern compilation fixes)
- **50%** smaller bundles (Next.js optimizations)

### Time Savings

- **Hours** saved per code review
- **Days** saved in debugging
- **Weeks** saved in modernization planning

## 🗺️ Roadmap

### v2.1 (Q1 2025)
- [ ] Spring Boot 3.3+ analyzer
- [ ] Python analyzer (Django, Flask)
- [ ] SARIF output format
- [ ] VS Code extension

### v2.2 (Q2 2025)
- [ ] Go analyzer
- [ ] React Native analyzer
- [ ] GitHub App integration
- [ ] Real-time analysis (LSP)

### v3.0 (Q3 2025)
- [ ] Machine learning pattern detection
- [ ] Automatic fix suggestions
- [ ] Team analytics dashboard
- [ ] Multi-repo analysis

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with ❤️ by developers, for developers.

Special thanks to:
- The Java and JavaScript communities
- Contributors and early adopters
- Open source projects that inspired this tool

## 📞 Support

- 📧 Email: support@codepulse.dev
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/codepulse/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/codepulse/issues)
- 📖 Docs: [docs.codepulse.dev](https://docs.codepulse.dev)

---

**Made with 🔍 by the CodePulse Team**

*Elevate Your Code Quality, Amplify Performance*
