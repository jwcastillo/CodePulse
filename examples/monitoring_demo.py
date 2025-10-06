#!/usr/bin/env python3
"""
Demo completo del sistema de monitoreo de CodePulse
Muestra el flujo end-to-end: Análisis -> Exportación -> Métricas Prometheus
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from analyzers.java.jvm_performance_analyzer import JVMPerformanceAnalyzer
from exporters.prometheus_exporter import PrometheusExporter
from core.models import Severity

def main():
    print("=" * 80)
    print("CodePulse Monitoring Demo - Sistema Completo de Monitoreo")
    print("=" * 80)
    print()

    # Paso 1: Análisis de código
    print("📊 PASO 1: Analizando código con JVM Performance Analyzer...")
    print("-" * 80)

    analyzer = JVMPerformanceAnalyzer()
    test_dir = Path(__file__).parent.parent / 'src'

    if not test_dir.exists():
        print(f"❌ Directorio no encontrado: {test_dir}")
        return 1

    result = analyzer.analyze_directory(test_dir)

    # Mostrar resultados del análisis
    critical = result.get_issues_by_severity(Severity.CRITICAL)
    high = result.get_issues_by_severity(Severity.HIGH)
    medium = result.get_issues_by_severity(Severity.MEDIUM)
    low = result.get_issues_by_severity(Severity.LOW)

    print(f"✅ Análisis completado:")
    print(f"   - Total issues: {len(result.issues)}")
    print(f"   - CRITICAL: {len(critical)}")
    print(f"   - HIGH: {len(high)}")
    print(f"   - MEDIUM: {len(medium)}")
    print(f"   - LOW: {len(low)}")
    print()

    # Paso 2: Exportar métricas a Prometheus
    print("📈 PASO 2: Exportando métricas a formato Prometheus...")
    print("-" * 80)

    exporter = PrometheusExporter()

    # Simular múltiples analyzers
    analyzers = ['jvm-performance', 'spring-data', 'spring-security', 'spring-rest']
    all_metrics = []

    for analyzer_name in analyzers:
        metrics = exporter.export_result(
            result,
            analyzer_name=analyzer_name,
            project_name='CodePulse',
            branch='main',
            commit_sha='demo123'
        )
        all_metrics.append(metrics)

    print("✅ Métricas exportadas para 4 analyzers")
    print()

    # Paso 3: Guardar métricas en archivos
    print("💾 PASO 3: Guardando métricas en archivos...")
    print("-" * 80)

    output_dir = Path(__file__).parent.parent / 'metrics_output'
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for i, (analyzer_name, metrics) in enumerate(zip(analyzers, all_metrics)):
        output_file = output_dir / f'metrics_{analyzer_name}_{timestamp}.txt'
        exporter.export_to_file(
            result,
            analyzer_name,
            output_file,
            project_name='CodePulse',
            branch='main',
            commit_sha='demo123'
        )
        print(f"   ✓ {output_file}")

    # Archivo combinado
    combined_file = output_dir / f'metrics_combined_{timestamp}.txt'
    with open(combined_file, 'w') as f:
        f.write('\n'.join(all_metrics))
    print(f"   ✓ {combined_file}")
    print()

    # Paso 4: Mostrar ejemplo de métricas
    print("📊 PASO 4: Ejemplo de métricas Prometheus:")
    print("-" * 80)
    print(all_metrics[0][:800] + "...")
    print()

    # Paso 5: Información de visualización
    print("📈 PASO 5: Visualización en Grafana")
    print("-" * 80)
    print("Para visualizar estas métricas en Grafana:")
    print()
    print("1. Prometheus Pushgateway:")
    print("   curl -X POST \\")
    print("     -H 'Content-Type: text/plain' \\")
    print(f"     --data-binary @{combined_file} \\")
    print("     'http://pushgateway:9091/metrics/job/codepulse/instance/demo'")
    print()
    print("2. Dashboards disponibles:")
    print("   - grafana/codepulse-overview-dashboard.json (11 paneles)")
    print("   - grafana/codepulse-comparison-dashboard.json (10 paneles)")
    print()
    print("3. Importar en Grafana:")
    print("   - UI: Dashboards → Import → Copiar JSON")
    print("   - API: curl -X POST http://grafana/api/dashboards/db \\")
    print("           -H 'Content-Type: application/json' \\")
    print("           -d @grafana/codepulse-overview-dashboard.json")
    print()

    # Paso 6: Kubernetes deployment
    print("☸️  PASO 6: Deployment en Kubernetes")
    print("-" * 80)
    print("Desplegar el sistema completo:")
    print()
    print("kubectl create namespace monitoring")
    print("kubectl apply -f k8s/codepulse-rbac.yaml")
    print("kubectl apply -f k8s/codepulse-configmap.yaml")
    print("kubectl apply -f k8s/codepulse-cronjob.yaml")
    print("kubectl apply -f k8s/prometheus-servicemonitor.yaml")
    print()
    print("Verificar:")
    print("kubectl get cronjobs -n monitoring")
    print("kubectl get pods -n monitoring -l app=codepulse")
    print()

    # Paso 7: CI/CD
    print("🔄 PASO 7: CI/CD Integration")
    print("-" * 80)
    print("GitHub Actions configurado en: .github/workflows/codepulse-metrics.yml")
    print()
    print("Triggers:")
    print("  - Push a main/develop")
    print("  - Pull Requests")
    print("  - Schedule diario (midnight)")
    print()
    print("Matrix strategy ejecuta 4 analyzers en paralelo")
    print("Falla el build si hay issues CRITICAL")
    print()

    # Resumen
    print("=" * 80)
    print("✅ DEMO COMPLETO - Sistema de Monitoreo Funcionando")
    print("=" * 80)
    print()
    print("📊 Métricas guardadas en: metrics_output/")
    print("📈 Dashboards: grafana/")
    print("☸️  Kubernetes: k8s/")
    print("🔄 CI/CD: .github/workflows/codepulse-metrics.yml")
    print("📚 Docs: docs/MONITORING_SETUP.md")
    print()
    print("Próximos pasos:")
    print("1. Configurar PROMETHEUS_PUSHGATEWAY_URL en GitHub Secrets")
    print("2. Importar dashboards en Grafana")
    print("3. Deploy CronJob en Kubernetes")
    print("4. Monitorear mejoras en tiempo real!")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
