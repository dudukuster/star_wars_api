# Star Wars API

Uma API RESTful desenvolvida em Python para consultar informações sobre o universo Star Wars, consumindo dados da SWAPI (The Star Wars API) e fornecendo endpoints enriquecidos com relacionamentos completos entre entidades.

## Visão Geral

Este projeto foi desenvolvido como parte de um desafio técnico para a posição de Desenvolvedor Backend Python Júnior na PowerOfData. A aplicação é executada no Google Cloud Platform utilizando Cloud Functions Gen 2 e API Gateway para fornecer uma interface unificada e escalável.

## Arquitetura

A aplicação segue uma arquitetura serverless com os seguintes componentes:

- **Cloud Functions Gen 2**: Quatro funções serverless independentes para cada recurso
- **API Gateway**: Interface unificada que centraliza todos os endpoints
- **SWAPI Client**: Cliente HTTP com cache LRU e retry automático
- **Validadores Pydantic**: Validação robusta de parâmetros de entrada
- **Sistema de Enriquecimento**: Busca e enriquece dados relacionados sob demanda

## Recursos Disponíveis

### Autenticação

Todos os endpoints requerem autenticação via API Key. Inclua o header `x-api-key` em todas as requisições:

```bash
curl -H "x-api-key: YOUR_API_KEY" "https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/films"
```

Requisições sem API Key retornarão erro 401 (Unauthorized).

### Endpoints

A API oferece quatro endpoints principais, todos acessíveis através do API Gateway:

#### 1. Films (Filmes)

Consulta filmes da saga Star Wars com suporte a busca, ordenação e enriquecimento de dados relacionados.

**Endpoint**: `GET /films`

**Parâmetros**:
- `search` (string): Busca por título do filme
- `sort_by` (string): Campo para ordenação (title, release_date, episode_id)
- `order` (string): Ordem de classificação (asc, desc)
- `include_characters` (boolean): Incluir detalhes dos personagens
- `include_planets` (boolean): Incluir detalhes dos planetas
- `include_species` (boolean): Incluir detalhes das espécies
- `include_vehicles` (boolean): Incluir detalhes dos veículos
- `include_starships` (boolean): Incluir detalhes das naves
- `include_all` (boolean): Incluir todos os detalhes relacionados

**Exemplo**:
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/films?search=empire&include_all=true"
```

#### 2. Characters (Personagens)

Consulta personagens com filtros avançados e enriquecimento de dados relacionados.

**Endpoint**: `GET /characters`

**Parâmetros**:
- `search` (string): Busca por nome do personagem
- `page` (integer): Número da página (1-100)
- `gender` (string): Filtro por gênero (male, female, n/a, hermaphrodite)
- `include_films` (boolean): Incluir detalhes dos filmes
- `include_homeworld` (boolean): Incluir detalhes do planeta natal
- `include_species` (boolean): Incluir detalhes das espécies
- `include_vehicles` (boolean): Incluir detalhes dos veículos
- `include_starships` (boolean): Incluir detalhes das naves
- `include_all` (boolean): Incluir todos os detalhes relacionados

**Exemplo**:
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/characters?search=vader&include_all=true"
```

#### 3. Planets (Planetas)

Consulta planetas com suporte a busca, filtros e ordenação.

**Endpoint**: `GET /planets`

**Parâmetros**:
- `search` (string): Busca por nome do planeta
- `page` (integer): Número da página
- `climate` (string): Filtro por clima
- `terrain` (string): Filtro por terreno
- `sort_by` (string): Campo para ordenação
- `order` (string): Ordem de classificação

**Exemplo**:
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/planets?search=tatooine"
```

#### 4. Starships (Naves)

Consulta naves espaciais com filtros e ordenação.

**Endpoint**: `GET /starships`

**Parâmetros**:
- `search` (string): Busca por nome da nave
- `page` (integer): Número da página
- `starship_class` (string): Filtro por classe de nave
- `sort_by` (string): Campo para ordenação
- `order` (string): Ordem de classificação

**Exemplo**:
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/starships?search=falcon"
```

## Funcionalidades Principais

### Sistema de Enriquecimento de Dados

Um dos principais diferenciais desta API é o sistema de enriquecimento que permite incluir dados completos de entidades relacionadas a outras entidades através das URLs fornecidas pela SWAPI.

Por exemplo, ao buscar um filme com `include_all=true`, você recebe:
- Lista completa de personagens com todos os seus atributos
- Detalhes de todos os planetas que aparecem no filme
- Informações completas sobre espécies, veículos e naves

Isso elimina a necessidade de múltiplas requisições para obter dados relacionados.

### Validação e Tratamento de Erros

Todos os parâmetros são validados usando Pydantic, garantindo:
- Tipos de dados corretos
- Valores dentro de limites esperados
- Mensagens de erro claras e descritivas

### Performance e Resiliência

- **Cache LRU**: Reduz chamadas desnecessárias à SWAPI
- **Retry Automático**: Até 3 tentativas com backoff exponencial
- **Singleton Pattern**: Reutilização de conexões HTTP
- **Logging Estruturado**: Logs em formato JSON para fácil análise

## Estrutura do Projeto

```
star_wars_api/
├── shared/                      # Módulos compartilhados
│   ├── swapi_client.py         # Cliente HTTP para SWAPI
│   ├── validators.py           # Validadores Pydantic
│   ├── decorators.py           # Decoradores (CORS, logs, errors)
│   └── utils.py                # Funções utilitárias e enriquecimento
├── functions/                   # Cloud Functions
│   ├── films/
│   │   └── main.py
│   ├── characters/
│   │   └── main.py
│   ├── planets/
│   │   └── main.py
│   └── starships/
│       └── main.py
├── tests/                       # Testes unitários
│   ├── conftest.py             # Fixtures compartilhadas
│   ├── test_validators.py      # Testes de validação Pydantic
│   ├── test_utils.py           # Testes de funções utilitárias
│   ├── test_swapi_client.py    # Testes do cliente SWAPI
│   └── test_decorators.py      # Testes de decoradores
├── deploy.sh                    # Script de deploy automatizado
├── deploy-gateway.sh            # Script de deploy do API Gateway
├── openapi.yaml                 # Especificação OpenAPI/Swagger 2.0
├── requirements.txt             # Dependências de produção
├── requirements-dev.txt         # Dependências de desenvolvimento
├── pytest.ini                   # Configuração do pytest
├── .gitignore                   # Arquivos ignorados pelo git
└── README.md                    # Este arquivo
```


## Tecnologias Utilizadas

- **Python 3.11**: Linguagem principal
- **Flask**: Framework web (usado pelo Functions Framework)
- **Pydantic**: Validação de dados
- **Requests**: Cliente HTTP
- **Pytest**: Framework de testes
- **Google Cloud Functions Gen 2**: Serverless compute
- **Google Cloud API Gateway**: Gestão de APIs
- **SWAPI**: Fonte de dados externa

## Deploy

### Pré-requisitos

- Google Cloud SDK instalado e configurado
- Projeto GCP criado com billing habilitado
- APIs necessárias habilitadas (Cloud Functions, Cloud Build, etc.)

### Deploy das Cloud Functions

Execute o script automatizado:

```bash
./deploy.sh
```

Este script irá:
1. Validar a instalação do Google Cloud SDK
2. Verificar autenticação e configuração do projeto
3. Habilitar APIs necessárias (se ainda não estiverem)
4. Copiar arquivos compartilhados para cada função
5. Fazer deploy de todas as 4 Cloud Functions
6. Exibir URLs de acesso

### Deploy do API Gateway

Execute o script de deploy do gateway:

```bash
./deploy-gateway.sh
```

## Desenvolvimento Local

Para executar testes locais:

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar testes (quando implementados)
pytest tests/
```

## Testes

O projeto possui um diretório com 91 testes e 85.91% de cobertura de código, superando o requisito mínimo de 80%.

### Cobertura por Módulo

| Módulo | Cobertura | Descrição |
|--------|-----------|-----------|
| `validators.py` | 100% | Validação de parâmetros com Pydantic |
| `decorators.py` | 86% | CORS, logging e tratamento de erros |
| `swapi_client.py` | 83% | Cliente HTTP, cache e retry |
| `utils.py` | 81% | Funções de enriquecimento e utilidades |
| **Total** | **85.91%** | Cobertura geral do projeto |

### Arquivos que serão testados

#### 1. Validadores Pydantic (`test_validators.py`)
- Validação de parâmetros de query (page, search, filters)
- Enums (gender, sort_by, order)
- Limites de valores (min/max page, string length)
- Valores padrão e conversão de tipos
- Validações específicas de cada endpoint

#### 2. Funções Utilitárias (`test_utils.py`)
- Enriquecimento de dados (characters, films, planets, starships, species, vehicles)
- Filtragem case-insensitive com substring matching
- Ordenação com suporte a tipos mistos (strings numéricas)
- Truncamento de texto
- Busca de detalhes de entidades relacionadas
- Tratamento de erros e casos extremos

#### 3. Cliente SWAPI (`test_swapi_client.py`)
- Singleton pattern
- Extração de IDs de URLs
- Requisições HTTP com retry automático
- Cache LRU funcionando corretamente
- Todos os métodos de busca (films, characters, planets, starships, species, vehicles)
- Tratamento de erros HTTP (4xx, 5xx)

#### 4. Decoradores (`test_decorators.py`)
- Adição de headers CORS
- Tratamento de requisições OPTIONS (preflight)
- Logging estruturado de requisições
- Tratamento de erros (ValidationError, exceções genéricas)
- Combinação de múltiplos decoradores

### Como Executar os Testes

#### 1. Configurar Ambiente Virtual

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

#### 2. Instalar Dependências de Desenvolvimento

```bash
pip install -r requirements-dev.txt
```

As dependências de teste incluem:
- `pytest==7.4.3` - Framework de testes
- `pytest-cov==4.1.0` - Relatórios de cobertura
- `pytest-mock==3.12.0` - Utilitários para mocking
- `responses==0.24.1` - Mock de requisições HTTP

#### 3. Executar Todos os Testes

```bash
# Executar todos os testes com cobertura
pytest

# Executar com output detalhado
pytest -v

# Executar com cobertura detalhada
pytest --cov=shared --cov-report=term-missing

# Gerar relatório HTML de cobertura
pytest --cov=shared --cov-report=html
# O relatório será gerado em htmlcov/index.html
```

#### 4. Executar Testes Específicos

```bash
# Testar apenas validadores
pytest tests/test_validators.py

# Testar apenas o cliente SWAPI
pytest tests/test_swapi_client.py

# Executar um teste específico
pytest tests/test_validators.py::TestCharacterQueryParams::test_valid_params

# Executar testes que contêm uma palavra-chave
pytest -k "cache"
```

#### 5. Opções Úteis do Pytest

```bash
# Parar no primeiro erro
pytest -x

# Modo verbose com output de print
pytest -v -s

# Executar apenas testes que falharam na última execução
pytest --lf

# Ver os testes mais lentos
pytest --durations=10
```

### Estrutura dos Testes

Os testes seguem as melhores práticas do pytest:

- **Fixtures compartilhadas** em `conftest.py` com dados de exemplo (sample_character, sample_film, etc.)
- **Organização por classes** para agrupar testes relacionados
- **Nomes descritivos** que explicam o que está sendo testado
- **Mocks apropriados** para isolar unidades de código
- **Cobertura de casos extremos** (valores None, listas vazias, erros)

