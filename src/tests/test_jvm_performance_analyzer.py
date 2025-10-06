"""
Tests for JVM Performance Analyzer.
"""

import pytest
from pathlib import Path

from core.models import Severity, Category
from analyzers.java.jvm_performance_analyzer import JVMPerformanceAnalyzer


class TestJVMPerformanceAnalyzerPatterns:
    """Tests for JVM Performance Analyzer pattern matching."""

    def test_has_string_performance_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'string_concat_in_loop' in patterns
        assert 'string_concat_multiple' in patterns
        assert 'string_format_in_loop' in patterns
        assert patterns['string_concat_in_loop'].severity == Severity.CRITICAL

    def test_has_collection_performance_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'arraylist_no_capacity' in patterns
        assert 'hashmap_no_capacity' in patterns
        assert 'vector_usage' in patterns
        assert 'hashtable_usage' in patterns
        assert 'linkedlist_random_access' in patterns

    def test_has_autoboxing_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'autoboxing_in_loop' in patterns
        assert 'wrapper_in_collection' in patterns
        assert patterns['autoboxing_in_loop'].severity == Severity.HIGH

    def test_has_pattern_regex_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'pattern_compile_in_loop' in patterns
        assert 'string_matches_in_loop' in patterns
        assert patterns['pattern_compile_in_loop'].severity == Severity.CRITICAL

    def test_has_exception_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'exception_for_control_flow' in patterns
        assert 'exception_in_loop' in patterns

    def test_has_synchronization_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'synchronized_method' in patterns
        assert 'double_checked_locking' in patterns

    def test_has_reflection_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'reflection_in_loop' in patterns
        assert 'class_forname' in patterns
        assert patterns['reflection_in_loop'].severity == Severity.CRITICAL

    def test_has_io_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'buffered_reader_missing' in patterns
        assert 'buffered_writer_missing' in patterns
        assert 'byte_array_output_stream_no_size' in patterns

    def test_has_memory_leak_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'static_collection_no_cleanup' in patterns
        assert 'thread_local_no_cleanup' in patterns
        assert patterns['thread_local_no_cleanup'].severity == Severity.HIGH

    def test_has_logging_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'string_concat_in_log' in patterns
        assert 'log_without_level_check' in patterns


class TestJVMPerformanceAnalyzerConfiguration:
    """Tests for JVM Performance Analyzer configuration."""

    def test_analyzer_config(self):
        analyzer = JVMPerformanceAnalyzer()
        assert analyzer.name == "JVM Performance Analyzer"
        assert '.java' in analyzer.get_file_extensions()

    def test_all_patterns_have_required_fields(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        for pattern_name, pattern in patterns.items():
            # All patterns must have these fields
            assert pattern.name, f"{pattern_name} missing name"
            assert pattern.regex, f"{pattern_name} missing regex"
            assert pattern.severity, f"{pattern_name} missing severity"
            assert pattern.category, f"{pattern_name} missing category"
            assert pattern.description, f"{pattern_name} missing description"
            assert pattern.impact, f"{pattern_name} missing impact"
            assert hasattr(pattern, 'solution'), f"{pattern_name} missing solution attribute"

    def test_has_enough_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()
        # Should have at least 30 patterns for comprehensive coverage
        assert len(patterns) >= 30, f"Only {len(patterns)} patterns found"


class TestJVMPerformanceAnalyzerSeverity:
    """Tests for severity distribution."""

    def test_has_critical_patterns(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()
        critical = [p for p in patterns.values() if p.severity == Severity.CRITICAL]
        # Performance analyzer should have several critical patterns
        assert len(critical) >= 3, f"Should have at least 3 CRITICAL patterns, found {len(critical)}"

    def test_has_varied_severity(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        critical = [p for p in patterns.values() if p.severity == Severity.CRITICAL]
        high = [p for p in patterns.values() if p.severity == Severity.HIGH]
        medium = [p for p in patterns.values() if p.severity == Severity.MEDIUM]
        low = [p for p in patterns.values() if p.severity == Severity.LOW]

        # Should have patterns across severity levels
        assert len(critical) > 0, "Should have CRITICAL patterns"
        assert len(high) > 0, "Should have HIGH patterns"
        assert len(medium) > 0, "Should have MEDIUM patterns"
        # LOW patterns are optional for performance analyzer


class TestJVMPerformanceAnalyzerCategories:
    """Tests for category distribution."""

    def test_has_performance_category(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()
        performance = [p for p in patterns.values() if p.category == Category.PERFORMANCE]
        # Most patterns should be performance-related
        assert len(performance) >= 15, f"Should have many PERFORMANCE patterns, found {len(performance)}"

    def test_has_memory_category(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()
        memory = [p for p in patterns.values() if p.category == Category.MEMORY]
        assert len(memory) > 0, "Should have MEMORY patterns"

    def test_has_concurrency_category(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()
        concurrency = [p for p in patterns.values() if p.category == Category.CONCURRENCY]
        # Should have at least one concurrency pattern
        assert len(concurrency) > 0, "Should have CONCURRENCY patterns"


class TestJVMPerformanceAnalyzerImpactMessages:
    """Tests for impact message quality."""

    def test_impact_messages_have_numbers(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        # At least a third of patterns should quantify impact
        patterns_with_numbers = [
            p for p in patterns.values()
            if any(char.isdigit() for char in p.impact)
        ]

        assert len(patterns_with_numbers) >= len(patterns) // 3, \
            f"At least a third of patterns should quantify impact with numbers, found {len(patterns_with_numbers)} out of {len(patterns)}"

    def test_critical_patterns_have_quantified_impact(self):
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        critical = [p for p in patterns.values() if p.severity == Severity.CRITICAL]

        for pattern in critical:
            # Critical patterns should quantify their impact
            has_number = any(char.isdigit() for char in pattern.impact)
            has_comparison = any(word in pattern.impact.lower() for word in ['faster', 'slower', 'x', 'times'])

            assert has_number or has_comparison, \
                f"Critical pattern '{pattern.name}' should quantify impact: {pattern.impact}"


class TestJVMPerformanceAnalyzerPatternGroups:
    """Tests for logical grouping of patterns."""

    def test_string_patterns_group(self):
        """Test that string-related patterns exist."""
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        string_patterns = [
            name for name in patterns.keys()
            if 'string' in name.lower()
        ]

        assert len(string_patterns) >= 3, "Should have multiple string performance patterns"

    def test_collection_patterns_group(self):
        """Test that collection-related patterns exist."""
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        collection_patterns = [
            name for name in patterns.keys()
            if any(word in name.lower() for word in ['arraylist', 'hashmap', 'vector', 'hashtable', 'linkedlist'])
        ]

        assert len(collection_patterns) >= 5, "Should have multiple collection performance patterns"

    def test_io_patterns_group(self):
        """Test that I/O-related patterns exist."""
        analyzer = JVMPerformanceAnalyzer()
        patterns = analyzer._init_patterns()

        io_patterns = [
            name for name in patterns.keys()
            if any(word in name.lower() for word in ['reader', 'writer', 'stream'])
        ]

        assert len(io_patterns) >= 3, "Should have multiple I/O performance patterns"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
