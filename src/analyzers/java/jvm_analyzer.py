#!/usr/bin/env python3
"""
JVM Code Analyzer - detects performance anti-patterns in JVM-based code.

This analyzer focuses on common JVM optimization opportunities including:
- String concatenation in loops
- Autoboxing issues
- Pattern compilation inefficiencies
- Nested loops and algorithmic complexity
- Repository/database access patterns
- Memory leaks in static collections
"""

from typing import Dict, Set
from pathlib import Path

from core import BaseAnalyzer, Pattern, Category, Severity


class JVMAnalyzer(BaseAnalyzer):
    """
    Analyzer for JVM performance anti-patterns.

    Detects common performance issues in Java/Kotlin code that can
    significantly impact application performance and resource usage.
    """

    def __init__(self):
        """Initialize the JVM analyzer."""
        super().__init__(name="JVM Performance Analyzer")

    def get_file_extensions(self) -> Set[str]:
        """Get file extensions for JVM languages."""
        return {'.java', '.kt', '.scala'}

    def _init_patterns(self) -> Dict[str, Pattern]:
        """Initialize JVM-specific detection patterns."""
        return {
            'string_concat_loop': Pattern(
                name='string_concat_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?\+\=.*?["\']',
                category=Category.PERFORMANCE,
                severity=Severity.HIGH,
                description='String concatenation in loop',
                impact='Reduces allocations from ~50MB to ~200KB per 10K iterations',
                solution='Use StringBuilder outside the loop or String.join() for collections',
                metadata={
                    'example_bad': 'String s = ""; for(...) { s += "x"; }',
                    'example_good': 'StringBuilder sb = new StringBuilder(); for(...) { sb.append("x"); }'
                }
            ),

            'autoboxing_collections': Pattern(
                name='autoboxing_collections',
                regex=r'(List|Set|Map)<(Integer|Long|Double|Float|Boolean)>',
                category=Category.MEMORY,
                severity=Severity.MEDIUM,
                description='Autoboxing in Collections (consider primitive collections)',
                impact='Reduces heap usage by ~75% (16MB → 4MB per 1M items)',
                solution='Use primitive collections like IntArrayList, LongHashSet from fastutil or Eclipse Collections',
                metadata={
                    'example_bad': 'List<Integer> numbers = new ArrayList<>();',
                    'example_good': 'IntArrayList numbers = new IntArrayList(); // from fastutil'
                }
            ),

            'pattern_in_loop': Pattern(
                name='pattern_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?(matches|Pattern\.compile)',
                category=Category.PERFORMANCE,
                severity=Severity.HIGH,
                description='Pattern compilation in loop (compile once, reuse)',
                impact='Reduces CPU usage by ~90%',
                solution='Compile Pattern as static final field and reuse',
                metadata={
                    'example_bad': 'for(String s : list) { if(s.matches("\\\\d+")) {...} }',
                    'example_good': 'private static final Pattern DIGITS = Pattern.compile("\\\\d+");\nfor(String s : list) { if(DIGITS.matcher(s).matches()) {...} }'
                }
            ),

            'nested_loops': Pattern(
                name='nested_loops',
                regex=r'for\s*\([^)]+\)\s*\{\s*[^}]*?for\s*\([^)]+\)',
                category=Category.PERFORMANCE,
                severity=Severity.CRITICAL,
                description='Nested loops with O(N²) complexity',
                impact='From O(N×M) to O(N+M) - 1000x faster with proper data structures',
                solution='Use HashSet/HashMap for lookups instead of nested iteration',
                metadata={
                    'example_bad': 'for(A a : listA) { for(B b : listB) { if(a.id == b.id) {...} } }',
                    'example_good': 'Map<Id, B> mapB = listB.stream().collect(toMap(B::getId, identity()));\nfor(A a : listA) { B b = mapB.get(a.id); if(b != null) {...} }'
                }
            ),

            'repository_in_loop': Pattern(
                name='repository_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?(Repository|\.find)',
                category=Category.DATABASE,
                severity=Severity.CRITICAL,
                description='N+1 Query Problem - database calls in loop',
                impact='From N+1 queries to 1 query - reduces latency by ~100x',
                solution='Use batch query with IN clause or fetch join',
                metadata={
                    'example_bad': 'for(User u : users) { Order o = orderRepo.findByUserId(u.id); }',
                    'example_good': 'List<Order> orders = orderRepo.findByUserIdIn(users.stream().map(User::getId).toList());'
                }
            ),

            'static_collection_no_limit': Pattern(
                name='static_collection_no_limit',
                regex=r'(private|public)\s+static\s+final\s+(Map|List|Set)<[^>]+>\s+\w+\s*=\s*new',
                category=Category.MEMORY,
                severity=Severity.CRITICAL,
                description='Static collection without size limit (potential memory leak)',
                impact='Prevents memory leaks and OutOfMemoryError',
                solution='Use bounded cache like Caffeine or implement size limit with LRU eviction',
                metadata={
                    'example_bad': 'private static final Map<String, Data> CACHE = new HashMap<>();',
                    'example_good': 'private static final LoadingCache<String, Data> CACHE = Caffeine.newBuilder().maximumSize(10_000).build(key -> loadData(key));'
                }
            ),

            'thread_sleep_in_loop': Pattern(
                name='thread_sleep_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?Thread\.sleep',
                category=Category.PERFORMANCE,
                severity=Severity.HIGH,
                description='Thread.sleep() in loop (use scheduled executor instead)',
                impact='Better resource management and cancellation support',
                solution='Use ScheduledExecutorService for periodic tasks',
                metadata={
                    'example_bad': 'while(running) { doWork(); Thread.sleep(1000); }',
                    'example_good': 'ScheduledExecutorService executor = Executors.newScheduledThreadPool(1);\nexecutor.scheduleAtFixedRate(() -> doWork(), 0, 1, TimeUnit.SECONDS);'
                }
            ),

            'exception_for_flow_control': Pattern(
                name='exception_for_flow_control',
                regex=r'try\s*\{[^}]*?\}\s*catch\s*\([^)]*\)\s*\{\s*\}',
                category=Category.CODE_SMELL,
                severity=Severity.MEDIUM,
                description='Empty catch block or exception-driven control flow',
                impact='Exceptions are expensive; validate inputs instead',
                solution='Use explicit validation instead of try-catch for expected conditions',
                metadata={
                    'example_bad': 'try { int x = Integer.parseInt(str); } catch(NumberFormatException e) { x = 0; }',
                    'example_good': 'int x = str.matches("\\\\d+") ? Integer.parseInt(str) : 0;'
                }
            ),

            'synchronization_granularity': Pattern(
                name='synchronization_granularity',
                regex=r'synchronized\s*\([^)]*\)\s*\{[^}]{200,}',
                category=Category.CONCURRENCY,
                severity=Severity.HIGH,
                description='Large synchronized block (reduces concurrency)',
                impact='Reduces lock contention and improves throughput',
                solution='Reduce synchronized block scope or use fine-grained locks',
                metadata={
                    'tips': 'Lock only the critical section, not the entire method'
                }
            ),

            'date_in_loop': Pattern(
                name='date_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?new\s+(Date|SimpleDateFormat|Calendar)',
                category=Category.PERFORMANCE,
                severity=Severity.MEDIUM,
                description='Date/Calendar object creation in loop',
                impact='Reduce object allocations by ~80%',
                solution='Create once before loop or use DateTimeFormatter (thread-safe)',
                metadata={
                    'example_bad': 'for(Record r : records) { Date d = new Date(); ... }',
                    'example_good': 'Instant now = Instant.now();\nfor(Record r : records) { ... }'
                }
            ),
        }
