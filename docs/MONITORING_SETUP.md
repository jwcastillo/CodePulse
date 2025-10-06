# CodePulse Monitoring con Grafana y Prometheus

## Resumen

Esta guía explica cómo configurar un sistema completo de monitoreo para CodePulse que permite:

- ✅ **Visualizar métricas** de calidad de código en Grafana
- ✅ **Comparar antes/después** de cambios y mejoras
- ✅ **Tendencias temporales** de issues por severity y category
- ✅ **Alertas automáticas** cuando aparecen issues críticos
- ✅ **CI/CD integration** para exportar métricas automáticamente
- ✅ **Deployment en Kubernetes** con CronJobs

## Arquitectura

```
┌─────────────────┐
│   Git Repo      │
└────────┬────────┘
         │
         ├──> GitHub Actions (CI/CD)
         │    └─> Analiza código
         │        └─> Exporta métricas
         │            └─> Prometheus Pushgateway
         │
         └──> Kubernetes CronJob
              └─> Analiza código cada hora
                  └─> Exporta métricas
                      └─> Prometheus Pushgateway
                           │
                           ▼
                    ┌──────────────┐
                    │  Prometheus  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Grafana    │
                    └──────────────┘
```

## Componentes

### 1. Prometheus Exporter

**Archivo**: `src/exporters/prometheus_exporter.py`

Exporta métricas en formato Prometheus:

```python
from exporters.prometheus_exporter import PrometheusExporter

exporter = PrometheusExporter()
metrics = exporter.export_result(
    result,
    analyzer_name="jvm-performance",
    project_name="my-project",
    branch="main",
    commit_sha="abc123"
)
```

**Métricas exportadas:**

| Métrica | Descripción | Labels |
|---------|-------------|--------|
| `codepulse_total_issues` | Total de issues encontrados | project, branch, analyzer, commit |
| `codepulse_files_analyzed` | Archivos analizados | project, branch, analyzer, commit |
| `codepulse_total_lines` | Líneas de código totales | project, branch, analyzer, commit |
| `codepulse_issue_density` | Issues por 1000 líneas | project, branch, analyzer, commit |
| `codepulse_issues_by_severity` | Issues por severidad | project, branch, analyzer, commit, severity |
| `codepulse_issues_by_category` | Issues por categoría | project, branch, analyzer, commit, category |
| `codepulse_critical_percentage` | % de issues críticos | project, branch, analyzer, commit |
| `codepulse_quality_score` | Score de calidad (0-100) | project, branch, analyzer, commit |

### 2. Kubernetes Deployment

**Archivos en `/k8s/`:**

- `codepulse-cronjob.yaml` - CronJob que ejecuta análisis cada hora
- `codepulse-configmap.yaml` - Configuración del proyecto
- `codepulse-rbac.yaml` - Permisos necesarios
- `prometheus-servicemonitor.yaml` - Configuración de scraping

#### Desplegar en Kubernetes

```bash
# Crear namespace
kubectl create namespace monitoring

# Aplicar manifests
kubectl apply -f k8s/codepulse-rbac.yaml
kubectl apply -f k8s/codepulse-configmap.yaml
kubectl apply -f k8s/codepulse-cronjob.yaml
kubectl apply -f k8s/prometheus-servicemonitor.yaml

# Verificar deployment
kubectl get cronjobs -n monitoring
kubectl get pods -n monitoring
```

#### Configurar tu proyecto

Edita `k8s/codepulse-configmap.yaml`:

```yaml
data:
  project.name: "tu-proyecto"
  git.repo.url: "https://github.com/tu-org/tu-repo.git"
  git.branch: "main"
  analyzers: "jvm-performance,spring-data,spring-security,spring-rest"
```

#### Build y Push de la imagen Docker

```bash
# Build
docker build -f Dockerfile.analyzer -t tu-registry/codepulse-analyzer:latest .

# Push
docker push tu-registry/codepulse-analyzer:latest

# Update CronJob
kubectl set image cronjob/codepulse-analyzer \
  analyzer=tu-registry/codepulse-analyzer:latest \
  -n monitoring
```

### 3. Grafana Dashboards

**Archivos en `/grafana/`:**

#### Dashboard 1: Code Quality Overview

**Archivo**: `grafana/codepulse-overview-dashboard.json`

**Paneles:**
- Quality Score Trend
- Total Issues by Severity (stacked graph)
- Current Critical/High Issues (stats)
- Issue Density
- Total Lines of Code
- Issues by Category (pie chart)
- Issues by Analyzer (bar gauge)
- Performance Issues Trend
- Security Issues Trend
- Critical Issues Table

**Variables:**
- `$project` - Seleccionar proyecto
- `$branch` - Seleccionar branch
- `$analyzer` - Filtrar por analyzer(s)

#### Dashboard 2: Before/After Comparison

**Archivo**: `grafana/codepulse-comparison-dashboard.json`

**Paneles:**
- Quality Score: Before vs After
- Critical Issues Reduction
- Total Issues Reduction
- Issues Reduction Over Time
- Improvement by Category
- Improvement by Analyzer
- Performance/Security Detailed Trends
- Weekly Improvement Summary
- Commit Impact on Quality

#### Importar Dashboards en Grafana

**Opción 1: UI**
1. Ir a Grafana → Dashboards → Import
2. Copiar contenido de JSON
3. Seleccionar Prometheus como datasource
4. Click "Import"

**Opción 2: API**
```bash
curl -X POST \
  http://admin:admin@grafana.example.com/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @grafana/codepulse-overview-dashboard.json
```

**Opción 3: ConfigMap en Kubernetes**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  codepulse-overview.json: |
    # contenido del JSON aquí
```

### 4. CI/CD Integration

**Archivo**: `.github/workflows/codepulse-metrics.yml`

**Triggers:**
- Push a main/develop
- Pull Requests
- Schedule diario (midnight)

**Matrix strategy** - ejecuta en paralelo:
- jvm-performance
- spring-data
- spring-security
- spring-rest

**Features:**
- ✅ Analiza código en cada push
- ✅ Exporta métricas a Prometheus Pushgateway
- ✅ Comenta en PRs con resultados
- ✅ Falla el build si hay issues CRITICAL
- ✅ Guarda métricas como artifacts (30 días)
- ✅ Combina métricas de todos los analyzers

#### Configurar Secrets

En GitHub Settings → Secrets:

```
PROMETHEUS_PUSHGATEWAY_URL=http://pushgateway.example.com:9091
```

## Setup Completo Paso a Paso

### Pre-requisitos

- Kubernetes cluster
- Prometheus con Pushgateway
- Grafana
- Git repository

### Paso 1: Instalar Prometheus Stack

```bash
# Usando Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

### Paso 2: Instalar Prometheus Pushgateway

```bash
helm install pushgateway prometheus-community/prometheus-pushgateway \
  --namespace monitoring \
  --set serviceMonitor.enabled=true
```

### Paso 3: Deploy CodePulse en Kubernetes

```bash
# Build imagen
docker build -f Dockerfile.analyzer -t codepulse/analyzer:latest .

# Configurar
kubectl apply -f k8s/codepulse-configmap.yaml

# Deploy
kubectl apply -f k8s/codepulse-rbac.yaml
kubectl apply -f k8s/codepulse-cronjob.yaml
kubectl apply -f k8s/prometheus-servicemonitor.yaml

# Verificar
kubectl get cronjobs -n monitoring
kubectl logs -n monitoring -l app=codepulse
```

### Paso 4: Importar Dashboards en Grafana

```bash
# Port-forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Abrir http://localhost:3000
# Usuario: admin
# Password: (obtener con)
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Importar dashboards desde UI o API
```

### Paso 5: Configurar CI/CD

```bash
# En tu repo, crear workflow
mkdir -p .github/workflows
cp .github/workflows/codepulse-metrics.yml .github/workflows/

# Configurar secret
gh secret set PROMETHEUS_PUSHGATEWAY_URL --body "http://pushgateway.example.com:9091"

# Commit y push
git add .github/workflows/codepulse-metrics.yml
git commit -m "Add CodePulse metrics workflow"
git push
```

## Uso

### Ver Métricas en Tiempo Real

1. **Grafana**: http://grafana.example.com
2. **Dashboard**: "CodePulse - Code Quality Overview"
3. **Seleccionar**:
   - Project: tu-proyecto
   - Branch: main
   - Analyzer: (todos o específico)

### Comparar Antes/Después

1. **Dashboard**: "CodePulse - Before/After Comparison"
2. **Time range**: Últimos 30 días
3. **Ver**:
   - Quality Score improvement
   - Critical issues reduction
   - Category improvements

### Queries de Prometheus Útiles

```promql
# Issues críticos actuales
sum(codepulse_issues_by_severity{severity="critical"})

# Tendencia de quality score
codepulse_quality_score{project="my-project", branch="main"}

# Issues por category
sum(codepulse_issues_by_category) by (category)

# Reducción de issues en última semana
sum(changes(codepulse_total_issues[7d]))

# Densidad promedio de issues
avg(codepulse_issue_density{project="my-project"})
```

### Crear Alertas

```yaml
# prometheus-alerts.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-codepulse-alerts
  namespace: monitoring
data:
  codepulse.rules: |
    groups:
    - name: codepulse
      interval: 5m
      rules:
      - alert: CriticalIssuesDetected
        expr: sum(codepulse_issues_by_severity{severity="critical"}) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Critical code quality issues detected"
          description: "{{ $value }} critical issues found in {{ $labels.project }}"

      - alert: QualityScoreDrop
        expr: delta(codepulse_quality_score[1h]) < -10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Quality score dropped significantly"
          description: "Quality score dropped by {{ $value }} points in {{ $labels.project }}"

      - alert: HighIssueDensity
        expr: avg(codepulse_issue_density) > 20
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High issue density detected"
          description: "{{ $value }} issues per 1000 lines in {{ $labels.project }}"
```

## Ejemplo de Workflow Completo

### Escenario: Mejorar Calidad de Código

1. **Baseline** (Día 0):
   - Dashboard muestra: 45 issues totales, 5 CRITICAL
   - Quality Score: 65

2. **Sprint de Mejora** (Semana 1):
   - Desarrolladores arreglan issues críticos
   - Cada commit → CI/CD analiza y exporta métricas
   - Dashboard actualiza en tiempo real

3. **Revisión** (Día 7):
   - Dashboard "Before/After" muestra:
     - Issues totales: 45 → 15 (67% reducción)
     - CRITICAL: 5 → 0 (100% reducción)
     - Quality Score: 65 → 95 (46% mejora)

4. **Alertas**:
   - ✅ Alert "CriticalIssuesDetected" se resolvió
   - 📊 Métricas exportadas a sistema de reporting
   - 🎉 Equipo celebra mejora visible en dashboard

## Métricas Clave para Medir

### Calidad General
- **Quality Score**: Objetivo > 90
- **Issue Density**: Objetivo < 5 por 1000 líneas
- **Critical Issues**: Objetivo = 0

### Tendencias
- **Reduction Rate**: % de reducción semana a semana
- **New Issues**: Issues nuevos vs resueltos
- **Time to Fix**: Tiempo promedio para resolver issues

### Por Categoría
- **Performance**: Reducción de issues de rendimiento
- **Security**: Issues de seguridad = 0
- **Best Practices**: Mejora continua

## Troubleshooting

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
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# Abrir http://localhost:9090
# Query: codepulse_total_issues
```

### CI/CD no exporta métricas

```bash
# Ver logs de workflow
gh run list
gh run view <run-id>

# Verificar secret
gh secret list

# Test manual
curl -X POST \
  -H "Content-Type: text/plain" \
  --data-binary @metrics.txt \
  "${PROMETHEUS_PUSHGATEWAY_URL}/metrics/job/test"
```

## Resumen

✅ **Prometheus Exporter** - Exporta 8 métricas clave
✅ **Kubernetes CronJob** - Análisis automático cada hora
✅ **2 Dashboards Grafana** - Overview y Comparison
✅ **CI/CD Integration** - GitHub Actions con matrix
✅ **Alertas** - Notificaciones de issues críticos
✅ **Documentación completa** - Setup paso a paso

Con este setup, puedes visualizar y medir la mejora de calidad de código de forma continua y automática en Grafana! 📊
