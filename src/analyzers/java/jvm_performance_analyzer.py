"""
JVM Performance Analyzer

Deep performance analysis for Java/JVM applications focusing on:
- Memory allocation and GC pressure
- CPU-intensive operations
- String handling and concatenation
- Collection performance
- Autoboxing and primitive types
- Synchronization and locking
- I/O operations
- Reflection and dynamic operations
"""

from pathlib import Path
from typing import Dict, Set
from core.models import Pattern, Severity, Category
from core.base_analyzer import BaseAnalyzer


class JVMPerformanceAnalyzer(BaseAnalyzer):
    """Deep performance analyzer for Java/JVM applications."""

    def __init__(self):
        super().__init__(name="JVM Performance Analyzer")
        self.description = "Deep performance analysis for Java/JVM applications"

    def get_file_extensions(self) -> Set[str]:
        return {'.java'}

    def _init_patterns(self) -> Dict[str, Pattern]:
        return {
            # String Performance
            'string_concat_in_loop': Pattern(
                name='string_concat_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?(\+\=\s*"|\w+\s*=\s*\w+\s*\+\s*")',
                severity=Severity.CRITICAL,
                category=Category.PERFORMANCE,
                description='String concatenation in loop',
                impact='Creates N temporary String objects. 1000 iterations = 50MB+ garbage. Use StringBuilder',
                solution='Use StringBuilder: StringBuilder sb = new StringBuilder(); for(...) { sb.append(...); }'
            ),

            'string_concat_multiple': Pattern(
                name='string_concat_multiple',
                regex=r'String\s+\w+\s*=\s*[^;]*?\+[^;]*?\+[^;]*?\+',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='Multiple string concatenation',
                impact='Creates intermediate String objects causing GC pressure',
                solution='Use String.format() or StringBuilder for multiple concatenations'
            ),

            'string_format_in_loop': Pattern(
                name='string_format_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?String\.format\(',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='String.format() in loop',
                impact='String.format is slower than StringBuilder. Use only when formatting is needed',
                solution='Use StringBuilder if simple concatenation, String.format() only for complex formatting'
            ),

            # Collection Performance
            'arraylist_no_capacity': Pattern(
                name='arraylist_no_capacity',
                regex=r'new\s+ArrayList<[^>]*>\s*\(\s*\)(?!\s*;)',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='ArrayList created without initial capacity',
                impact='Multiple array copies on growth. 1000 adds = 10+ array copies',
                solution='new ArrayList<>(expectedSize) to avoid resizing'
            ),

            'hashmap_no_capacity': Pattern(
                name='hashmap_no_capacity',
                regex=r'new\s+HashMap<[^>]*>\s*\(\s*\)',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='HashMap created without initial capacity',
                impact='Multiple rehashing on growth. Specify capacity: expectedSize / 0.75 + 1',
                solution='new HashMap<>(capacity) to avoid rehashing'
            ),

            'vector_usage': Pattern(
                name='vector_usage',
                regex=r'(new\s+Vector<|Vector<[^>]*>\s+\w+)',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='Using Vector instead of ArrayList',
                impact='Synchronized on every operation. 10x slower than ArrayList in single-threaded code',
                solution='Use ArrayList for single thread, CopyOnWriteArrayList for concurrent reads'
            ),

            'hashtable_usage': Pattern(
                name='hashtable_usage',
                regex=r'(new\s+Hashtable<|Hashtable<[^>]*>\s+\w+)',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='Using Hashtable instead of HashMap',
                impact='Synchronized on every operation. Use HashMap or ConcurrentHashMap',
                solution='HashMap for single thread, ConcurrentHashMap for multi-thread'
            ),

            'linkedlist_random_access': Pattern(
                name='linkedlist_random_access',
                regex=r'LinkedList<[^>]*>[^;]*?\.get\s*\(\s*\d+\s*\)',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='Random access on LinkedList',
                impact='O(N) for get(index). Use ArrayList for random access',
                solution='Use ArrayList for index-based access, LinkedList only for queue operations'
            ),

            # Autoboxing and Primitives
            'autoboxing_in_loop': Pattern(
                name='autoboxing_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*(Integer|Long|Double|Float|Boolean)\s+\w+\s*=',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='Autoboxing in loop',
                impact='Creates N wrapper objects. 1000 iterations = 1000 objects. Use primitives',
                solution='Use primitive types (int, long, double) instead of wrappers in loops'
            ),

            'wrapper_in_collection': Pattern(
                name='wrapper_in_collection',
                regex=r'(ArrayList|HashSet|HashMap)<\s*(Integer|Long|Double|Float|Boolean)',
                severity=Severity.MEDIUM,
                category=Category.MEMORY,
                description='Using wrapper types in collections',
                impact='Each Integer uses 16 bytes vs 4 bytes for int. Consider primitive collections',
                solution='Use Trove, FastUtil, or Eclipse Collections for primitive-optimized collections'
            ),

            # Pattern and Regex
            'pattern_compile_in_loop': Pattern(
                name='pattern_compile_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?Pattern\.compile\(',
                severity=Severity.CRITICAL,
                category=Category.PERFORMANCE,
                description='Pattern.compile() in loop',
                impact='Regex compilation is expensive. 1000x slower than reusing compiled pattern',
                solution='Compile pattern once as static: private static final Pattern PATTERN = Pattern.compile(...)'
            ),

            'string_matches_in_loop': Pattern(
                name='string_matches_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?\.matches\s*\(',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='String.matches() in loop',
                impact='Compiles regex every time. Use precompiled Pattern.matcher()',
                solution='Pre-compile Pattern and reuse: PATTERN.matcher(str).matches()'
            ),

            # Exception Handling
            'exception_for_control_flow': Pattern(
                name='exception_for_control_flow',
                regex=r'catch\s*\([^)]*\)\s*\{\s*\}',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='Empty catch block - possibly using exceptions for flow control',
                impact='Exceptions are 1000x slower than conditional checks',
                solution='Use conditional logic instead of try-catch for flow control'
            ),

            'exception_in_loop': Pattern(
                name='exception_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?try\s*\{',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='Try-catch inside loop',
                impact='Move try-catch outside loop if possible for better performance',
                solution='Wrap entire loop in try-catch or validate before loop'
            ),

            # Synchronization
            'synchronized_method': Pattern(
                name='synchronized_method',
                regex=r'public\s+synchronized\s+\w+',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='Synchronized method',
                impact='Locks entire object. Consider synchronized block for fine-grained locking',
                solution='Use synchronized block with minimal scope or ReentrantLock'
            ),

            'double_checked_locking': Pattern(
                name='double_checked_locking',
                regex=r'if\s*\([^)]*==\s*null\)\s*\{[^}]*synchronized',
                severity=Severity.HIGH,
                category=Category.CONCURRENCY,
                description='Possible broken double-checked locking',
                impact='Can fail without volatile. Use volatile or initialization-on-demand holder',
                solution='Make field volatile or use enum singleton pattern'
            ),

            # Reflection
            'reflection_in_loop': Pattern(
                name='reflection_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*(\.getMethod|\.getDeclaredMethod|\.getField|\.newInstance)',
                severity=Severity.CRITICAL,
                category=Category.PERFORMANCE,
                description='Reflection in loop',
                impact='Reflection is 100x slower than direct access. Cache Method/Field objects',
                solution='Obtain Method/Field once outside loop and reuse'
            ),

            'class_forname': Pattern(
                name='class_forname',
                regex=r'Class\.forName\s*\(',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='Class.forName() usage',
                impact='Expensive operation. Cache Class objects when possible',
                solution='Cache the Class object if called multiple times'
            ),

            # I/O Operations
            'buffered_reader_missing': Pattern(
                name='buffered_reader_missing',
                regex=r'new\s+FileReader\s*\([^)]*\)(?!.*BufferedReader)',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='FileReader without BufferedReader',
                impact='Reads one char at a time. 1000x slower than buffered reading',
                solution='Wrap in BufferedReader: new BufferedReader(new FileReader(...))'
            ),

            'buffered_writer_missing': Pattern(
                name='buffered_writer_missing',
                regex=r'new\s+FileWriter\s*\([^)]*\)(?!.*BufferedWriter)',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='FileWriter without BufferedWriter',
                impact='Writes one char at a time. Use BufferedWriter',
                solution='Wrap in BufferedWriter: new BufferedWriter(new FileWriter(...))'
            ),

            'byte_array_output_stream_no_size': Pattern(
                name='byte_array_output_stream_no_size',
                regex=r'new\s+ByteArrayOutputStream\s*\(\s*\)',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='ByteArrayOutputStream without initial size',
                impact='Multiple array copies on growth. Specify expected size',
                solution='new ByteArrayOutputStream(expectedSize)'
            ),

            # Date and Time
            'simpledateformat_not_cached': Pattern(
                name='simpledateformat_not_cached',
                regex=r'new\s+SimpleDateFormat\s*\(',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='SimpleDateFormat created repeatedly',
                impact='Expensive to create. Cache in ThreadLocal or use DateTimeFormatter (Java 8+)',
                solution='Use ThreadLocal<SimpleDateFormat> or java.time.DateTimeFormatter'
            ),

            'date_usage': Pattern(
                name='date_usage',
                regex=r'new\s+Date\s*\(\s*\)',
                severity=Severity.LOW,
                category=Category.PERFORMANCE,
                description='Using java.util.Date',
                impact='Legacy API. Use java.time (Java 8+) for better performance and API',
                solution='Use Instant.now() or LocalDateTime.now() from java.time'
            ),

            # Stream Operations
            'stream_boxing_unboxing': Pattern(
                name='stream_boxing_unboxing',
                regex=r'\.stream\(\)\.map\((\w+::valueOf|Integer::parseInt)',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='Boxing/unboxing in stream operations',
                impact='Creates wrapper objects. Use primitive streams (IntStream, LongStream)',
                solution='Use mapToInt(), mapToLong(), or primitive stream methods'
            ),

            'parallel_stream_small_data': Pattern(
                name='parallel_stream_small_data',
                regex=r'\.parallelStream\(\)',
                severity=Severity.LOW,
                category=Category.PERFORMANCE,
                description='Parallel stream usage',
                impact='Overhead for small datasets (<1000 items). Benchmark before using',
                solution='Use sequential stream for small data, parallel only for large datasets'
            ),

            # Memory Leaks
            'static_collection_no_cleanup': Pattern(
                name='static_collection_no_cleanup',
                regex=r'private\s+static\s+(final\s+)?(List|Set|Map|Collection)<',
                severity=Severity.MEDIUM,
                category=Category.MEMORY,
                description='Static collection that may cause memory leak',
                impact='Never garbage collected. Ensure items are removed when no longer needed',
                solution='Implement cleanup logic or use WeakHashMap/SoftReference for caches'
            ),

            'thread_local_no_cleanup': Pattern(
                name='thread_local_no_cleanup',
                regex=r'ThreadLocal<[^>]*>(?!.*\.remove\(\))',
                severity=Severity.HIGH,
                category=Category.MEMORY,
                description='ThreadLocal without cleanup',
                impact='Memory leak in thread pools. Always call remove() when done',
                solution='Call threadLocal.remove() in finally block or use try-with-resources'
            ),

            # Logging Performance
            'string_concat_in_log': Pattern(
                name='string_concat_in_log',
                regex=r'log\.(debug|trace|info)\s*\([^)]*\+',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='String concatenation in log statement',
                impact='String built even if log level disabled. Use parameterized logging',
                solution='Use parameterized: log.debug("Value: {}", value) instead of concatenation'
            ),

            'log_without_level_check': Pattern(
                name='log_without_level_check',
                regex=r'log\.(debug|trace)\s*\([^)]*\w+\.toString\(\)',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='Expensive operation in log without level check',
                impact='toString() called even if logging disabled',
                solution='if (log.isDebugEnabled()) { log.debug(...); }'
            ),

            # Object Creation
            'new_object_in_loop': Pattern(
                name='new_object_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?new\s+\w+\s*\(',
                severity=Severity.MEDIUM,
                category=Category.MEMORY,
                description='Object creation in loop',
                impact='Creates N objects. Consider object pooling or reuse for large N',
                solution='Reuse objects when possible or use object pooling for expensive objects'
            ),

            # Clone Performance
            'clone_usage': Pattern(
                name='clone_usage',
                regex=r'\.clone\s*\(\)',
                severity=Severity.LOW,
                category=Category.PERFORMANCE,
                description='Using clone() method',
                impact='Often slower than copy constructor. Shallow vs deep copy issues',
                solution='Use copy constructor or factory method for clarity and performance'
            ),

            # Enum Performance
            'enum_valueof_in_loop': Pattern(
                name='enum_valueof_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?\w+\.valueOf\s*\(',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='Enum.valueOf() in loop',
                impact='String comparison on every enum value. Cache result or use Map',
                solution='Create static Map<String, EnumType> for frequent lookups'
            ),
        }


def main():
    """Example usage of JVM Performance Analyzer."""
    import sys
    from reporters.console_reporter import ConsoleReporter

    if len(sys.argv) < 2:
        print("Usage: python jvm_performance_analyzer.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    analyzer = JVMPerformanceAnalyzer()
    result = analyzer.analyze_directory(directory)

    reporter = ConsoleReporter(use_colors=True, verbose=True)
    reporter.report(result)


if __name__ == '__main__':
    main()
