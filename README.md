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
curl "https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/films?search=empire&include_all=true"
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
curl "https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/characters?search=vader&include_all=true"
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
curl "https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/planets?search=tatooine"
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
curl "https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/starships?search=falcon"
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
├── deploy.sh                    # Script de deploy automatizado
├── deploy-gateway.sh            # Script de deploy do API Gateway
├── openapi.yaml                 # Especificação OpenAPI/Swagger 2.0
├── requirements.txt             # Dependências Python
├── .gitignore                   # Arquivos ignorados pelo git
└── README.md                    # Este arquivo
```

## Tecnologias Utilizadas

- **Python 3.11**: Linguagem principal
- **Flask**: Framework web (usado pelo Functions Framework)
- **Pydantic**: Validação de dados
- **Requests**: Cliente HTTP
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
