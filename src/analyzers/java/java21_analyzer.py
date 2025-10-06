#!/usr/bin/env python3
"""
Java 21 Modernization Analyzer - identifies opportunities to use Java 21 features.

This analyzer detects code patterns that can be modernized using Java 21 features:
- Virtual Threads for improved concurrency
- Pattern Matching for cleaner type checks
- Records for immutable data classes
- Sequenced Collections for better APIs
- String Templates for safer string formatting
- Structured Concurrency for better async code
"""

from typing import Dict, Set

from core import BaseAnalyzer, Pattern, Category, Severity


class Java21Analyzer(BaseAnalyzer):
    """
    Analyzer for Java 21 modernization opportunities.

    Identifies code that can benefit from new Java 21 features and provides
    specific upgrade recommendations.
    """

    def __init__(self):
        """Initialize the Java 21 analyzer."""
        super().__init__(name="Java 21 Modernization Analyzer")

    def get_file_extensions(self) -> Set[str]:
        """Get file extensions for Java code."""
        return {'.java'}

    def _init_patterns(self) -> Dict[str, Pattern]:
        """Initialize Java 21 feature detection patterns."""
        return {
            # VIRTUAL THREADS
            'platform_thread_pool': Pattern(
                name='platform_thread_pool',
                regex=r'Executors\.(newFixedThreadPool|newCachedThreadPool)\s*\(',
                category=Category.MODERNIZATION,
                severity=Severity.HIGH,
                description='Traditional thread pool (Java 21: use Virtual Threads)',
                impact='Virtual Threads: ~1M threads vs ~4K platform threads',
                solution='Use Executors.newVirtualThreadPerTaskExecutor() for I/O-bound tasks',
                metadata={
                    'java_version': 21,
                    'feature': 'Virtual Threads',
                    'jep': 444,
                    'example_before': 'ExecutorService executor = Executors.newFixedThreadPool(100);',
                    'example_after': 'ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();'
                }
            ),

            'blocking_with_platform_threads': Pattern(
                name='blocking_with_platform_threads',
                regex=r'(Socket|HttpClient|InputStream).*newFixedThreadPool',
                category=Category.MODERNIZATION,
                severity=Severity.CRITICAL,
                description='Blocking I/O with platform threads',
                impact='From 4K to 1M+ concurrent requests with Virtual Threads',
                solution='Use Virtual Threads for all I/O-bound operations',
                metadata={
                    'java_version': 21,
                    'feature': 'Virtual Threads'
                }
            ),

            # PATTERN MATCHING
            'instanceof_cast': Pattern(
                name='instanceof_cast',
                regex=r'instanceof\s+(\w+)\s*\)\s*\{\s*(\w+)\s*=\s*\(\1\)',
                category=Category.MODERNIZATION,
                severity=Severity.MEDIUM,
                description='instanceof followed by manual cast (Java 21: Pattern Matching)',
                impact='Reduces boilerplate and prevents ClassCastException',
                solution='Use pattern matching: if (obj instanceof String s) { use s directly }',
                metadata={
                    'java_version': 16,
                    'feature': 'Pattern Matching for instanceof',
                    'jep': 394,
                    'example_before': 'if (obj instanceof String) {\n    String s = (String) obj;\n    return s.length();\n}',
                    'example_after': 'if (obj instanceof String s) {\n    return s.length();\n}'
                }
            ),

            'traditional_switch_type': Pattern(
                name='traditional_switch_type',
                regex=r'switch\s*\([^)]+\)\s*\{[^}]*instanceof',
                category=Category.MODERNIZATION,
                severity=Severity.HIGH,
                description='Switch with instanceof checks (Java 21: Pattern Matching Switch)',
                impact='Type-safe, null-safe, and more concise',
                solution='Use switch with pattern matching',
                metadata={
                    'java_version': 21,
                    'feature': 'Pattern Matching for switch',
                    'jep': 441,
                    'example_after': 'return switch(obj) {\n    case String s -> s.length();\n    case Integer i -> i;\n    case null -> 0;\n    default -> -1;\n};'
                }
            ),

            # RECORDS
            'pojo_immutable': Pattern(
                name='pojo_immutable',
                regex=r'class\s+\w+\s*\{[^}]*private\s+final\s+\w+[^}]*public\s+\w+\s+get',
                category=Category.MODERNIZATION,
                severity=Severity.LOW,
                description='Immutable POJO (Java 21: consider using Record)',
                impact='Records auto-generate equals/hashCode/toString',
                solution='Replace with record for simple data carriers',
                metadata={
                    'java_version': 16,
                    'feature': 'Records',
                    'jep': 395,
                    'example_after': 'public record Point(int x, int y) {}'
                }
            ),

            # SEQUENCED COLLECTIONS
            'manual_first_last': Pattern(
                name='manual_first_last',
                regex=r'\.(get\(0\)|get\(.*\.size\(\)\s*-\s*1\))',
                category=Category.MODERNIZATION,
                severity=Severity.LOW,
                description='Manual first/last element access',
                impact='Clearer API with getFirst()/getLast()',
                solution='Use sequenced collection methods',
                metadata={
                    'java_version': 21,
                    'feature': 'Sequenced Collections',
                    'jep': 431,
                    'example_before': 'list.get(0) and list.get(list.size() - 1)',
                    'example_after': 'list.getFirst() and list.getLast()'
                }
            ),

            'manual_reverse': Pattern(
                name='manual_reverse',
                regex=r'Collections\.reverse\s*\(',
                category=Category.MODERNIZATION,
                severity=Severity.LOW,
                description='Manual list reversal',
                impact='More efficient reversed() view',
                solution='Use list.reversed() for read-only reverse view',
                metadata={
                    'java_version': 21,
                    'feature': 'Sequenced Collections'
                }
            ),

            # SCOPED VALUES
            'threadlocal_with_virtual': Pattern(
                name='threadlocal_with_virtual',
                regex=r'ThreadLocal<[^>]+>',
                category=Category.MODERNIZATION,
                severity=Severity.MEDIUM,
                description='ThreadLocal (Java 21: consider Scoped Values with Virtual Threads)',
                impact='Scoped Values: better with Virtual Threads, automatic cleanup',
                solution='Use ScopedValue for immutable per-thread data',
                metadata={
                    'java_version': 21,
                    'feature': 'Scoped Values',
                    'jep': 446,
                    'example_after': 'private static final ScopedValue<User> CURRENT_USER = ScopedValue.newInstance();'
                }
            ),

            # STRING TEMPLATES
            'string_format': Pattern(
                name='string_format',
                regex=r'String\.format\s*\(\s*"[^"]*%[sd]',
                category=Category.MODERNIZATION,
                severity=Severity.LOW,
                description='String.format() (Java 21: String Templates - Preview)',
                impact='More readable and type-safe string interpolation',
                solution='Use String Templates (when finalized)',
                metadata={
                    'java_version': 21,
                    'feature': 'String Templates',
                    'jep': 430,
                    'status': 'Preview',
                    'example_after': 'STR."User \\{name} has \\{points} points"'
                }
            ),

            'string_concat_builder': Pattern(
                name='string_concat_builder',
                regex=r'new\s+StringBuilder\(\)\.append\([^)]+\)\.append',
                category=Category.MODERNIZATION,
                severity=Severity.LOW,
                description='StringBuilder for simple concatenation',
                impact='String Templates provide cleaner syntax',
                solution='Consider String Templates for readable string building',
                metadata={
                    'java_version': 21,
                    'feature': 'String Templates',
                    'status': 'Preview'
                }
            ),

            # SWITCH EXPRESSIONS
            'switch_with_breaks': Pattern(
                name='switch_with_breaks',
                regex=r'switch\s*\([^)]+\)\s*\{[^}]*break;',
                category=Category.MODERNIZATION,
                severity=Severity.LOW,
                description='Switch statement with breaks (Java 21: Switch Expressions)',
                impact='More concise with exhaustiveness checking',
                solution='Use switch expressions with arrow syntax',
                metadata={
                    'java_version': 14,
                    'feature': 'Switch Expressions',
                    'jep': 361,
                    'example_after': 'var result = switch(day) {\n    case MONDAY, FRIDAY -> 6;\n    case TUESDAY -> 7;\n    default -> 8;\n};'
                }
            ),

            # STRUCTURED CONCURRENCY
            'future_get': Pattern(
                name='future_get',
                regex=r'Future.*\.get\(\)',
                category=Category.MODERNIZATION,
                severity=Severity.MEDIUM,
                description='Future.get() blocking (Java 21: Structured Concurrency)',
                impact='Better error handling and automatic cancellation',
                solution='Use StructuredTaskScope for related concurrent tasks',
                metadata={
                    'java_version': 21,
                    'feature': 'Structured Concurrency',
                    'jep': 453,
                    'status': 'Preview',
                    'example_after': '''try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var user = scope.fork(() -> findUser());
    var order = scope.fork(() -> findOrder());
    scope.join().throwIfFailed();
    return new Result(user.resultNow(), order.resultNow());
}'''
                }
            ),

            'completablefuture_all': Pattern(
                name='completablefuture_all',
                regex=r'CompletableFuture\.allOf\s*\(',
                category=Category.MODERNIZATION,
                severity=Severity.MEDIUM,
                description='CompletableFuture.allOf (Java 21: Structured Concurrency)',
                impact='Cleaner error handling with StructuredTaskScope',
                solution='Use StructuredTaskScope for coordinated tasks',
                metadata={
                    'java_version': 21,
                    'feature': 'Structured Concurrency'
                }
            ),

            # UNNAMED PATTERNS AND VARIABLES
            'unused_exception_variable': Pattern(
                name='unused_exception_variable',
                regex=r'catch\s*\(\s*\w+\s+(\w+)\s*\)\s*\{[^}]*\}',
                category=Category.MODERNIZATION,
                severity=Severity.LOW,
                description='Unused exception variable',
                impact='Use unnamed variable (_) for unused catch parameters',
                solution='Replace unused exception variable with _',
                metadata={
                    'java_version': 21,
                    'feature': 'Unnamed Patterns and Variables',
                    'jep': 443,
                    'example_after': 'catch (IOException _) { ... }'
                }
            ),
        }
