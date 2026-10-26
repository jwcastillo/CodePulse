#!/usr/bin/env python3
"""
Unit tests for analyzers.
"""

import pytest
from pathlib import Path
from analyzers.java import JVMAnalyzer, Java21Analyzer
from analyzers.javascript import NodeJSAnalyzer, NextJSAnalyzer
from core import Severity, Category


class TestJVMAnalyzer:
    """Test JVM analyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = JVMAnalyzer()
        assert analyzer.name == "JVM Performance Analyzer"
        assert len(analyzer.patterns) > 0

    def test_file_extensions(self):
        """Test supported file extensions."""
        analyzer = JVMAnalyzer()
        extensions = analyzer.get_file_extensions()
        assert '.java' in extensions
        assert '.kt' in extensions
        assert '.scala' in extensions

    def test_pattern_initialization(self):
        """Test that patterns are properly initialized."""
        analyzer = JVMAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'string_concat_loop' in patterns
        assert 'nested_loops' in patterns
        assert 'repository_in_loop' in patterns

        # Check pattern properties
        pattern = patterns['string_concat_loop']
        assert pattern.severity == Severity.HIGH
        assert pattern.category == Category.PERFORMANCE


class TestJava21Analyzer:
    """Test Java 21 analyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = Java21Analyzer()
        assert analyzer.name == "Java 21 Modernization Analyzer"

    def test_java21_patterns(self):
        """Test Java 21 specific patterns."""
        analyzer = Java21Analyzer()
        patterns = analyzer._init_patterns()

        assert 'platform_thread_pool' in patterns
        assert 'instanceof_cast' in patterns
        assert 'pojo_immutable' in patterns

        # Check virtual threads pattern
        vt_pattern = patterns['platform_thread_pool']
        assert vt_pattern.metadata.get('java_version') == 21
        assert 'Virtual Threads' in vt_pattern.solution


class TestNodeJSAnalyzer:
    """Test Node.js analyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = NodeJSAnalyzer()
        assert analyzer.name == "Node.js Anti-Pattern Analyzer"

    def test_file_extensions(self):
        """Test supported file extensions."""
        analyzer = NodeJSAnalyzer()
        extensions = analyzer.get_file_extensions()
        assert '.js' in extensions
        assert '.ts' in extensions
        assert '.mjs' in extensions

    def test_nodejs_patterns(self):
        """Test Node.js patterns."""
        analyzer = NodeJSAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'sync_file_operations' in patterns
        assert 'unhandled_promise' in patterns
        assert 'query_in_loop' in patterns

        # Check event loop pattern
        pattern = patterns['sync_file_operations']
        assert pattern.severity == Severity.CRITICAL
        assert pattern.category == Category.EVENT_LOOP


class TestNextJSAnalyzer:
    """Test Next.js analyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = NextJSAnalyzer()
        assert analyzer.name == "Next.js Optimization Analyzer"

    def test_nextjs_patterns(self):
        """Test Next.js specific patterns."""
        analyzer = NextJSAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'use_client_unnecessary' in patterns
        assert 'img_tag_no_next_image' in patterns
        assert 'font_no_optimization' in patterns

        # Check image optimization pattern
        pattern = patterns['img_tag_no_next_image']
        assert pattern.severity == Severity.HIGH
        assert 'next/image' in pattern.solution


class TestAnalyzerBase:
    """Test base analyzer functionality."""

    def test_pattern_management(self):
        """Test adding/removing patterns."""
        analyzer = JVMAnalyzer()
        initial_count = len(analyzer.patterns)

        # Disable pattern
        analyzer.disable_pattern('string_concat_loop')
        assert analyzer.patterns['string_concat_loop'].enabled is False

        # Enable pattern
        analyzer.enable_pattern('string_concat_loop')
        assert analyzer.patterns['string_concat_loop'].enabled is True

        # Remove pattern
        analyzer.remove_pattern('string_concat_loop')
        assert 'string_concat_loop' not in analyzer.patterns
        assert len(analyzer.patterns) == initial_count - 1


class TestPatternCustomizationSurvivesAnalysis:
    """Regression: analyze_directory used to reload patterns, discarding disable/remove/add calls."""

    JAVA = 'class S { String f(java.util.List<String> xs){ String o=""; for (String x : xs) { o += x + ","; } return o; } }'

    def test_disabled_pattern_is_not_reported(self, tmp_path):
        (tmp_path / "S.java").write_text(self.JAVA)
        analyzer = JVMAnalyzer()
        assert any(i.metadata["pattern"] == "string_concat_loop" for i in analyzer.analyze_directory(tmp_path).issues)
        analyzer.disable_pattern("string_concat_loop")
        for _ in range(2):  # and it stays disabled on later runs
            issues = analyzer.analyze_directory(tmp_path).issues
            assert not any(i.metadata["pattern"] == "string_concat_loop" for i in issues)

    def test_removed_pattern_is_not_reported(self, tmp_path):
        (tmp_path / "S.java").write_text(self.JAVA)
        analyzer = JVMAnalyzer()
        analyzer.remove_pattern("string_concat_loop")
        assert not any(i.metadata["pattern"] == "string_concat_loop" for i in analyzer.analyze_directory(tmp_path).issues)
