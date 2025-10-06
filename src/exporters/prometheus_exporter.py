"""
Prometheus Metrics Exporter for CodePulse

Exporta métricas de análisis de código a Prometheus para visualización en Grafana.

Métricas exportadas:
- Total de issues por severity
- Total de issues por category
- Total de issues por analyzer
- Tendencias temporales
- Archivos analizados
- Líneas de código
"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json

from core.models import AnalysisResult, Severity, Category


class PrometheusExporter:
    """Exportador de métricas en formato Prometheus."""

    def __init__(self):
        self.metrics: List[str] = []
        self.timestamp = int(datetime.now().timestamp() * 1000)

    def export_result(self, result: AnalysisResult, analyzer_name: str,
                     project_name: str = "default",
                     branch: str = "main",
                     commit_sha: str = "unknown") -> str:
        """
        Exporta resultado de análisis como métricas Prometheus.

        Args:
            result: Resultado del análisis
            analyzer_name: Nombre del analyzer
            project_name: Nombre del proyecto
            branch: Branch de git
            commit_sha: SHA del commit

        Returns:
            String con métricas en formato Prometheus
        """
        self.metrics = []
        labels = f'project="{project_name}",branch="{branch}",analyzer="{analyzer_name}",commit="{commit_sha[:8]}"'

        # Métricas básicas
        self._export_basic_metrics(result, labels)

        # Métricas por severity
        self._export_severity_metrics(result, labels)

        # Métricas por category
        self._export_category_metrics(result, labels)

        # Métricas de tendencia
        self._export_trend_metrics(result, labels)

        return "\n".join(self.metrics)

    def _export_basic_metrics(self, result: AnalysisResult, labels: str):
        """Exporta métricas básicas."""
        # Total de issues
        self.metrics.append(
            f'codepulse_total_issues{{{labels}}} {len(result.issues)} {self.timestamp}'
        )

        # Archivos analizados
        self.metrics.append(
            f'codepulse_files_analyzed{{{labels}}} {result.files_analyzed} {self.timestamp}'
        )

        # Líneas de código
        self.metrics.append(
            f'codepulse_total_lines{{{labels}}} {result.total_lines} {self.timestamp}'
        )

        # Issues por 1000 líneas (densidad)
        if result.total_lines > 0:
            density = (len(result.issues) / result.total_lines) * 1000
            self.metrics.append(
                f'codepulse_issue_density{{{labels}}} {density:.2f} {self.timestamp}'
            )

    def _export_severity_metrics(self, result: AnalysisResult, labels: str):
        """Exporta métricas por severity."""
        severities = {
            'critical': Severity.CRITICAL,
            'high': Severity.HIGH,
            'medium': Severity.MEDIUM,
            'low': Severity.LOW,
            'info': Severity.INFO
        }

        for sev_name, severity in severities.items():
            issues = result.get_issues_by_severity(severity)
            count = len(issues)

            # Agregar label de severity
            sev_labels = labels.replace('}', f',severity="{sev_name}"}}')
            self.metrics.append(
                f'codepulse_issues_by_severity{{{sev_labels}}} {count} {self.timestamp}'
            )

    def _export_category_metrics(self, result: AnalysisResult, labels: str):
        """Exporta métricas por category."""
        categories = {
            'performance': Category.PERFORMANCE,
            'memory': Category.MEMORY,
            'security': Category.SECURITY,
            'database': Category.DATABASE,
            'concurrency': Category.CONCURRENCY,
            'code_smell': Category.CODE_SMELL,
            'best_practice': Category.BEST_PRACTICE,
            'modernization': Category.MODERNIZATION,
            'bundle_size': Category.BUNDLE_SIZE,
            'event_loop': Category.EVENT_LOOP,
            'api_design': Category.API_DESIGN
        }

        for cat_name, category in categories.items():
            issues = result.get_issues_by_category(category)
            count = len(issues)

            if count > 0:  # Solo exportar si hay issues
                cat_labels = labels.replace('}', f',category="{cat_name}"}}')
                self.metrics.append(
                    f'codepulse_issues_by_category{{{cat_labels}}} {count} {self.timestamp}'
                )

    def _export_trend_metrics(self, result: AnalysisResult, labels: str):
        """Exporta métricas de tendencia."""
        # Porcentaje de issues críticos
        if len(result.issues) > 0:
            critical = result.get_issues_by_severity(Severity.CRITICAL)
            critical_pct = (len(critical) / len(result.issues)) * 100
            self.metrics.append(
                f'codepulse_critical_percentage{{{labels}}} {critical_pct:.2f} {self.timestamp}'
            )

        # Score de calidad (100 - (issues críticos * 10) - (issues high * 5))
        critical_count = len(result.get_issues_by_severity(Severity.CRITICAL))
        high_count = len(result.get_issues_by_severity(Severity.HIGH))
        quality_score = max(0, 100 - (critical_count * 10) - (high_count * 5))

        self.metrics.append(
            f'codepulse_quality_score{{{labels}}} {quality_score} {self.timestamp}'
        )

    def export_to_file(self, result: AnalysisResult, analyzer_name: str,
                      output_path: Path, **kwargs) -> None:
        """
        Exporta métricas a archivo.

        Args:
            result: Resultado del análisis
            analyzer_name: Nombre del analyzer
            output_path: Path del archivo de salida
            **kwargs: Argumentos adicionales para export_result
        """
        metrics = self.export_result(result, analyzer_name, **kwargs)
        output_path.write_text(metrics)

    def export_multiple_results(self, results: Dict[str, AnalysisResult],
                               project_name: str = "default",
                               branch: str = "main",
                               commit_sha: str = "unknown") -> str:
        """
        Exporta múltiples resultados de diferentes analyzers.

        Args:
            results: Dict de analyzer_name -> AnalysisResult
            project_name: Nombre del proyecto
            branch: Branch de git
            commit_sha: SHA del commit

        Returns:
            String con todas las métricas
        """
        all_metrics = []

        for analyzer_name, result in results.items():
            metrics = self.export_result(
                result, analyzer_name, project_name, branch, commit_sha
            )
            all_metrics.append(metrics)

        return "\n".join(all_metrics)


class PrometheusMetricsServer:
    """Servidor HTTP simple para exponer métricas a Prometheus."""

    def __init__(self, port: int = 9090):
        self.port = port
        self.metrics_cache = ""

    def update_metrics(self, metrics: str):
        """Actualiza las métricas en cache."""
        self.metrics_cache = metrics

    def start(self):
        """Inicia el servidor HTTP."""
        from http.server import HTTPServer, BaseHTTPRequestHandler

        exporter = self

        class MetricsHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/metrics':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain; version=0.0.4')
                    self.end_headers()
                    self.wfile.write(exporter.metrics_cache.encode())
                elif self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'OK')
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                # Silenciar logs de access
                pass

        server = HTTPServer(('', self.port), MetricsHandler)
        print(f"Prometheus metrics server started on port {self.port}")
        print(f"Metrics available at http://localhost:{self.port}/metrics")
        server.serve_forever()


def main():
    """Example usage."""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python prometheus_exporter.py <analyzer> <directory> [output_file]")
        print("\nExample:")
        print("  python prometheus_exporter.py jvm ./src metrics.txt")
        sys.exit(1)

    analyzer_name = sys.argv[1]
    directory = Path(sys.argv[2])
    output_file = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    # Importar analyzer dinámicamente
    if analyzer_name == 'jvm':
        from analyzers.java.jvm_performance_analyzer import JVMPerformanceAnalyzer
        analyzer = JVMPerformanceAnalyzer()
    elif analyzer_name == 'spring-data':
        from analyzers.java.spring_data_analyzer import SpringDataAnalyzer
        analyzer = SpringDataAnalyzer()
    elif analyzer_name == 'spring-security':
        from analyzers.java.spring_security_analyzer import SpringSecurityAnalyzer
        analyzer = SpringSecurityAnalyzer()
    elif analyzer_name == 'spring-rest':
        from analyzers.java.spring_rest_analyzer import SpringRestAnalyzer
        analyzer = SpringRestAnalyzer()
    else:
        print(f"Unknown analyzer: {analyzer_name}")
        sys.exit(1)

    # Analizar
    result = analyzer.analyze_directory(directory)

    # Exportar métricas
    exporter = PrometheusExporter()

    # Obtener info de git si está disponible
    import subprocess
    try:
        branch = subprocess.check_output(['git', 'branch', '--show-current'],
                                        stderr=subprocess.DEVNULL).decode().strip()
        commit_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                            stderr=subprocess.DEVNULL).decode().strip()
    except:
        branch = "main"
        commit_sha = "unknown"

    metrics = exporter.export_result(
        result,
        analyzer_name=analyzer_name,
        project_name=directory.name,
        branch=branch,
        commit_sha=commit_sha
    )

    if output_file:
        output_file.write_text(metrics)
        print(f"✅ Metrics exported to {output_file}")
    else:
        print(metrics)


if __name__ == '__main__':
    main()
