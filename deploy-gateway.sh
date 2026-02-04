#!/bin/bash

################################################################################
# Deploy Script - API Gateway para Star Wars API
#
# Esse script configura e deploya o API Gateway do GCP para unificar
# as 4 Cloud Functions em uma única URL.
#
# Uso:
#   ./deploy-gateway.sh [PROJECT_ID] [REGION]
#
# Exemplos:
#   ./deploy-gateway.sh starwars-api-powerofdata us-central1
################################################################################

set -e  # Para execução se houver erro

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

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Configurações
PROJECT_ID=${1:-$(gcloud config get-value project 2>/dev/null)}
REGION=${2:-"us-central1"}
API_ID="starwars-api"
API_CONFIG_ID="starwars-api-config"
GATEWAY_ID="starwars-api-gateway"

print_header "Star Wars API - Deploy API Gateway"

# Validação 1: Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud SDK não encontrado!"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
print_success "Google Cloud SDK instalado"

# Validação 2: Verificar se PROJECT_ID foi fornecido
if [ -z "$PROJECT_ID" ]; then
    print_error "PROJECT_ID não especificado!"
    echo ""
    echo "Uso:"
    echo "  ./deploy-gateway.sh [PROJECT_ID] [REGION]"
    echo ""
    echo "Ou configure o projeto padrão:"
    echo "  gcloud config set project SEU_PROJECT_ID"
    exit 1
fi

print_info "Projeto: $PROJECT_ID"
print_info "Região: $REGION"
print_info "API ID: $API_ID"
print_info "Gateway ID: $GATEWAY_ID"
echo ""

# Validação 3: Verificar se openapi-gateway.yaml existe
if [ ! -f "openapi-gateway.yaml" ]; then
    print_error "Arquivo openapi-gateway.yaml não encontrado!"
    echo "Certifique-se de estar no diretório raiz do projeto."
    exit 1
fi
print_success "Arquivo openapi-gateway.yaml encontrado"

# Validação 4: Verificar autenticação
print_info "Verificando autenticação..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    print_error "Não autenticado no GCP!"
    echo "Execute: gcloud auth login"
    exit 1
fi
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
print_success "Autenticado como: $ACCOUNT"

echo ""
print_header "Habilitando APIs Necessárias"

# Habilitar API do API Gateway
REQUIRED_APIS=(
    "apigateway.googleapis.com"
    "servicemanagement.googleapis.com"
    "servicecontrol.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    if gcloud services list --enabled --project=$PROJECT_ID --filter="name:$api" --format="value(name)" 2>/dev/null | grep -q "$api"; then
        print_success "API habilitada: $api"
    else
        print_warning "API não habilitada: $api"
        print_info "Habilitando $api..."
        gcloud services enable $api --project=$PROJECT_ID
        print_success "API $api habilitada"
    fi
done

echo ""
print_header "Criando/Atualizando API"

# Verificar se API já existe
if gcloud api-gateway apis describe $API_ID --project=$PROJECT_ID &> /dev/null; then
    print_info "API $API_ID já existe"
else
    print_info "Criando API $API_ID..."
    gcloud api-gateway apis create $API_ID \
        --project=$PROJECT_ID \
        --display-name="Star Wars API"
    print_success "API criada"
fi

echo ""
print_header "Criando Configuração da API"

print_info "Deployando openapi.yaml..."

# Gerar ID único para a configuração (evita conflitos)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
CONFIG_ID="${API_CONFIG_ID}-${TIMESTAMP}"

print_info "Config ID: $CONFIG_ID"

# Deploy da configuração
if gcloud api-gateway api-configs create $CONFIG_ID \
    --api=$API_ID \
    --openapi-spec=openapi-gateway.yaml \
    --project=$PROJECT_ID \
    --backend-auth-service-account=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")-compute@developer.gserviceaccount.com 2>&1 | tee /tmp/api-config-deploy.log; then

    print_success "Configuração da API criada!"
else
    print_error "Erro ao criar configuração da API"
    cat /tmp/api-config-deploy.log
    exit 1
fi

echo ""
print_header "Criando/Atualizando Gateway"

# Verificar se Gateway já existe
if gcloud api-gateway gateways describe $GATEWAY_ID --location=$REGION --project=$PROJECT_ID &> /dev/null; then
    print_info "Gateway $GATEWAY_ID já existe. Atualizando..."

    gcloud api-gateway gateways update $GATEWAY_ID \
        --api=$API_ID \
        --api-config=$CONFIG_ID \
        --location=$REGION \
        --project=$PROJECT_ID \
        --quiet

    print_success "Gateway atualizado!"
else
    print_info "Criando Gateway $GATEWAY_ID..."

    gcloud api-gateway gateways create $GATEWAY_ID \
        --api=$API_ID \
        --api-config=$CONFIG_ID \
        --location=$REGION \
        --project=$PROJECT_ID

    print_success "Gateway criado!"
fi

echo ""
print_header "Obtendo URL do Gateway"

# Aguardar Gateway ficar ativo (pode levar alguns segundos)
print_info "Aguardando Gateway ficar ativo..."
sleep 5

GATEWAY_URL=$(gcloud api-gateway gateways describe $GATEWAY_ID \
    --location=$REGION \
    --project=$PROJECT_ID \
    --format="value(defaultHostname)" 2>/dev/null)

if [ -z "$GATEWAY_URL" ]; then
    print_warning "Não foi possível obter URL automaticamente"
    print_info "Execute para obter a URL:"
    echo "gcloud api-gateway gateways describe $GATEWAY_ID --location=$REGION --project=$PROJECT_ID"
else
    GATEWAY_URL="https://${GATEWAY_URL}"
    print_success "Gateway deployado com sucesso!"
fi

echo ""
print_header "Deploy do API Gateway Concluído! 🎉"

if [ -n "$GATEWAY_URL" ]; then
    echo ""
    echo -e "${GREEN}📍 URL Única do API Gateway:${NC}"
    echo "   $GATEWAY_URL"
    echo ""
    echo -e "${GREEN}Endpoints disponíveis:${NC}"
    echo "   ${GATEWAY_URL}/films"
    echo "   ${GATEWAY_URL}/characters"
    echo "   ${GATEWAY_URL}/planets"
    echo "   ${GATEWAY_URL}/starships"
    echo ""
fi

echo ""
print_header "Testes Rápidos"

if [ -n "$GATEWAY_URL" ]; then
    echo ""
    echo "Teste com curl:"
    echo ""
    echo "# Filmes:"
    echo "curl \"${GATEWAY_URL}/films?search=empire\""
    echo ""
    echo "# Personagens:"
    echo "curl \"${GATEWAY_URL}/characters?search=luke&include_films=true\""
    echo ""
    echo "# Planetas:"
    echo "curl \"${GATEWAY_URL}/planets?search=tatooine\""
    echo ""
    echo "# Naves:"
    echo "curl \"${GATEWAY_URL}/starships?search=falcon\""
    echo ""
fi

echo ""
print_header "Comandos Úteis"

echo ""
echo "# Ver detalhes do Gateway:"
echo "gcloud api-gateway gateways describe $GATEWAY_ID --location=$REGION --project=$PROJECT_ID"
echo ""
echo "# Ver configurações da API:"
echo "gcloud api-gateway api-configs list --api=$API_ID --project=$PROJECT_ID"
echo ""
echo "# Ver logs do Gateway:"
echo "gcloud logging read \"resource.type=api_gateway\" --project=$PROJECT_ID --limit=50"
echo ""
echo "# Deletar Gateway (se necessário):"
echo "gcloud api-gateway gateways delete $GATEWAY_ID --location=$REGION --project=$PROJECT_ID"
echo ""

print_success "API Gateway pronto para uso! 🚀"

echo ""
print_info "Documentação Swagger:"
echo "- Acesse: https://editor.swagger.io"
echo "- Carregue o arquivo: openapi.yaml"
echo "- Ou use URL direta (após commit no GitHub):"
echo "  https://editor.swagger.io/?url=https://raw.githubusercontent.com/seu-usuario/star-wars-api/main/openapi.yaml"
