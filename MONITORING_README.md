# 📊 CodePulse Monitoring System

Sistema completo de monitoreo y visualización para CodePulse que permite trackear mejoras de calidad de código en tiempo real usando Grafana, Prometheus y Kubernetes.

## 🚀 Quick Start

### 1. Demo Local (5 minutos)

```bash
# Ejecutar demo completo
make monitor-demo

# Exportar métricas
make monitor-export

# Ver métricas generadas
cat metrics_output/metrics.txt
```

### 2. Setup en Kubernetes (Interactivo)

```bash
# Script interactivo que configura todo
make monitor-setup

# O manualmente:
./scripts/setup_monitoring.sh
```

### 3. Importar Dashboards en Grafana

```bash
# Ver instrucciones
make dashboard-import

# Validar JSONs
make dashboard-validate
```

## 📈 Componentes del Sistema

### 1. Prometheus Exporter
**Archivo**: `src/exporters/prometheus_exporter.py`

Exporta 8 métricas clave:

| Métrica | Descripción | Labels |
|---------|-------------|--------|
| `codepulse_total_issues` | Total de issues | project, branch, analyzer, commit |
| `codepulse_files_analyzed` | Archivos analizados | project, branch, analyzer, commit |
| `codepulse_total_lines` | Líneas de código | project, branch, analyzer, commit |
| `codepulse_issue_density` | Issues por 1000 líneas | project, branch, analyzer, commit |
| `codepulse_issues_by_severity` | Issues por severidad | project, branch, analyzer, commit, severity |
| `codepulse_issues_by_category` | Issues por categoría | project, branch, analyzer, commit, category |
| `codepulse_critical_percentage` | % de issues críticos | project, branch, analyzer, commit |
| `codepulse_quality_score` | Score de calidad (0-100) | project, branch, analyzer, commit |

### 2. Kubernetes Deployment

**CronJob**: Ejecuta análisis automáticamente cada hora
```bash
# Deploy
make k8s-deploy

# Ver estado
make k8s-status

# Ver logs
make k8s-logs

# Trigger manual
make k8s-trigger
```

**Archivos**:
- `k8s/codepulse-cronjob.yaml` - CronJob definition
- `k8s/codepulse-configmap.yaml` - Configuration
- `k8s/codepulse-rbac.yaml` - Permissions
- `k8s/prometheus-servicemonitor.yaml` - Scraping config

### 3. Grafana Dashboards

#### Dashboard 1: Code Quality Overview
**11 paneles** mostrando estado actual:
- Quality Score Trend
- Total Issues by Severity (stacked)
- Current Critical/High Issues
- Issue Density
- Total Lines of Code
- Issues by Category (pie chart)
- Issues by Analyzer (bar gauge)
- Performance Issues Trend
- Security Issues Trend
- Critical Issues Table

#### Dashboard 2: Before/After Comparison
**10 paneles** mostrando mejoras:
- Quality Score: Before vs After
- Critical Issues Reduction (% change)
- Total Issues Reduction (% change)
- Issues Reduction Over Time
- Improvement by Category
- Improvement by Analyzer
- Performance/Security Detailed Trends
- Weekly Improvement Summary
- Commit Impact on Quality

### 4. CI/CD Integration

**GitHub Actions**: `.github/workflows/codepulse-metrics.yml`

Ejecuta en:
- Push a main/develop
- Pull Requests
- Schedule diario (midnight)

**Matrix strategy**: 4 analyzers en paralelo
- jvm-performance
- spring-data
- spring-security
- spring-rest

**Features**:
- ✅ Análisis automático en cada push
- ✅ Exporta métricas a Prometheus Pushgateway
- ✅ Comenta en PRs con resultados
- ✅ Falla build si hay issues CRITICAL
- ✅ Guarda artifacts (30 días retention)

### 5. Docker

```bash
# Build imagen
make docker-build

# Push a registry
make docker-push REGISTRY=docker.io/usuario
```

**Dockerfile.analyzer**: Python 3.10-slim con CodePulse instalado

## 🎯 Workflow Completo

```
1. Developer hace commit
   ↓
2. GitHub Actions ejecuta
   ├─> Analiza con 4 analyzers en paralelo
   ├─> Exporta métricas
   ├─> Push a Prometheus Pushgateway
   └─> Comenta en PR si aplica
   ↓
3. Prometheus scrape de Pushgateway cada 30s
   ↓
4. Grafana visualiza en dashboards
   ├─> Overview: Estado actual
   └─> Comparison: Mejoras en el tiempo
   ↓
5. Si issues CRITICAL:
   ├─> Alerta en Prometheus
   ├─> Notificación (Slack/Email)
   └─> Build falla
```

## 📋 Comandos Make Disponibles

### Monitoreo
```bash
make monitor-demo         # Demo del sistema completo
make monitor-setup        # Setup en Kubernetes (interactivo)
make monitor-export       # Exportar métricas localmente
make monitor-push         # Push a Pushgateway
```

### Dashboards
```bash
make dashboard-import     # Instrucciones de importación
make dashboard-validate   # Validar JSONs
```

### Kubernetes
```bash
make k8s-deploy          # Deploy completo
make k8s-status          # Ver estado
make k8s-logs            # Ver logs (follow)
make k8s-trigger         # Trigger manual
```

### Docker
```bash
make docker-build        # Build imagen
make docker-push         # Push al registry
```

## 📊 Ejemplo de Uso: Mejora de Código

### Día 0 - Baseline
Dashboard Overview muestra:
- Quality Score: **65/100**
- Total Issues: **45**
- Critical: **5** 🔴
- High: **15** 🟠
- Density: **8.5** issues/1000 lines

### Semana 1 - Sprint de Mejora
Cada commit:
1. GitHub Actions analiza automáticamente
2. Exporta métricas nuevas
3. Dashboard actualiza en tiempo real
4. Si commit introduce CRITICAL → build falla ❌

Dashboard Comparison muestra:
- Issues resueltos por día
- Tendencia de quality score ↗️
- Reducción de cada category

### Día 7 - Revisión
Dashboard Comparison muestra:
- Quality Score: **65 → 95** (+46%) ✅
- Total Issues: **45 → 12** (-73%) ✅
- Critical: **5 → 0** (-100%) ✅
- High: **15 → 3** (-80%) ✅
- Density: **8.5 → 2.3** (-73%) ✅

**Métricas exportadas**:
- 33 issues resueltos
- 0 nuevos críticos introducidos
- Mejora sostenida durante 7 días

## 🔍 Queries de Prometheus Útiles

```promql
# Total issues críticos actuales
sum(codepulse_issues_by_severity{severity="critical"})

# Quality score promedio
avg(codepulse_quality_score{project="my-project"})

# Tendencia de reducción (última semana)
sum(changes(codepulse_total_issues{project="my-project"}[7d]))

# Issues por category
sum(codepulse_issues_by_category{project="my-project"}) by (category)

# Densidad por analyzer
avg(codepulse_issue_density{project="my-project"}) by (analyzer)

# Quality score increase (últimas 24h)
delta(codepulse_quality_score{project="my-project"}[24h])
```

## 🚨 Alertas Configurables

```yaml
# prometheus-alerts.yaml
- alert: CriticalCodeIssues
  expr: sum(codepulse_issues_by_severity{severity="critical"}) > 0
  for: 5m
  annotations:
    summary: "{{ $value }} critical issues detected"

- alert: QualityScoreDrop
  expr: delta(codepulse_quality_score[1h]) < -10
  for: 5m
  annotations:
    summary: "Quality score dropped {{ $value }} points"

- alert: HighIssueDensity
  expr: avg(codepulse_issue_density) > 10
  for: 10m
  annotations:
    summary: "Issue density: {{ $value }} per 1000 lines"
```

## 🐛 Troubleshooting

### Métricas no aparecen en Grafana

```bash
# 1. Verificar CronJob
kubectl get cronjobs -n monitoring
kubectl get pods -n monitoring -l app=codepulse

# 2. Ver logs
kubectl logs -n monitoring -l app=codepulse --tail=100

# 3. Verificar Pushgateway
kubectl port-forward -n monitoring svc/prometheus-pushgateway 9091:9091
curl http://localhost:9091/metrics | grep codepulse

# 4. Verificar Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Abrir http://localhost:9090 y query: codepulse_total_issues
```

### CI/CD no exporta métricas

```bash
# Ver logs de workflow
gh run list
gh run view <run-id>

# Verificar secret
gh secret list

# Test manual de push
make monitor-push PUSHGATEWAY_URL=http://pushgateway:9091
```

### Dashboard no muestra datos

1. Verificar datasource Prometheus configurado
2. Verificar variables: $project, $branch
3. Verificar time range (últimos 7-30 días)
4. Query directa en Prometheus para verificar datos

## 📚 Documentación

- **Setup Completo**: [`docs/MONITORING_SETUP.md`](docs/MONITORING_SETUP.md)
- **Implementación Completa**: [`GRAFANA_MONITORING_COMPLETE.md`](GRAFANA_MONITORING_COMPLETE.md)
- **Guía JVM Performance**: [`docs/guides/jvm_performance_guide.md`](docs/guides/jvm_performance_guide.md)

## 🎯 Beneficios

### Para Developers
- 👀 Visualización en tiempo real de calidad
- 📈 Motivación viendo mejoras cuantificadas
- 🎯 Focus en issues más críticos
- 📊 Data-driven decisions

### Para Tech Leads
- 📉 Tracking de technical debt
- 🎯 Priorización basada en métricas
- 📈 ROI visible de mejoras
- 📊 Reportes para stakeholders

### Para DevOps
- 🚨 Alertas automáticas
- 🔄 Integración con pipelines
- 📊 Monitoring continuo
- ✅ Quality gates automáticos

## 🏁 Resumen

✅ **Prometheus Exporter** - 8 métricas con labels
✅ **Kubernetes CronJob** - Análisis automático cada hora
✅ **2 Dashboards Grafana** - 21 paneles total
✅ **GitHub Actions** - CI/CD con matrix strategy
✅ **Docker Image** - Ready para production
✅ **Documentación completa** - Setup paso a paso

**CodePulse tiene monitoreo completo de calidad de código!** 🎉📊
