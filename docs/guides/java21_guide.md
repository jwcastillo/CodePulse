# Java 21 Modernization Guide - CodePulse 2.0

## Overview

This guide shows how to use CodePulse's Java 21 analyzer to identify modernization opportunities in your Java codebase.

## Quick Start

```python
from pathlib import Path
from analyzers.java import Java21Analyzer
from reporters import ConsoleReporter, HTMLReporter

# Create analyzer
analyzer = Java21Analyzer()

# Analyze your project
result = analyzer.analyze_directory(Path("./your-java-project"))

# View results
ConsoleReporter(use_colors=True, verbose=True).report(result)

# Or generate HTML report
HTMLReporter().report(result, Path("./java21-modernization.html"))
```

## What It Detects

### 1. Virtual Threads (JEP 444)

**Before:**
```java
ExecutorService executor = Executors.newFixedThreadPool(100);
executor.submit(() -> {
    // I/O-bound task
    String data = httpClient.send(request);
    return processData(data);
});
```

**After:**
```java
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
executor.submit(() -> {
    // Can handle millions of concurrent tasks
    String data = httpClient.send(request);
    return processData(data);
});
```

**Impact:** From 4K to 1M+ concurrent requests

### 2. Pattern Matching for Switch (JEP 441)

**Before:**
```java
String formatted;
if (obj instanceof Integer) {
    Integer i = (Integer) obj;
    formatted = String.format("int %d", i);
} else if (obj instanceof String) {
    String s = (String) obj;
    formatted = String.format("String %s", s);
} else {
    formatted = obj.toString();
}
```

**After:**
```java
String formatted = switch (obj) {
    case Integer i -> String.format("int %d", i);
    case String s  -> String.format("String %s", s);
    case null      -> "null";
    default        -> obj.toString();
};
```

**Impact:** Type-safe, null-safe, more concise

### 3. Sequenced Collections (JEP 431)

**Before:**
```java
List<String> list = new ArrayList<>();
String first = list.get(0);
String last = list.get(list.size() - 1);
```

**After:**
```java
List<String> list = new ArrayList<>();
String first = list.getFirst();
String last = list.getLast();
```

**Impact:** Clearer API, less error-prone

### 4. Records (JEP 395)

**Before:**
```java
public class Point {
    private final int x;
    private final int y;

    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    public int getX() { return x; }
    public int getY() { return y; }

    @Override
    public boolean equals(Object o) { /* ... */ }
    @Override
    public int hashCode() { /* ... */ }
    @Override
    public String toString() { /* ... */ }
}
```

**After:**
```java
public record Point(int x, int y) {}
```

**Impact:** 90% less boilerplate code

### 5. String Templates (Preview - JEP 430)

**Before:**
```java
String message = String.format("User %s has %d points", name, points);
```

**After:**
```java
String message = STR."User \{name} has \{points} points";
```

**Impact:** More readable, type-safe string interpolation

### 6. Structured Concurrency (Preview - JEP 453)

**Before:**
```java
Future<User> userFuture = executor.submit(() -> findUser(id));
Future<Order> orderFuture = executor.submit(() -> findOrder(id));

User user = userFuture.get();
Order order = orderFuture.get();
```

**After:**
```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var userTask = scope.fork(() -> findUser(id));
    var orderTask = scope.fork(() -> findOrder(id));

    scope.join().throwIfFailed();

    User user = userTask.resultNow();
    Order order = orderTask.resultNow();
}
```

**Impact:** Better error handling, automatic cleanup

## Running the Analyzer

### Basic Analysis

```python
from pathlib import Path
from analyzers.java import Java21Analyzer
from reporters import ConsoleReporter

analyzer = Java21Analyzer()
result = analyzer.analyze_directory(Path("./src"))

reporter = ConsoleReporter()
reporter.report(result)
```

### Filter Critical Issues

```python
from core import Severity

# Get only high-priority modernization opportunities
critical = result.get_issues_by_severity(Severity.CRITICAL)
high = result.get_issues_by_severity(Severity.HIGH)

print(f"Critical: {len(critical)}")
print(f"High: {len(high)}")
```

### Generate Modernization Roadmap

```python
from reporters import HTMLReporter

# Generate interactive HTML report
HTMLReporter().report(result, Path("./modernization-roadmap.html"))
```

## Best Practices

1. **Start with Virtual Threads**
   - Biggest impact for I/O-bound applications
   - Easy to adopt (just change Executor)
   - Minimal code changes required

2. **Use Pattern Matching Gradually**
   - Start with instanceof checks
   - Then move to switch expressions
   - Refactor incrementally

3. **Convert to Records**
   - Identify immutable POJOs
   - Convert simple data carriers first
   - Keep validation logic separate

4. **Monitor Preview Features**
   - String Templates (Preview)
   - Structured Concurrency (Preview)
   - Wait for finalization before production use

## Integration with CI/CD

```python
# ci_check.py
from pathlib import Path
from analyzers.java import Java21Analyzer
from reporters import JSONReporter
import sys

analyzer = Java21Analyzer()
result = analyzer.analyze_directory(Path("./src"))

# Save report
JSONReporter().report(result, Path("./java21-opportunities.json"))

# Count high-priority opportunities
critical = result.get_issues_by_severity(Severity.CRITICAL)
high = result.get_issues_by_severity(Severity.HIGH)

print(f"Found {len(critical) + len(high)} high-priority modernization opportunities")

# Optional: Fail build if many opportunities
if len(critical) > 10:
    print("⚠️ Many Virtual Thread opportunities - consider modernizing")
    sys.exit(1)
```

## Example Output

```
================================================================================
  CodePulse Analysis Report - Java 21 Modernization Analyzer
================================================================================
  Directory: /home/user/my-java-app
  Files Analyzed: 156
  Total Lines: 24,583

SUMMARY
--------------------------------------------------------------------------------
  🔴  CRITICAL: 8
  🟠  HIGH:     15
  🟡  MEDIUM:   23
  🟢  LOW:      12
--------------------------------------------------------------------------------
  Total Issues: 58

🔴  CRITICAL ISSUES (8)
================================================================================

  1. Traditional thread pool (Java 21: use Virtual Threads)
     Location: WebServer.java:42
     Impact: Virtual Threads: ~1M threads vs ~4K platform threads
     Solution: Use Executors.newVirtualThreadPerTaskExecutor()

  2. Blocking I/O with platform threads
     Location: ApiClient.java:128
     Impact: From 4K to 1M+ concurrent requests with Virtual Threads
     Solution: Use Virtual Threads for all I/O-bound operations
```

## Additional Resources

- [JEP 444: Virtual Threads](https://openjdk.org/jeps/444)
- [JEP 441: Pattern Matching for switch](https://openjdk.org/jeps/441)
- [JEP 431: Sequenced Collections](https://openjdk.org/jeps/431)
- [Java 21 Documentation](https://docs.oracle.com/en/java/javase/21/)

## Next Steps

1. Run analysis on your codebase
2. Prioritize Virtual Thread adoption
3. Generate HTML roadmap
4. Plan incremental migration
5. Monitor preview features for production readiness
