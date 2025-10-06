"""
Spring Data JPA Analyzer

Detects anti-patterns and optimization opportunities in Spring Data JPA applications:
- N+1 query problems
- Missing fetch strategies
- Repository anti-patterns
- Transaction issues
- Query optimization opportunities
"""

from pathlib import Path
from typing import Dict, Set
from core.models import Pattern, Severity, Category
from core.base_analyzer import BaseAnalyzer


class SpringDataAnalyzer(BaseAnalyzer):
    """Analyzer for Spring Data JPA anti-patterns and optimizations."""

    def __init__(self):
        super().__init__(name="Spring Data JPA Analyzer")
        self.description = "Detects anti-patterns in Spring Data JPA repositories and entities"

    def get_file_extensions(self) -> Set[str]:
        return {'.java'}

    def _init_patterns(self) -> Dict[str, Pattern]:
        return {
            # N+1 Query Problems
            'lazy_in_loop': Pattern(
                name='lazy_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?\.get[A-Z]\w+\(\)',
                severity=Severity.CRITICAL,
                category=Category.PERFORMANCE,
                description='N+1 Query Problem - Lazy loading in loop',
                impact='1000 entities = 1001 queries. Can cause 100x performance degradation',
                solution='Use @EntityGraph, JOIN FETCH in query, or batch fetching'
            ),

            'missing_entity_graph': Pattern(
                name='missing_entity_graph',
                regex=r'@OneToMany(?!\s*\([^)]*fetch\s*=\s*FetchType\.EAGER)[^;]*?(?!@EntityGraph)',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='@OneToMany without @EntityGraph or eager fetching',
                impact='Potential N+1 queries when accessing related entities',
                solution='Add @EntityGraph(attributePaths = "relationName") to repository method'
            ),

            'repository_findall_no_pagination': Pattern(
                name='repository_findall_no_pagination',
                regex=r'(findAll\(\)|findBy\w+\([^)]*\))\s*(?!.*Pageable)',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='Repository findAll without pagination',
                impact='Loading entire table into memory. OutOfMemoryError with large datasets',
                solution='Add Pageable parameter: findAll(Pageable pageable)'
            ),

            # Repository Anti-patterns
            'derived_query_too_complex': Pattern(
                name='derived_query_too_complex',
                regex=r'findBy\w+And\w+And\w+And\w+',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='Complex derived query method with multiple AND clauses',
                impact='Poor readability and potential performance issues',
                solution='Use @Query with JPQL or named query for better control'
            ),

            'repository_in_loop': Pattern(
                name='repository_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?(Repository|\w+Repository\.)\.find',
                severity=Severity.CRITICAL,
                category=Category.PERFORMANCE,
                description='Repository call inside loop - N+1 problem',
                impact='N iterations = N database queries instead of 1',
                solution='Use findAllById() or findByIdIn() with batch query'
            ),

            'save_in_loop': Pattern(
                name='save_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?\.save\(',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='save() called in loop instead of batch',
                impact='N saves = N database round trips. Very slow for bulk operations',
                solution='Use saveAll() or batch processing with flush intervals'
            ),

            # Transaction Issues
            'missing_transactional': Pattern(
                name='missing_transactional',
                regex=r'public\s+\w+\s+\w+\([^)]*\)\s*\{[^}]*?\.save\(',
                severity=Severity.MEDIUM,
                category=Category.DATABASE,
                description='Data modification without @Transactional',
                impact='Potential data inconsistency, no transaction rollback on errors',
                solution='Add @Transactional annotation to service method'
            ),

            'transactional_on_repository': Pattern(
                name='transactional_on_repository',
                regex=r'@Repository[^}]*?@Transactional',
                severity=Severity.MEDIUM,
                category=Category.DATABASE,
                description='@Transactional on Repository instead of Service',
                impact='Transaction boundaries in wrong layer, harder to manage',
                solution='Move @Transactional to Service layer methods'
            ),

            'readonly_not_marked': Pattern(
                name='readonly_not_marked',
                regex=r'public\s+\w+\s+find\w+\([^)]*\)\s*\{(?!.*readOnly)',
                severity=Severity.LOW,
                category=Category.PERFORMANCE,
                description='Read-only operation without @Transactional(readOnly = true)',
                impact='Missed optimization opportunity for read operations',
                solution='Add @Transactional(readOnly = true) to read methods'
            ),

            # Query Optimization
            'select_n_plus_1': Pattern(
                name='select_n_plus_1',
                regex=r'@Query\s*\(\s*"SELECT\s+\w+\s+FROM\s+\w+(?!.*JOIN\s+FETCH)',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='Query without JOIN FETCH for associations',
                impact='Lazy loading triggers N+1 queries',
                solution='Add JOIN FETCH for associated entities in query'
            ),

            'native_query_overuse': Pattern(
                name='native_query_overuse',
                regex=r'@Query\s*\(\s*value\s*=\s*"[^"]*",\s*nativeQuery\s*=\s*true',
                severity=Severity.LOW,
                category=Category.PERFORMANCE,
                description='Native query when JPQL would work',
                impact='Database-specific, harder to test, no entity caching',
                solution='Use JPQL unless native features are required'
            ),

            'missing_index_hint': Pattern(
                name='missing_index_hint',
                regex=r'@Column(?!\s*\([^)]*indexed)',
                severity=Severity.LOW,
                category=Category.DATABASE,
                description='Column without index consideration',
                impact='Potential slow queries if used in WHERE clauses',
                solution='Add @Index if column is frequently queried'
            ),

            # Entity Design Issues
            'bidirectional_no_helper': Pattern(
                name='bidirectional_no_helper',
                regex=r'@OneToMany\s*\([^)]*mappedBy[^}]*?(?!public\s+void\s+add)',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='Bidirectional relationship without helper methods',
                impact='Risk of inconsistent bidirectional state',
                solution='Add helper methods to maintain both sides of relationship'
            ),

            'cascade_all': Pattern(
                name='cascade_all',
                regex=r'cascade\s*=\s*CascadeType\.ALL',
                severity=Severity.MEDIUM,
                category=Category.DATABASE,
                description='CascadeType.ALL used - potential unintended cascades',
                impact='Accidental deletion or persistence of related entities',
                solution='Use specific cascade types: PERSIST, MERGE, etc.'
            ),

            'equals_hashcode_missing': Pattern(
                name='equals_hashcode_missing',
                regex=r'@Entity[^}]*?class\s+\w+(?!.*@EqualsAndHashCode)(?!.*public\s+boolean\s+equals)',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='Entity without equals/hashCode implementation',
                impact='Collections and caching may not work correctly',
                solution='Implement equals/hashCode based on business key or use @EqualsAndHashCode'
            ),

            # Batch and Bulk Operations
            'no_batch_size': Pattern(
                name='no_batch_size',
                regex=r'saveAll\((?!.*@BatchSize)',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='Batch save without batch size configuration',
                impact='Not using JDBC batch for bulk operations',
                solution='Configure spring.jpa.properties.hibernate.jdbc.batch_size'
            ),

            'delete_in_loop': Pattern(
                name='delete_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*?\.delete\(',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='delete() called in loop',
                impact='N deletes = N database queries. Very slow',
                solution='Use deleteAll() or deleteInBatch() for bulk deletes'
            ),

            # Projection Issues
            'no_projection_for_large_entity': Pattern(
                name='no_projection_for_large_entity',
                regex=r'List<\w+>\s+findBy\w+\(',
                severity=Severity.LOW,
                category=Category.PERFORMANCE,
                description='Fetching full entity when projection would suffice',
                impact='Over-fetching data, larger memory footprint',
                solution='Use DTO projection or interface-based projection'
            ),

            # Connection and Session Management
            'missing_connection_pool': Pattern(
                name='missing_connection_pool',
                regex=r'spring\.datasource\.(?!hikari)(?!type)',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='DataSource without explicit connection pool configuration',
                impact='Default settings may not be optimal for production',
                solution='Configure HikariCP with appropriate pool size'
            ),
        }


def main():
    """Example usage of Spring Data JPA Analyzer."""
    import sys
    from reporters.console_reporter import ConsoleReporter

    if len(sys.argv) < 2:
        print("Usage: python spring_data_analyzer.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    analyzer = SpringDataAnalyzer()
    result = analyzer.analyze_directory(directory)

    reporter = ConsoleReporter(use_colors=True, verbose=True)
    reporter.report(result)


if __name__ == '__main__':
    main()
