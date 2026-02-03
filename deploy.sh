#!/bin/bash

################################################################################
# Deploy Script - Star Wars API PowerOfData
#
# Este script automatiza o deploy das Cloud Functions no Google Cloud Platform
#
# Uso:
#   ./deploy.sh [PROJECT_ID] [REGION]
#
# Exemplos:
#   ./deploy.sh starwars-api-powerofdata us-central1
#   ./deploy.sh (usa projeto atual e us-central1)
################################################################################

set -e  # Para execução se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
RUNTIME="python311"
FUNCTIONS=("films" "characters" "planets" "starships")

print_header "Star Wars API - Deploy no GCP"

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
    echo "  ./deploy.sh [PROJECT_ID] [REGION]"
    echo ""
    echo "Ou configure o projeto padrão:"
    echo "  gcloud config set project SEU_PROJECT_ID"
    exit 1
fi

print_info "Projeto: $PROJECT_ID"
print_info "Região: $REGION"
print_info "Runtime: $RUNTIME"
echo ""

# Validação 3: Verificar se está autenticado
print_info "Verificando autenticação..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    print_error "Não autenticado no GCP!"
    echo "Execute: gcloud auth login"
    exit 1
fi
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
print_success "Autenticado como: $ACCOUNT"

# Validação 4: Verificar se o projeto existe
print_info "Verificando projeto..."
if ! gcloud projects describe $PROJECT_ID &> /dev/null; then
    print_error "Projeto $PROJECT_ID não encontrado!"
    echo "Crie em: https://console.cloud.google.com/projectcreate"
    exit 1
fi
print_success "Projeto encontrado"

# Validação 5: Verificar APIs necessárias
print_info "Verificando APIs habilitadas..."
REQUIRED_APIS=(
    "cloudfunctions.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
    "run.googleapis.com"
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
print_header "Preparando arquivos para deploy"

# Passo 1: Copiar arquivos shared para cada função
for func in "${FUNCTIONS[@]}"; do
    print_info "Copiando arquivos shared para functions/$func/..."

    # Verificar se diretório existe
    if [ ! -d "functions/$func" ]; then
        print_error "Diretório functions/$func não encontrado!"
        exit 1
    fi

    # Copiar arquivos do shared
    cp shared/swapi_client.py functions/$func/
    cp shared/validators.py functions/$func/
    cp shared/decorators.py functions/$func/
    cp shared/utils.py functions/$func/
    cp shared/__init__.py functions/$func/

    print_success "Arquivos copiados para $func"
done

echo ""
print_header "Deployando Cloud Functions"

# Array para armazenar URLs
declare -A FUNCTION_URLS

# Passo 2: Deploy de cada função
for func in "${FUNCTIONS[@]}"; do
    FUNCTION_NAME="get-$func"
    ENTRY_POINT="get_${func}"
    SOURCE_DIR="./functions/$func"

    print_info "Deployando $FUNCTION_NAME..."
    echo ""

    # Deploy com output detalhado
    if gcloud functions deploy $FUNCTION_NAME \
        --gen2 \
        --runtime=$RUNTIME \
        --region=$REGION \
        --source=$SOURCE_DIR \
        --entry-point=$ENTRY_POINT \
        --trigger-http \
        --allow-unauthenticated \
        --timeout=60s \
        --memory=256MB \
        --project=$PROJECT_ID 2>&1 | tee /tmp/deploy_$func.log; then

        print_success "$FUNCTION_NAME deployada com sucesso!"

        # Obter URL da função
        URL=$(gcloud functions describe $FUNCTION_NAME \
            --gen2 \
            --region=$REGION \
            --project=$PROJECT_ID \
            --format="value(serviceConfig.uri)" 2>/dev/null)

        FUNCTION_URLS[$FUNCTION_NAME]=$URL

    else
        print_error "Erro ao deployar $FUNCTION_NAME"
        echo "Veja detalhes em: /tmp/deploy_$func.log"
        exit 1
    fi

    echo ""
done

echo ""
print_header "Deploy Concluído com Sucesso! 🎉"

echo ""
echo "URLs das Cloud Functions:"
echo ""

for func in "${FUNCTIONS[@]}"; do
    FUNCTION_NAME="get-$func"
    URL=${FUNCTION_URLS[$FUNCTION_NAME]}
    echo -e "${GREEN}📍 $FUNCTION_NAME${NC}"
    echo "   $URL"
    echo ""
done

echo ""
print_header "Testes Rápidos"

echo ""
echo "Teste com curl:"
echo ""

for func in "${FUNCTIONS[@]}"; do
    FUNCTION_NAME="get-$func"
    URL=${FUNCTION_URLS[$FUNCTION_NAME]}

    case $func in
        "films")
            echo "# Filmes:"
            echo "curl \"$URL?search=empire\""
            ;;
        "characters")
            echo "# Personagens:"
            echo "curl \"$URL?search=luke&include_films=true\""
            ;;
        "planets")
            echo "curl \"$URL?search=tatooine\""
            ;;
        "starships")
            echo "curl \"$URL?search=falcon\""
            ;;
    esac
    echo ""
done

echo ""
print_info "Para ver logs:"
echo "gcloud functions logs read NOME_DA_FUNCAO --gen2 --region=$REGION --project=$PROJECT_ID"

echo ""
print_success "Deploy finalizado! 🚀"
