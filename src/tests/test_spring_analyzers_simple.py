"""
Simplified tests for Spring analyzers that test pattern matching directly.
"""

import pytest
from pathlib import Path

from core.models import Severity, Category, Pattern
from analyzers.java.spring_data_analyzer import SpringDataAnalyzer
from analyzers.java.spring_security_analyzer import SpringSecurityAnalyzer
from analyzers.java.spring_rest_analyzer import SpringRestAnalyzer


class TestSpringDataAnalyzerPatterns:
    """Tests for Spring Data JPA Analyzer pattern matching."""

    def test_has_n_plus_one_patterns(self):
        analyzer = SpringDataAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'lazy_in_loop' in patterns
        assert 'repository_in_loop' in patterns
        assert patterns['lazy_in_loop'].severity == Severity.CRITICAL
        assert patterns['repository_in_loop'].severity == Severity.CRITICAL

    def test_has_transaction_patterns(self):
        analyzer = SpringDataAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'missing_transactional' in patterns
        assert 'transactional_on_repository' in patterns

    def test_has_batch_operation_patterns(self):
        analyzer = SpringDataAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'save_in_loop' in patterns
        assert 'delete_in_loop' in patterns
        assert patterns['save_in_loop'].severity == Severity.HIGH


class TestSpringSecurityAnalyzerPatterns:
    """Tests for Spring Security Analyzer pattern matching."""

    def test_has_csrf_patterns(self):
        analyzer = SpringSecurityAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'csrf_disabled' in patterns
        assert patterns['csrf_disabled'].severity == Severity.CRITICAL
        assert patterns['csrf_disabled'].category == Category.SECURITY

    def test_has_cors_patterns(self):
        analyzer = SpringSecurityAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'cors_allow_all' in patterns
        assert 'cors_credentials_with_wildcard' in patterns
        assert patterns['cors_allow_all'].severity == Severity.CRITICAL

    def test_has_authentication_patterns(self):
        analyzer = SpringSecurityAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'hardcoded_credentials' in patterns
        assert 'weak_password_encoder' in patterns
        assert 'password_in_memory' in patterns

    def test_has_authorization_patterns(self):
        analyzer = SpringSecurityAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'permit_all_endpoints' in patterns
        assert 'missing_method_security' in patterns


class TestSpringRestAnalyzerPatterns:
    """Tests for Spring REST API Analyzer pattern matching."""

    def test_has_validation_patterns(self):
        analyzer = SpringRestAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'missing_valid_annotation' in patterns
        assert 'entity_in_request' in patterns
        assert 'entity_in_response' in patterns

    def test_has_http_method_patterns(self):
        analyzer = SpringRestAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'get_with_body' in patterns
        assert 'delete_returning_body' in patterns
        assert 'post_not_returning_201' in patterns

    def test_has_pagination_patterns(self):
        analyzer = SpringRestAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'list_without_pagination' in patterns
        assert patterns['list_without_pagination'].severity == Severity.HIGH

    def test_has_error_handling_patterns(self):
        analyzer = SpringRestAnalyzer()
        patterns = analyzer._init_patterns()

        assert 'missing_exception_handler' in patterns
        assert 'generic_exception_catch' in patterns
        assert 'stacktrace_in_response' in patterns
        assert patterns['stacktrace_in_response'].severity == Severity.CRITICAL


class TestSpringAnalyzersConfiguration:
    """Tests for Spring analyzers configuration and metadata."""

    def test_spring_data_analyzer_config(self):
        analyzer = SpringDataAnalyzer()
        assert analyzer.name == "Spring Data JPA Analyzer"
        assert '.java' in analyzer.get_file_extensions()

    def test_spring_security_analyzer_config(self):
        analyzer = SpringSecurityAnalyzer()
        assert analyzer.name == "Spring Security Analyzer"
        assert '.java' in analyzer.get_file_extensions()

    def test_spring_rest_analyzer_config(self):
        analyzer = SpringRestAnalyzer()
        assert analyzer.name == "Spring REST API Analyzer"
        assert '.java' in analyzer.get_file_extensions()

    def test_all_patterns_have_required_fields(self):
        analyzers = [
            SpringDataAnalyzer(),
            SpringSecurityAnalyzer(),
            SpringRestAnalyzer()
        ]

        for analyzer in analyzers:
            patterns = analyzer._init_patterns()
            for pattern_name, pattern in patterns.items():
                # All patterns must have these fields
                assert pattern.name, f"{pattern_name} missing name"
                assert pattern.regex, f"{pattern_name} missing regex"
                assert pattern.severity, f"{pattern_name} missing severity"
                assert pattern.category, f"{pattern_name} missing category"
                assert pattern.description, f"{pattern_name} missing description"
                assert pattern.impact, f"{pattern_name} missing impact"
                # Solution can be empty but should exist
                assert hasattr(pattern, 'solution'), f"{pattern_name} missing solution attribute"


class TestSpringAnalyzersPatternCounts:
    """Tests to ensure analyzers have sufficient pattern coverage."""

    def test_spring_data_has_enough_patterns(self):
        analyzer = SpringDataAnalyzer()
        patterns = analyzer._init_patterns()
        # Should have at least 15 patterns for comprehensive coverage
        assert len(patterns) >= 15, f"Only {len(patterns)} patterns found"

    def test_spring_security_has_enough_patterns(self):
        analyzer = SpringSecurityAnalyzer()
        patterns = analyzer._init_patterns()
        # Should have at least 15 patterns for comprehensive coverage
        assert len(patterns) >= 15, f"Only {len(patterns)} patterns found"

    def test_spring_rest_has_enough_patterns(self):
        analyzer = SpringRestAnalyzer()
        patterns = analyzer._init_patterns()
        # Should have at least 20 patterns for comprehensive coverage
        assert len(patterns) >= 20, f"Only {len(patterns)} patterns found"


class TestSpringAnalyzersSeverityDistribution:
    """Tests to ensure proper severity distribution."""

    def test_spring_data_has_critical_patterns(self):
        analyzer = SpringDataAnalyzer()
        patterns = analyzer._init_patterns()
        critical = [p for p in patterns.values() if p.severity == Severity.CRITICAL]
        assert len(critical) >= 2, "Should have at least 2 CRITICAL patterns"

    def test_spring_security_has_many_critical_patterns(self):
        analyzer = SpringSecurityAnalyzer()
        patterns = analyzer._init_patterns()
        critical = [p for p in patterns.values() if p.severity == Severity.CRITICAL]
        # Security should have many critical patterns
        assert len(critical) >= 8, f"Security analyzer should have many CRITICAL patterns, found {len(critical)}"

    def test_spring_rest_has_varied_severity(self):
        analyzer = SpringRestAnalyzer()
        patterns = analyzer._init_patterns()

        critical = [p for p in patterns.values() if p.severity == Severity.CRITICAL]
        high = [p for p in patterns.values() if p.severity == Severity.HIGH]
        medium = [p for p in patterns.values() if p.severity == Severity.MEDIUM]
        low = [p for p in patterns.values() if p.severity == Severity.LOW]

        # Should have patterns across all severity levels
        assert len(critical) > 0, "Should have CRITICAL patterns"
        assert len(high) > 0, "Should have HIGH patterns"
        assert len(medium) > 0, "Should have MEDIUM patterns"
        assert len(low) > 0, "Should have LOW patterns"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
