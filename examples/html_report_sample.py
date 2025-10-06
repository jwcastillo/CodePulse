#!/usr/bin/env python3
"""
Genera un reporte HTML de ejemplo con datos de muestra
Muestra todos los tipos de issues y severidades
"""

import sys
import os
import webbrowser
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from reporters.html_reporter import HTMLReporter
from core.models import AnalysisResult, Issue, Severity, Category


def create_sample_result() -> AnalysisResult:
    """Crea un resultado de análisis con datos de ejemplo."""
    result = AnalysisResult()
    result.files_analyzed = 25
    result.total_lines = 5420
    result.metadata['analyzer'] = 'JVM Performance Analyzer'
    result.metadata['directory'] = '/home/user/projects/my-java-app/src'

    # Issues CRITICAL
    result.add_issue(Issue(
        category=Category.PERFORMANCE,
        severity=Severity.CRITICAL,
        file_path='src/main/java/com/example/service/UserService.java',
        line_number=45,
        code_snippet='''public List<User> getAllUsers() {
    List<User> users = userRepository.findAll();
    for (User user : users) {
        user.setOrders(orderRepository.findByUserId(user.getId()));
    }
    return users;
}''',
        description='N+1 query problem in user loading',
        potential_impact='100x slower queries. For 1000 users = 1001 database queries instead of 2. Can cause 30+ second response times and database overload.',
        solution='Use JOIN FETCH or entity graph: @EntityGraph(attributePaths = {"orders"}) to load users and orders in a single query'
    ))

    result.add_issue(Issue(
        category=Category.PERFORMANCE,
        severity=Severity.CRITICAL,
        file_path='src/main/java/com/example/utils/StringUtils.java',
        line_number=23,
        code_snippet='''String result = "";
for (int i = 0; i < 1000; i++) {
    result += data[i];
}''',
        description='String concatenation in loop',
        potential_impact='Creates 1000 temporary String objects. 50MB+ garbage for 1000 iterations. 1000x slower than StringBuilder.',
        solution='Use StringBuilder: StringBuilder sb = new StringBuilder(); for(...) { sb.append(data[i]); } return sb.toString();'
    ))

    result.add_issue(Issue(
        category=Category.SECURITY,
        severity=Severity.CRITICAL,
        file_path='src/main/java/com/example/controller/SearchController.java',
        line_number=67,
        code_snippet='''String query = "SELECT * FROM products WHERE name LIKE '%" + searchTerm + "%'";
List<Product> results = jdbcTemplate.query(query, productMapper);''',
        description='SQL injection vulnerability',
        potential_impact='Database can be compromised. Attacker can read/modify/delete any data using searchTerm = "\'; DROP TABLE users--"',
        solution='Use PreparedStatement: "SELECT * FROM products WHERE name LIKE ?" with jdbcTemplate.query(sql, productMapper, "%" + searchTerm + "%")'
    ))

    # Issues HIGH
    result.add_issue(Issue(
        category=Category.MEMORY,
        severity=Severity.HIGH,
        file_path='src/main/java/com/example/cache/CacheManager.java',
        line_number=89,
        code_snippet='''private static final Map<String, byte[]> cache = new HashMap<>();

public void addToCache(String key, byte[] data) {
    cache.put(key, data);
}''',
        description='Unbounded cache without eviction policy',
        potential_impact='Memory leak. Can consume all heap memory (OutOfMemoryError) as cache grows indefinitely.',
        solution='Use Caffeine cache with size limit: LoadingCache<String, byte[]> cache = Caffeine.newBuilder().maximumSize(10_000).build()'
    ))

    result.add_issue(Issue(
        category=Category.PERFORMANCE,
        severity=Severity.HIGH,
        file_path='src/main/java/com/example/service/ReportService.java',
        line_number=120,
        code_snippet='''public synchronized Report generateReport(String reportId) {
    // Report generation takes 5 seconds
    return reportGenerator.generate(reportId);
}''',
        description='Synchronized method for long-running operation',
        potential_impact='Blocks all threads. With 100 concurrent users, 99 wait 5+ seconds each. Throughput: 0.2 requests/sec instead of 20.',
        solution='Use asynchronous processing: @Async public CompletableFuture<Report> generateReport(String reportId)'
    ))

    result.add_issue(Issue(
        category=Category.PERFORMANCE,
        severity=Severity.HIGH,
        file_path='src/main/java/com/example/controller/FileController.java',
        line_number=34,
        code_snippet='''@GetMapping("/files/{id}")
public ResponseEntity<byte[]> downloadFile(@PathVariable String id) {
    byte[] fileContent = fileService.readFile(id);
    return ResponseEntity.ok(fileContent);
}''',
        description='Loading entire file into memory',
        potential_impact='OutOfMemoryError for large files. 100MB file = 100MB heap usage per request. 10 concurrent = 1GB consumed.',
        solution='Use streaming: return ResponseEntity.ok().body(new InputStreamResource(fileService.getFileStream(id)))'
    ))

    # Issues MEDIUM
    result.add_issue(Issue(
        category=Category.PERFORMANCE,
        severity=Severity.MEDIUM,
        file_path='src/main/java/com/example/model/User.java',
        line_number=15,
        code_snippet='''@OneToMany(fetch = FetchType.EAGER)
private List<Order> orders;''',
        description='EAGER fetching for collection',
        potential_impact='Loads all orders even when not needed. 100 users = loads all orders from DB. 10x slower queries.',
        solution='Change to LAZY: @OneToMany(fetch = FetchType.LAZY) and use JOIN FETCH when needed'
    ))

    result.add_issue(Issue(
        category=Category.BEST_PRACTICE,
        severity=Severity.MEDIUM,
        file_path='src/main/java/com/example/config/AppConfig.java',
        line_number=28,
        code_snippet='''@Bean
public DataSource dataSource() {
    HikariDataSource ds = new HikariDataSource();
    ds.setMaximumPoolSize(100);
    ds.setMinimumIdle(50);
    return ds;
}''',
        description='Oversized connection pool',
        potential_impact='50-100 idle connections consume 500MB+ memory. Recommended: CPU cores * 2 (typically 8-16).',
        solution='Set reasonable pool size: ds.setMaximumPoolSize(10); ds.setMinimumIdle(2);'
    ))

    result.add_issue(Issue(
        category=Category.PERFORMANCE,
        severity=Severity.MEDIUM,
        file_path='src/main/java/com/example/utils/PatternMatcher.java',
        line_number=42,
        code_snippet='''public boolean matches(String input) {
    return input.matches("\\\\d{3}-\\\\d{2}-\\\\d{4}");
}''',
        description='Pattern compilation in method call',
        potential_impact='Recompiles regex on every call. 1000x slower than pre-compiled Pattern.',
        solution='Compile once: private static final Pattern PATTERN = Pattern.compile("\\\\d{3}-\\\\d{2}-\\\\d{4}"); public boolean matches(String input) { return PATTERN.matcher(input).matches(); }'
    ))

    # Issues LOW
    result.add_issue(Issue(
        category=Category.BEST_PRACTICE,
        severity=Severity.LOW,
        file_path='src/main/java/com/example/service/EmailService.java',
        line_number=56,
        code_snippet='''@Autowired
private JavaMailSender mailSender;

@PostConstruct
public void init() {
    mailSender.send(createWelcomeEmail());
}''',
        description='Heavy initialization in @PostConstruct',
        potential_impact='Slows down application startup. Not critical but adds 2-5 seconds to boot time.',
        solution='Move to lazy initialization or background task'
    ))

    result.add_issue(Issue(
        category=Category.PERFORMANCE,
        severity=Severity.LOW,
        file_path='src/main/java/com/example/utils/LoggerUtils.java',
        line_number=18,
        code_snippet='''public void logDebug(String message, Object... args) {
    log.debug("Processing: " + String.format(message, args));
}''',
        description='String concatenation with logging',
        potential_impact='Creates String even when debug is disabled. Minor performance impact.',
        solution='Use parameterized logging: log.debug("Processing: {}", String.format(message, args))'
    ))

    return result


def main():
    print("=" * 80)
    print("CodePulse HTML Report - Sample Data")
    print("=" * 80)
    print()

    # Crear resultado con datos de ejemplo
    print("📊 Creando resultado de análisis de ejemplo...")
    result = create_sample_result()

    print(f"✅ Datos de ejemplo creados:")
    print(f"   - Total issues: {len(result.issues)}")
    print(f"   - CRITICAL: {len(result.get_issues_by_severity(Severity.CRITICAL))}")
    print(f"   - HIGH: {len(result.get_issues_by_severity(Severity.HIGH))}")
    print(f"   - MEDIUM: {len(result.get_issues_by_severity(Severity.MEDIUM))}")
    print(f"   - LOW: {len(result.get_issues_by_severity(Severity.LOW))}")
    print()

    # Generar reporte HTML
    print("📄 Generando reporte HTML...")
    reporter = HTMLReporter()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(__file__).parent.parent / 'reports'
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f'codepulse_sample_report_{timestamp}.html'

    reporter.report(result, output_file)

    print(f"✅ Reporte generado:")
    print(f"   - Archivo: {output_file}")
    print(f"   - Tamaño: {output_file.stat().st_size:,} bytes")
    print()

    # Abrir en navegador
    print("🌐 Abriendo reporte en navegador...")
    file_url = output_file.absolute().as_uri()

    try:
        webbrowser.open(file_url)
        print(f"✅ Reporte abierto en navegador")
    except Exception as e:
        print(f"⚠️  No se pudo abrir: {e}")

    print()
    print("=" * 80)
    print("✅ Reporte de ejemplo generado")
    print("=" * 80)
    print()
    print("Este reporte incluye ejemplos de:")
    print("  🔴 3 issues CRITICAL (N+1, String concat, SQL injection)")
    print("  🟠 3 issues HIGH (Memory leak, Sync blocking, File loading)")
    print("  🟡 3 issues MEDIUM (Eager fetch, Pool size, Pattern compile)")
    print("  🟢 2 issues LOW (PostConstruct, String concatenation)")
    print()
    print(f"Ver reporte en: {output_file}")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
