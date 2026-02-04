#!/bin/bash

################################################################################
# Deploy Script - Swagger UI e OpenAPI Spec Functions
#
# Esse shell script faz deploy das Cloud Functions necessárias para servir
# a interface gráfica do Swagger UI.
#
# Uso:
#   ./deploy-swagger.sh [PROJECT_ID] [REGION]
#
# Exemplos:
#   ./deploy-swagger.sh starwars-api-powerofdata us-central1
################################################################################

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funções auxiliares
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Configurações
PROJECT_ID=${1:-$(gcloud config get-value project 2>/dev/null)}
REGION=${2:-"us-central1"}

print_header "Deploy Swagger UI Functions"

# Validação: PROJECT_ID
if [ -z "$PROJECT_ID" ]; then
    print_error "PROJECT_ID não especificado!"
    echo "Uso: ./deploy-swagger.sh [PROJECT_ID] [REGION]"
    exit 1
fi

print_info "Projeto: $PROJECT_ID"
print_info "Região: $REGION"
echo ""

# Passo 1: Copiar openapi.yaml para função openapi-spec
print_header "Preparando openapi.yaml"

if [ ! -f "openapi.yaml" ]; then
    print_error "openapi.yaml não encontrado!"
    exit 1
fi

cp openapi.yaml functions/openapi-spec/openapi.yaml
print_success "openapi.yaml copiado para functions/openapi-spec/"
echo ""

# Passo 2: Deploy da função swagger-ui
print_header "Deploy: swagger-ui"

print_info "Deployando Cloud Function swagger-ui..."
gcloud functions deploy swagger-ui \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=functions/swagger-ui \
    --entry-point=swagger_ui \
    --trigger-http \
    --allow-unauthenticated \
    --memory=256MB \
    --timeout=60s \
    --max-instances=10 \
    --project=$PROJECT_ID

print_success "Função swagger-ui deployada!"
echo ""

# Passo 3: Deploy da função openapi-spec
print_header "Deploy: openapi-spec"

print_info "Deployando Cloud Function openapi-spec..."
gcloud functions deploy openapi-spec \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=functions/openapi-spec \
    --entry-point=openapi_spec \
    --trigger-http \
    --allow-unauthenticated \
    --memory=256MB \
    --timeout=60s \
    --max-instances=10 \
    --project=$PROJECT_ID

print_success "Função openapi-spec deployada!"
echo ""

# Passo 4: Obter URLs das funções
print_header "URLs das Funções"

SWAGGER_URL=$(gcloud functions describe swagger-ui \
    --gen2 \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(serviceConfig.uri)" 2>/dev/null)

OPENAPI_URL=$(gcloud functions describe openapi-spec \
    --gen2 \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(serviceConfig.uri)" 2>/dev/null)

echo ""
print_success "Swagger UI URL: $SWAGGER_URL"
print_success "OpenAPI Spec URL: $OPENAPI_URL"
echo ""

# Passo 5: Atualizar openapi.yaml com URLs corretas
print_header "Atualizando openapi.yaml"

print_info "As URLs das funções devem ser atualizadas no openapi.yaml:"
echo ""
echo "  /docs:"
echo "    x-google-backend:"
echo "      address: $SWAGGER_URL"
echo ""
echo "  /openapi.yaml:"
echo "    x-google-backend:"
echo "      address: $OPENAPI_URL"
echo ""

print_info "Após atualizar, execute: ./deploy-gateway.sh"
echo ""

print_header "Deploy Concluído"

echo ""
print_success "Funções deployadas com sucesso!"
echo ""
echo "Próximos passos:"
echo "1. Atualize o openapi.yaml com as URLs acima"
echo "2. Execute: ./deploy-gateway.sh"
echo "3. Acesse: https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/docs"
echo ""
