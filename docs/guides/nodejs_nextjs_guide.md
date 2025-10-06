# Node.js & Next.js Analysis Guide - CodePulse 2.0

## Overview

This guide demonstrates how to use CodePulse to analyze Node.js and Next.js applications for performance issues, anti-patterns, and optimization opportunities.

## Quick Start

### Node.js Analysis

```python
from pathlib import Path
from analyzers.javascript import NodeJSAnalyzer
from reporters import ConsoleReporter

# Create analyzer
analyzer = NodeJSAnalyzer()

# Analyze your Node.js app
result = analyzer.analyze_directory(Path("./your-nodejs-app"))

# View results
ConsoleReporter(use_colors=True, verbose=True).report(result)
```

### Next.js Analysis

```python
from pathlib import Path
from analyzers.javascript import NextJSAnalyzer
from reporters import HTMLReporter

# Create analyzer
analyzer = NextJSAnalyzer()

# Analyze your Next.js app
result = analyzer.analyze_directory(Path("./your-nextjs-app"))

# Generate HTML report
HTMLReporter().report(result, Path("./nextjs-optimization.html"))
```

## Node.js Anti-Patterns

### 1. Event Loop Blocking

**Critical Issue:** Synchronous file operations

**Before:**
```javascript
const data = fs.readFileSync('large-file.json');
const parsed = JSON.parse(data);
```

**After:**
```javascript
const data = await fs.promises.readFile('large-file.json', 'utf-8');
const parsed = JSON.parse(data);
```

**Impact:** Reduces latency by 100x

### 2. N+1 Query Problem

**Critical Issue:** Database calls in loops

**Before:**
```javascript
for (const userId of userIds) {
    const user = await User.findById(userId);
    users.push(user);
}
```

**After:**
```javascript
const users = await User.find({ _id: { $in: userIds } });
```

**Impact:** 1000 items = 1001 queries → 1 query

### 3. Memory Leaks

**High Issue:** Event listeners without cleanup

**Before:**
```javascript
emitter.on('data', (data) => {
    processData(data);
});
// No cleanup!
```

**After:**
```javascript
const handler = (data) => processData(data);
emitter.on('data', handler);

// Cleanup
process.on('exit', () => {
    emitter.removeListener('data', handler);
});
```

**Impact:** Prevents memory leaks

### 4. Unhandled Promises

**Critical Issue:** Promise without error handling

**Before:**
```javascript
fetchData()
    .then(data => processData(data));
// No .catch()!
```

**After:**
```javascript
fetchData()
    .then(data => processData(data))
    .catch(err => logger.error('Failed to fetch data', err));
```

**Impact:** Prevents production crashes

### 5. Stream Handling

**High Issue:** Loading large files without streams

**Before:**
```javascript
const data = await fs.promises.readFile('1GB-file.csv');
// Loads entire file into memory!
```

**After:**
```javascript
const stream = fs.createReadStream('1GB-file.csv');
stream.on('data', chunk => processChunk(chunk));
```

**Impact:** 1GB file = 1GB RAM → constant memory usage

## Next.js Optimizations

### 1. Image Optimization

**High Issue:** Using `<img>` instead of `next/image`

**Before:**
```jsx
<img src="/photo.jpg" alt="Photo" />
```

**After:**
```jsx
import Image from 'next/image';

<Image
    src="/photo.jpg"
    alt="Photo"
    width={500}
    height={300}
    priority  // for above-fold images
/>
```

**Impact:** Automatic WebP, lazy loading, CLS prevention

### 2. Server Components

**High Issue:** Unnecessary 'use client'

**Before:**
```jsx
'use client';

export default function UserList({ users }) {
    return <div>{users.map(u => <div key={u.id}>{u.name}</div>)}</div>;
}
```

**After:**
```jsx
// No 'use client' needed - this is a Server Component
export default function UserList({ users }) {
    return <div>{users.map(u => <div key={u.id}>{u.name}</div>)}</div>;
}
```

**Impact:** Bundle size -50KB, better SEO

### 3. Font Optimization

**Medium Issue:** Manual font loading

**Before:**
```html
<link href="https://fonts.googleapis.com/css2?family=Inter" rel="stylesheet">
```

**After:**
```jsx
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({ children }) {
    return <html className={inter.className}>{children}</html>;
}
```

**Impact:** Eliminates layout shift, faster loading

### 4. Data Fetching

**High Issue:** Client-side data fetching

**Before:**
```jsx
'use client';

export default function Page() {
    const [data, setData] = useState(null);

    useEffect(() => {
        fetch('/api/data')
            .then(res => res.json())
            .then(setData);
    }, []);

    return <div>{data?.value}</div>;
}
```

**After:**
```jsx
// Server Component
async function getData() {
    const res = await fetch('https://api.example.com/data', {
        cache: 'force-cache',
        next: { revalidate: 3600 }
    });
    return res.json();
}

export default async function Page() {
    const data = await getData();
    return <div>{data.value}</div>;
}
```

**Impact:** Better SEO, faster initial load

### 5. Bundle Size

**High Issue:** Importing entire libraries

**Before:**
```javascript
import _ from 'lodash';
import Button from '@mui/material';
```

**After:**
```javascript
import debounce from 'lodash/debounce';
import Button from '@mui/material/Button';
```

**Impact:** Bundle size reduction of 100KB-500KB

## Running Analysis

### Combined Analysis

```python
from pathlib import Path
from analyzers.javascript import NodeJSAnalyzer, NextJSAnalyzer
from reporters import ConsoleReporter
from core import AnalysisResult

# Run both analyzers
nodejs_analyzer = NodeJSAnalyzer()
nextjs_analyzer = NextJSAnalyzer()

# Analyze
nodejs_result = nodejs_analyzer.analyze_directory(Path("./app"))
nextjs_result = nextjs_analyzer.analyze_directory(Path("./app"))

# Combine results
all_issues = nodejs_result.issues + nextjs_result.issues
combined = AnalysisResult(issues=all_issues)

# Report
ConsoleReporter().report(combined)
```

### Filter by Severity

```python
from core import Severity, Category

# Get critical issues
critical = result.get_issues_by_severity(Severity.CRITICAL)

# Get bundle size issues
bundle = result.get_issues_by_category(Category.BUNDLE_SIZE)

# Get event loop issues
event_loop = result.get_issues_by_category(Category.EVENT_LOOP)

print(f"Critical: {len(critical)}")
print(f"Bundle size: {len(bundle)}")
print(f"Event loop: {len(event_loop)}")
```

### Generate Reports

```python
from reporters import JSONReporter, HTMLReporter

# JSON for CI/CD
JSONReporter().report(result, Path("./analysis.json"))

# HTML for team review
HTMLReporter().report(result, Path("./optimization-report.html"))
```

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

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install CodePulse
        run: pip install codepulse

      - name: Run Analysis
        run: |
          python3 << 'EOF'
          from pathlib import Path
          from analyzers.javascript import NodeJSAnalyzer, NextJSAnalyzer
          from reporters import JSONReporter
          from core import Severity
          import sys

          # Analyze
          nodejs = NodeJSAnalyzer()
          nextjs = NextJSAnalyzer()

          result1 = nodejs.analyze_directory(Path("./"))
          result2 = nextjs.analyze_directory(Path("./"))

          # Combine
          all_issues = result1.issues + result2.issues

          # Save report
          from core import AnalysisResult
          combined = AnalysisResult(issues=all_issues)
          JSONReporter().report(combined, Path("./codepulse-report.json"))

          # Check for critical issues
          critical = [i for i in all_issues if i.severity == Severity.CRITICAL]
          if critical:
              print(f"❌ Found {len(critical)} critical issues!")
              sys.exit(1)

          print("✅ Code quality check passed")
          EOF

      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: codepulse-report
          path: codepulse-report.json
```

## Best Practices

### For Node.js

1. **Always use async/await** for I/O operations
2. **Implement connection pooling** for databases
3. **Add error handling** to all promises
4. **Use streams** for large files
5. **Clean up** event listeners and intervals

### For Next.js

1. **Default to Server Components** unless you need interactivity
2. **Use next/image** for all images
3. **Use next/font** for fonts
4. **Fetch data on the server** when possible
5. **Implement proper caching** strategies

## Example Output

```
================================================================================
  CodePulse Analysis Report - Node.js Anti-Pattern Analyzer
================================================================================
  Directory: /home/user/my-app
  Files Analyzed: 89
  Total Lines: 12,450

SUMMARY
--------------------------------------------------------------------------------
  🔴  CRITICAL: 5
  🟠  HIGH:     12
  🟡  MEDIUM:   18
  🟢  LOW:      8
--------------------------------------------------------------------------------
  Total Issues: 43

🔴  CRITICAL ISSUES (5)
================================================================================

  1. N+1 Query Problem
     Location: UserService.js:42
     Impact: 1000 items = 1001 queries instead of 2
     Solution: Use findMany/findAll with array of IDs

  2. Synchronous file operation blocks event loop
     Location: ConfigLoader.js:15
     Impact: Blocks event loop. Using async reduces latency 100x
     Solution: Use fs.promises.readFile()
```

## Additional Resources

- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Server Components](https://react.dev/blog/2023/03/22/react-labs-what-we-have-been-working-on-march-2023)

## Next Steps

1. Run analysis on your application
2. Fix critical issues first
3. Optimize bundle size
4. Implement proper caching
5. Monitor performance improvements
