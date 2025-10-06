# CodePulse Makefile
# Sistema de análisis de código y monitoreo

.PHONY: help install test analyze monitor

# Default target
help:
	@echo "CodePulse - Sistema de Análisis y Monitoreo"
	@echo ""
	@echo "Análisis:"
	@echo "  make analyze              - Ejecutar análisis JVM Performance"
	@echo "  make analyze-all          - Ejecutar todos los analyzers"
	@echo "  make test                 - Ejecutar tests"
	@echo ""
	@echo "Reportes HTML:"
	@echo "  make report-html          - Generar reporte HTML del análisis"
	@echo "  make report-html-sample   - Generar reporte de ejemplo con datos"
	@echo ""
	@echo "Monitoreo:"
	@echo "  make monitor-demo         - Demo del sistema de monitoreo"
	@echo "  make monitor-setup        - Setup completo en Kubernetes"
	@echo "  make monitor-export       - Exportar métricas Prometheus"
	@echo "  make monitor-push         - Push métricas a Pushgateway"
	@echo ""
	@echo "Dashboards:"
	@echo "  make dashboard-import     - Instrucciones para importar dashboards"
	@echo "  make dashboard-validate   - Validar JSONs de dashboards"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build         - Build imagen del analyzer"
	@echo "  make docker-push          - Push imagen al registry"
	@echo ""
	@echo "Kubernetes:"
	@echo "  make k8s-deploy           - Deploy en Kubernetes"
	@echo "  make k8s-status           - Ver estado del deployment"
	@echo "  make k8s-logs             - Ver logs del analyzer"
	@echo "  make k8s-trigger          - Trigger manual del job"
	@echo ""
	@echo "Utilidades:"
	@echo "  make clean                - Limpiar archivos generados"
	@echo "  make install              - Instalar dependencias"

# Instalación
install:
	pip install -e .
	@echo "✅ CodePulse instalado"

# Tests
test:
	python -m pytest src/tests/ -v
	@echo "✅ Tests completados"

# Análisis
analyze:
	python3 -m analyzers.java.jvm_performance_analyzer ./src
	@echo "✅ Análisis JVM Performance completado"

analyze-all:
	@echo "🔍 Ejecutando todos los analyzers..."
	python3 -m analyzers.java.jvm_performance_analyzer ./src
	@echo "✅ Análisis completado"

# Reportes HTML
report-html:
	@echo "📄 Generando reporte HTML..."
	python3 examples/html_report_demo.py
	@echo "✅ Reporte HTML generado"

report-html-sample:
	@echo "📄 Generando reporte HTML con datos de ejemplo..."
	python3 examples/html_report_sample.py
	@echo "✅ Reporte de ejemplo generado"

# Monitoreo - Demo
monitor-demo:
	@echo "📊 Ejecutando demo de monitoreo..."
	python3 examples/monitoring_demo.py
	@echo "✅ Demo completado - Ver métricas en metrics_output/"

# Monitoreo - Export métricas
monitor-export:
	@echo "📈 Exportando métricas a Prometheus..."
	@mkdir -p metrics_output
	python3 << 'EOF'
	import sys
	from pathlib import Path
	sys.path.insert(0, 'src')
	from analyzers.java.jvm_performance_analyzer import JVMPerformanceAnalyzer
	from exporters.prometheus_exporter import PrometheusExporter
	analyzer = JVMPerformanceAnalyzer()
	result = analyzer.analyze_directory(Path('./src'))
	exporter = PrometheusExporter()
	exporter.export_to_file(result, 'jvm-performance', Path('metrics_output/metrics.txt'),
	                        project_name='CodePulse', branch='main', commit_sha='local')
	print("✅ Métricas exportadas a metrics_output/metrics.txt")
	EOF

# Monitoreo - Push a Pushgateway
monitor-push: monitor-export
	@if [ -z "$(PUSHGATEWAY_URL)" ]; then \
		echo "❌ Error: Define PUSHGATEWAY_URL"; \
		echo "   Ejemplo: make monitor-push PUSHGATEWAY_URL=http://localhost:9091"; \
		exit 1; \
	fi
	@echo "📤 Pushing métricas a $(PUSHGATEWAY_URL)..."
	curl -X POST \
		-H 'Content-Type: text/plain' \
		--data-binary @metrics_output/metrics.txt \
		"$(PUSHGATEWAY_URL)/metrics/job/codepulse/instance/local"
	@echo "✅ Métricas pushed exitosamente"

# Monitoreo - Setup Kubernetes
monitor-setup:
	@echo "☸️  Iniciando setup de monitoreo en Kubernetes..."
	./scripts/setup_monitoring.sh

# Dashboards
dashboard-import:
	@echo "📊 Dashboards de Grafana:"
	@echo ""
	@echo "1. Overview Dashboard:"
	@echo "   Archivo: grafana/codepulse-overview-dashboard.json"
	@echo "   Paneles: 11 (Quality Score, Issues by Severity, etc.)"
	@echo ""
	@echo "2. Comparison Dashboard:"
	@echo "   Archivo: grafana/codepulse-comparison-dashboard.json"
	@echo "   Paneles: 10 (Before/After, Improvements, etc.)"
	@echo ""
	@echo "Importar en Grafana:"
	@echo "  - UI: Dashboards → Import → Copiar JSON"
	@echo "  - API: curl -X POST http://grafana/api/dashboards/db \\"
	@echo "           -H 'Content-Type: application/json' \\"
	@echo "           -d @grafana/codepulse-overview-dashboard.json"

dashboard-validate:
	@echo "🔍 Validando dashboards JSON..."
	python3 -m json.tool grafana/codepulse-overview-dashboard.json > /dev/null && echo "✅ codepulse-overview-dashboard.json"
	python3 -m json.tool grafana/codepulse-comparison-dashboard.json > /dev/null && echo "✅ codepulse-comparison-dashboard.json"
	@echo "✅ Todos los dashboards son válidos"

# Docker
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -f Dockerfile.analyzer -t codepulse/analyzer:latest .
	@echo "✅ Imagen built: codepulse/analyzer:latest"

docker-push: docker-build
	@if [ -z "$(REGISTRY)" ]; then \
		echo "❌ Error: Define REGISTRY"; \
		echo "   Ejemplo: make docker-push REGISTRY=docker.io/usuario"; \
		exit 1; \
	fi
	docker tag codepulse/analyzer:latest $(REGISTRY)/codepulse-analyzer:latest
	docker push $(REGISTRY)/codepulse-analyzer:latest
	@echo "✅ Imagen pushed: $(REGISTRY)/codepulse-analyzer:latest"

# Kubernetes
k8s-deploy:
	@echo "☸️  Desplegando en Kubernetes..."
	kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -f k8s/codepulse-rbac.yaml
	kubectl apply -f k8s/codepulse-configmap.yaml
	kubectl apply -f k8s/codepulse-cronjob.yaml
	kubectl apply -f k8s/prometheus-servicemonitor.yaml
	@echo "✅ Deployment completo"

k8s-status:
	@echo "📊 Estado del deployment:"
	@echo ""
	kubectl get cronjobs -n monitoring
	@echo ""
	kubectl get jobs -n monitoring
	@echo ""
	kubectl get pods -n monitoring -l app=codepulse

k8s-logs:
	@echo "📋 Logs del analyzer:"
	kubectl logs -n monitoring -l app=codepulse --tail=100 -f

k8s-trigger:
	@echo "🚀 Triggering manual job..."
	kubectl create job -n monitoring codepulse-manual-$(shell date +%s) --from=cronjob/codepulse-analyzer
	@echo "✅ Job manual creado - Ver con: make k8s-status"

# Clean
clean:
	@echo "🧹 Limpiando archivos generados..."
	rm -rf metrics_output/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Limpieza completada"

# Quick start
quickstart:
	@echo "🚀 CodePulse Quick Start"
	@echo ""
	@echo "1. Instalando dependencias..."
	@make install
	@echo ""
	@echo "2. Ejecutando tests..."
	@make test
	@echo ""
	@echo "3. Ejecutando análisis..."
	@make analyze
	@echo ""
	@echo "4. Demo de monitoreo..."
	@make monitor-demo
	@echo ""
	@echo "✅ Quick start completado!"
	@echo ""
	@echo "Próximos pasos:"
	@echo "  - Configurar Kubernetes: make monitor-setup"
	@echo "  - Importar dashboards: make dashboard-import"
	@echo "  - Ver documentación: docs/MONITORING_SETUP.md"
