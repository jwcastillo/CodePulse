#!/usr/bin/env python3
"""
Java 17 LTS Analyzer - identifies opportunities to use Java 17 LTS features.

This analyzer focuses on Java 17 LTS modernization:
- Sealed classes for controlled inheritance
- Pattern matching for instanceof (finalized in 17)
- Text blocks for multi-line strings
- Enhanced pseudo-random number generators
- Helpful NullPointerExceptions
"""

from typing import Dict, Set

from core import BaseAnalyzer, Pattern, Category, Severity


class Java17Analyzer(BaseAnalyzer):
    """
    Analyzer for Java 17 LTS modernization opportunities.

    Helps projects on older versions (8, 11) identify code that would
    benefit from Java 17 LTS features.
    """

    def __init__(self):
        """Initialize the Java 17 analyzer."""
        super().__init__(name="Java 17 LTS Modernization Analyzer")

    def get_file_extensions(self) -> Set[str]:
        """Get file extensions for Java code."""
        return {'.java'}

    def _init_patterns(self) -> Dict[str, Pattern]:
        """Initialize Java 17 feature detection patterns."""
        return {
            # TEXT BLOCKS
            'multiline_string_concat': Pattern(
                name='multiline_string_concat',
                regex=r'"\s*\+\s*\n\s*".*\+\s*\n',
                category=Category.MODERNIZATION,
                severity=Severity.MEDIUM,
                description='Multi-line string concatenation (Java 17: Text Blocks)',
                impact='More readable multi-line strings',
                solution='Use text blocks with triple quotes',
                metadata={
                    'java_version': 15,
                    'feature': 'Text Blocks',
                    'jep': 378,
                    'example_before': '"SELECT * FROM users " +\n"WHERE id = ?"',
                    'example_after': '"""\n    SELECT * FROM users\n    WHERE id = ?\n    """'
                }
            ),

            'json_string_concat': Pattern(
                name='json_string_concat',
                regex=r'"\{\s*\\".*\\".*\+',
                category=Category.MODERNIZATION,
                severity=Severity.MEDIUM,
                description='JSON string with escaped quotes (Java 17: Text Blocks)',
                impact='Eliminates escape sequences in JSON/XML/HTML',
                solution='Use text blocks for embedded languages',
                metadata={
                    'java_version': 15,
                    'feature': 'Text Blocks'
                }
            ),

            # SEALED CLASSES
            'inheritance_documentation': Pattern(
                name='inheritance_documentation',
                regex=r'/\*\*[^*]*@apiNote[^*]*permitted[^*]*\*/',
                category=Category.MODERNIZATION,
                severity=Severity.LOW,
                description='Documentation-only inheritance restrictions',
                impact='Sealed classes enforce permitted subtypes at compile-time',
                solution='Use sealed classes with permits clause',
                metadata={
                    'java_version': 17,
                    'feature': 'Sealed Classes',
                    'jep': 409,
                    'example_after': 'public sealed class Shape permits Circle, Rectangle, Square {}'
                }
            ),

            # PATTERN MATCHING
            'instanceof_with_cast': Pattern(
                name='instanceof_with_cast',
                regex=r'if\s*\(\s*\w+\s+instanceof\s+\w+\s*\)\s*\{[^}]*\(\w+\)',
                category=Category.MODERNIZATION,
                severity=Severity.MEDIUM,
                description='instanceof with explicit cast',
                impact='Pattern matching eliminates cast and reduces errors',
                solution='Use pattern matching for instanceof',
                metadata={
                    'java_version': 16,
                    'feature': 'Pattern Matching for instanceof',
                    'example_before': 'if (obj instanceof String) {\n    String s = (String) obj;',
                    'example_after': 'if (obj instanceof String s) {'
                }
            ),

            # RANDOM NUMBER GENERATION
            'random_constructor': Pattern(
                name='random_constructor',
                regex=r'new\s+Random\s*\(',
                category=Category.MODERNIZATION,
                severity=Severity.LOW,
                description='Traditional Random class',
                impact='Enhanced PRNGs offer better algorithms and performance',
                solution='Use RandomGeneratorFactory for modern algorithms',
                metadata={
                    'java_version': 17,
                    'feature': 'Enhanced Pseudo-Random Number Generators',
                    'jep': 356,
                    'example_after': 'RandomGenerator random = RandomGeneratorFactory.of("L128X256MixRandom").create();'
                }
            ),

            # STREAM API ENHANCEMENTS
            'stream_collect_to_list': Pattern(
                name='stream_collect_to_list',
                regex=r'\.collect\s*\(\s*Collectors\.toList\s*\(\s*\)\s*\)',
                category=Category.MODERNIZATION,
                severity=Severity.LOW,
                description='Stream collect to list (Java 17: simpler toList())',
                impact='More concise with Stream.toList()',
                solution='Use .toList() instead of .collect(Collectors.toList())',
                metadata={
                    'java_version': 16,
                    'feature': 'Stream.toList()',
                    'example_before': 'list.stream().filter(...).collect(Collectors.toList())',
                    'example_after': 'list.stream().filter(...).toList()'
                }
            ),

            # SWITCH EXPRESSIONS (finalized in Java 14, but worth mentioning for pre-14)
            'switch_assignment': Pattern(
                name='switch_assignment',
                regex=r'(\w+)\s*=\s*null;\s*switch\s*\([^)]+\)\s*\{[^}]*\1\s*=',
                category=Category.MODERNIZATION,
                severity=Severity.MEDIUM,
                description='Variable assignment in switch',
                impact='Switch expressions eliminate temporary variables',
                solution='Use switch expression',
                metadata={
                    'java_version': 14,
                    'feature': 'Switch Expressions',
                    'example_after': 'var result = switch(value) {\n    case A -> 1;\n    case B -> 2;\n    default -> 0;\n};'
                }
            ),

            # HELPFUL NULLPOINTEREXCEPTIONS (enabled by default in Java 17)
            'null_check_comment': Pattern(
                name='null_check_comment',
                regex=r'//.*NPE.*\n.*if\s*\([^)]*!=\s*null',
                category=Category.MODERNIZATION,
                severity=Severity.LOW,
                description='Manual NPE documentation',
                impact='Java 17 provides helpful NPE messages by default',
                solution='Rely on enhanced NPE messages in Java 17+',
                metadata={
                    'java_version': 14,
                    'feature': 'Helpful NullPointerExceptions',
                    'jep': 358,
                    'note': 'Enabled by default in Java 17'
                }
            ),

            # RECORDS (finalized in Java 16)
            'data_class_with_getters': Pattern(
                name='data_class_with_getters',
                regex=r'class\s+\w+\s*\{[^}]*private\s+final[^}]*public\s+\w+\s+get\w+\s*\(',
                category=Category.MODERNIZATION,
                severity=Severity.MEDIUM,
                description='Data class with getters (Java 17: Records)',
                impact='Records reduce boilerplate significantly',
                solution='Use record for immutable data carriers',
                metadata={
                    'java_version': 16,
                    'feature': 'Records',
                    'example_after': 'public record User(String name, int age) {}'
                }
            ),

            # DEPRECATIONS
            'security_manager_usage': Pattern(
                name='security_manager_usage',
                regex=r'System\.(get|set)SecurityManager|SecurityManager',
                category=Category.MODERNIZATION,
                severity=Severity.HIGH,
                description='SecurityManager usage (deprecated in Java 17)',
                impact='SecurityManager is deprecated for removal',
                solution='Use OS-level security or containerization instead',
                metadata={
                    'java_version': 17,
                    'feature': 'SecurityManager Deprecation',
                    'jep': 411,
                    'status': 'Deprecated for removal'
                }
            ),

            'finalization_override': Pattern(
                name='finalization_override',
                regex=r'protected\s+void\s+finalize\s*\(\s*\)',
                category=Category.MODERNIZATION,
                severity=Severity.HIGH,
                description='Finalizer usage (deprecated in Java 9)',
                impact='Use try-with-resources or Cleaner API',
                solution='Replace finalize() with Cleaner or AutoCloseable',
                metadata={
                    'java_version': 9,
                    'feature': 'Finalization Deprecation',
                    'jep': 421,
                    'example_after': 'class Resource implements AutoCloseable {\n    @Override\n    public void close() { ... }\n}'
                }
            ),
        }
