#!/bin/bash
# Setup completo del sistema de monitoreo de CodePulse

set -e

echo "=========================================="
echo "CodePulse Monitoring Setup"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar prerequisitos
echo -e "${BLUE}📋 Verificando prerequisitos...${NC}"

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl no está instalado${NC}"
    echo "Instalar: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
echo -e "${GREEN}✓ kubectl${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker no está instalado (opcional para build local)${NC}"
else
    echo -e "${GREEN}✓ docker${NC}"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ python3${NC}"

echo ""

# Configuración
echo -e "${BLUE}⚙️  Configuración${NC}"
read -p "Nombre del proyecto: " PROJECT_NAME
read -p "URL del repositorio Git: " GIT_REPO_URL
read -p "Branch (default: main): " GIT_BRANCH
GIT_BRANCH=${GIT_BRANCH:-main}
read -p "URL de Prometheus Pushgateway: " PUSHGATEWAY_URL

echo ""

# Paso 1: Build Docker image (opcional)
echo -e "${BLUE}🐳 Paso 1: Build Docker image${NC}"
read -p "¿Deseas hacer build de la imagen Docker localmente? (y/n): " BUILD_DOCKER

if [ "$BUILD_DOCKER" = "y" ]; then
    REGISTRY=""
    read -p "Registry de Docker (ej: docker.io/usuario, vacío para local): " REGISTRY

    if [ -n "$REGISTRY" ]; then
        IMAGE_NAME="$REGISTRY/codepulse-analyzer:latest"
    else
        IMAGE_NAME="codepulse/analyzer:latest"
    fi

    echo "Building $IMAGE_NAME..."
    docker build -f Dockerfile.analyzer -t $IMAGE_NAME .

    if [ -n "$REGISTRY" ]; then
        read -p "¿Deseas hacer push al registry? (y/n): " PUSH_DOCKER
        if [ "$PUSH_DOCKER" = "y" ]; then
            docker push $IMAGE_NAME
            echo -e "${GREEN}✓ Imagen pushed a $IMAGE_NAME${NC}"
        fi
    fi
else
    IMAGE_NAME="codepulse/analyzer:latest"
fi

echo ""

# Paso 2: Configurar Kubernetes
echo -e "${BLUE}☸️  Paso 2: Configurar Kubernetes${NC}"

# Crear namespace
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespace 'monitoring' creado${NC}"

# Actualizar ConfigMap
echo "Actualizando ConfigMap..."
cat > /tmp/codepulse-configmap.yaml <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: codepulse-config
  namespace: monitoring
data:
  project.name: "$PROJECT_NAME"
  git.repo.url: "$GIT_REPO_URL"
  git.branch: "$GIT_BRANCH"
  analyzers: "jvm-performance,spring-data,spring-security,spring-rest"
  prometheus.pushgateway.url: "$PUSHGATEWAY_URL"
EOF

kubectl apply -f /tmp/codepulse-configmap.yaml
echo -e "${GREEN}✓ ConfigMap configurado${NC}"

# Aplicar RBAC
kubectl apply -f k8s/codepulse-rbac.yaml
echo -e "${GREEN}✓ RBAC aplicado${NC}"

# Actualizar CronJob con la imagen correcta
sed "s|image:.*|image: $IMAGE_NAME|" k8s/codepulse-cronjob.yaml | kubectl apply -f -
echo -e "${GREEN}✓ CronJob desplegado${NC}"

# Aplicar ServiceMonitor
kubectl apply -f k8s/prometheus-servicemonitor.yaml
echo -e "${GREEN}✓ ServiceMonitor configurado${NC}"

echo ""

# Paso 3: GitHub Actions (opcional)
echo -e "${BLUE}🔄 Paso 3: GitHub Actions CI/CD${NC}"
read -p "¿Deseas configurar GitHub Actions? (y/n): " SETUP_GITHUB

if [ "$SETUP_GITHUB" = "y" ]; then
    if command -v gh &> /dev/null; then
        gh secret set PROMETHEUS_PUSHGATEWAY_URL --body "$PUSHGATEWAY_URL"
        echo -e "${GREEN}✓ Secret PROMETHEUS_PUSHGATEWAY_URL configurado${NC}"
        echo "Workflow: .github/workflows/codepulse-metrics.yml"
    else
        echo -e "${YELLOW}⚠ GitHub CLI (gh) no está instalado${NC}"
        echo "Configurar manualmente en: Settings → Secrets → Actions"
        echo "Secret: PROMETHEUS_PUSHGATEWAY_URL = $PUSHGATEWAY_URL"
    fi
fi

echo ""

# Paso 4: Verificación
echo -e "${BLUE}✅ Paso 4: Verificación${NC}"
echo "Verificando deployment..."

sleep 2

CRONJOB_STATUS=$(kubectl get cronjobs -n monitoring codepulse-analyzer -o jsonpath='{.spec.schedule}' 2>/dev/null || echo "NOT_FOUND")

if [ "$CRONJOB_STATUS" != "NOT_FOUND" ]; then
    echo -e "${GREEN}✓ CronJob desplegado correctamente${NC}"
    echo "  Schedule: $CRONJOB_STATUS"
else
    echo -e "${RED}❌ Error: CronJob no encontrado${NC}"
fi

echo ""

# Paso 5: Instrucciones finales
echo -e "${BLUE}📊 Paso 5: Grafana Dashboards${NC}"
echo ""
echo "Importar dashboards en Grafana:"
echo ""
echo "1. Dashboard Overview:"
echo "   - Ir a Grafana → Dashboards → Import"
echo "   - Copiar contenido de: grafana/codepulse-overview-dashboard.json"
echo "   - Seleccionar datasource: Prometheus"
echo ""
echo "2. Dashboard Comparison:"
echo "   - Ir a Grafana → Dashboards → Import"
echo "   - Copiar contenido de: grafana/codepulse-comparison-dashboard.json"
echo "   - Seleccionar datasource: Prometheus"
echo ""

# Resumen
echo ""
echo "=========================================="
echo -e "${GREEN}✅ Setup Completo${NC}"
echo "=========================================="
echo ""
echo "Recursos desplegados:"
echo "  - Namespace: monitoring"
echo "  - CronJob: codepulse-analyzer (ejecuta cada hora)"
echo "  - ConfigMap: codepulse-config"
echo "  - ServiceAccount: codepulse-analyzer"
echo "  - ServiceMonitor: codepulse-pushgateway"
echo ""
echo "Comandos útiles:"
echo ""
echo "  # Ver CronJobs"
echo "  kubectl get cronjobs -n monitoring"
echo ""
echo "  # Ver Jobs ejecutados"
echo "  kubectl get jobs -n monitoring"
echo ""
echo "  # Ver logs del último job"
echo "  kubectl logs -n monitoring -l app=codepulse --tail=100"
echo ""
echo "  # Trigger manual del job"
echo "  kubectl create job -n monitoring codepulse-manual --from=cronjob/codepulse-analyzer"
echo ""
echo "  # Verificar métricas en Pushgateway"
echo "  curl http://$PUSHGATEWAY_URL/metrics | grep codepulse"
echo ""
echo "📚 Documentación completa: docs/MONITORING_SETUP.md"
echo ""
