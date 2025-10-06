#!/usr/bin/env python3
"""
Demo del HTML Reporter con JVM Performance Analyzer
Genera un reporte HTML completo y lo abre en el navegador
"""

import sys
import os
import webbrowser
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from analyzers.java.jvm_performance_analyzer import JVMPerformanceAnalyzer
from reporters.html_reporter import HTMLReporter
from core.models import Severity


def main():
    print("=" * 80)
    print("CodePulse HTML Report Demo")
    print("=" * 80)
    print()

    # Paso 1: Analizar código
    print("📊 Paso 1: Analizando código...")
    print("-" * 80)

    analyzer = JVMPerformanceAnalyzer()

    # Directorio a analizar
    target_dir = Path(__file__).parent.parent / 'src'

    if not target_dir.exists():
        print(f"❌ Directorio no encontrado: {target_dir}")
        # Crear ejemplo de prueba
        target_dir = Path(__file__).parent

    print(f"   Analizando: {target_dir}")
    result = analyzer.analyze_directory(target_dir)

    # Agregar metadata
    result.metadata['analyzer'] = 'JVM Performance Analyzer'
    result.metadata['directory'] = str(target_dir)

    # Stats
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
    print(f"   - Files analyzed: {result.files_analyzed}")
    print(f"   - Total lines: {result.total_lines:,}")
    print()

    # Paso 2: Generar reporte HTML
    print("📄 Paso 2: Generando reporte HTML...")
    print("-" * 80)

    reporter = HTMLReporter()

    # Output file con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(__file__).parent.parent / 'reports'
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f'codepulse_report_{timestamp}.html'

    reporter.report(result, output_file)

    print(f"✅ Reporte generado:")
    print(f"   - Archivo: {output_file}")
    print(f"   - Tamaño: {output_file.stat().st_size:,} bytes")
    print()

    # Paso 3: Abrir en navegador
    print("🌐 Paso 3: Abriendo reporte en navegador...")
    print("-" * 80)

    # Abrir en navegador
    file_url = output_file.absolute().as_uri()

    try:
        webbrowser.open(file_url)
        print(f"✅ Reporte abierto en navegador")
        print(f"   URL: {file_url}")
    except Exception as e:
        print(f"⚠️  No se pudo abrir automáticamente: {e}")
        print(f"   Abrir manualmente: {output_file}")

    print()

    # Resumen
    print("=" * 80)
    print("✅ Demo completado")
    print("=" * 80)
    print()
    print("El reporte HTML incluye:")
    print("  ✓ Header con metadata del análisis")
    print("  ✓ Summary cards por severidad")
    print("  ✓ Issues detallados con:")
    print("    - Descripción y severidad")
    print("    - Categoría y ubicación")
    print("    - Impacto potencial")
    print("    - Solución recomendada")
    print("    - Code snippet con syntax")
    print("  ✓ Estilos modernos y responsive")
    print("  ✓ Footer con info del proyecto")
    print()
    print(f"Reporte guardado en: {output_file}")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
