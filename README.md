# Star Wars API

Uma API RESTful desenvolvida em Python para consultar informações sobre o universo Star Wars, consumindo dados da SWAPI (The Star Wars API) e fornecendo endpoints enriquecidos com relacionamentos completos entre entidades.

## Visão Geral

Esse projeto foi desenvolvido como parte de um desafio técnico para a posição de Desenvolvedor Backend Python Júnior na PowerOfData. A aplicação é executada no Google Cloud Platform utilizando Cloud Functions Gen 2 e API Gateway para fornecer uma interface unificada e escalável.

**IMPORTANTE**
### Autenticação
Todos os endpoints requerem autenticação via API Key. Adicione o header `x-api-key` em todas as requisições:
### api_key: AIzaSyDTlS64NzQ9NHKIWk9Id8Idd8m1oCvbExc
```bash
curl -H "x-api-key: YOUR_API_KEY" "https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/films?page=1"
```
### Observação: Sei que não é uma boa prática compartilhar chaves em repositórios públicos, porém como é um teste técnico utilizando uma api pública considerei que não teria problema em compartilhar

Requisições sem API Key retornarão erro 401 (Unauthorized).

## Arquitetura

A aplicação segue uma arquitetura serverless com os seguintes componentes:

- **Cloud Functions Gen 2**: Seis funções serverless (4 recursos + documentação Swagger UI + OpenAPI spec)
- **API Gateway**: Interface unificada que centraliza todos os endpoints com autenticação via API Key
- **SWAPI Client**: Cliente HTTP com cache LRU e retry automático
- **Validadores Pydantic**: Validação robusta de parâmetros de entrada
- **Sistema de Enriquecimento**: Busca e enriquece dados relacionados sob demanda
- **Paginação Obrigatória**: Todos os endpoints exigem parâmetro `page` para evitar timeout em requisições grandes

### Diagramas de Arquitetura

Diagramas C4 completos da arquitetura estão disponíveis em `arquitetura_tecnica/`:
- **C4_L1.png**: Diagrama de Contexto (visão geral do sistema)
- **C4_L2.png**: Diagrama de Containers (componentes principais)
- **C4_L3.png**: Diagrama de Componentes (detalhes de uma Cloud Function)
- **C4_L4.png**: Diagrama de Código (classes e validadores)
- **Diagrama_Deploy.png**: Infraestrutura GCP e deployment

Informações mais detalhadas dos diagramas no diretório `arquitetura_tecnica/README.md`.

## Recursos Disponíveis

### Documentação

A API possui documentação Swagger UI disponível em:

**URL**: `https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/docs`

Através do Swagger UI você pode:
- Visualizar todos os endpoints disponíveis
- Testar requisições diretamente no navegador
- Ver exemplos de respostas
- Consultar parâmetros obrigatórios e opcionais

A especificação OpenAPI completa está disponível em:
**URL**: `https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/openapi.yaml`

### Paginação

**IMPORTANTE**: Todos os endpoints exigem o parâmetro `page` (obrigatório) para evitar timeout em requisições grandes.

- Requisições sem o parâmetro `page` retornarão erro 400 (Bad Request)
- Todos os endpoints retornam informações de paginação na resposta:
  - `page`: Página atual
  - `page_size`: Quantidade de itens na página atual
  - `next`: Número da próxima página (null se não houver)
  - `previous`: Número da página anterior (null se não houver)
  - `total`: Total de itens disponíveis
  - `count`: Quantidade de itens na página atual

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
│   ├── swapi_client.py         # Cliente HTTP para SWAPI com cache LRU e retry
│   ├── validators.py           # Validadores Pydantic para todos os endpoints
│   ├── decorators.py           # Decoradores (CORS, logs, tratamento de erros)
│   └── utils.py                # Funções utilitárias e enriquecimento de dados
├── functions/                   # Cloud Functions Gen 2
│   ├── films/
│   │   ├── main.py             # Endpoint GET /films
│   │   ├── requirements.txt
│   │   └── [shared files]      # Cópias dos arquivos shared/
│   ├── characters/
│   │   ├── main.py             # Endpoint GET /characters
│   │   ├── requirements.txt
│   │   └── [shared files]
│   ├── planets/
│   │   ├── main.py             # Endpoint GET /planets
│   │   ├── requirements.txt
│   │   └── [shared files]
│   ├── starships/
│   │   ├── main.py             # Endpoint GET /starships
│   │   ├── requirements.txt
│   │   └── [shared files]
│   ├── swagger-ui/
│   │   └── main.py             # Documentação interativa Swagger UI
│   └── openapi-spec/
│       ├── main.py             # Endpoint GET /openapi.yaml
│       └── openapi.yaml        # Especificação OpenAPI servida
├── arquitetura_tecnica/         # Diagramas de arquitetura
│   ├── C4_L1.png               # Diagrama C4 - Contexto
│   ├── C4_L2.png               # Diagrama C4 - Containers
│   ├── C4_L3.png               # Diagrama C4 - Componentes
│   ├── C4_L4.png               # Diagrama C4 - Código
│   ├── Diagrama_Deploy.png     # Diagrama de Deploy GCP
│   └── README.md               # Explicação sobre C4 Model
├── deploy.sh                    # Script de deploy das 4 Cloud Functions principais
├── deploy-swagger.sh            # Script de deploy das Cloud Functions de documentação
├── deploy-gateway.sh            # Script de deploy do API Gateway
├── openapi.yaml                 # Especificação OpenAPI/Swagger 2.0 (fonte)
├── openapi-gateway.yaml         # Especificação para API Gateway (inclui /docs e /openapi.yaml)
├── requirements.txt             # Dependências de produção
├── .gitignore                   # Arquivos ignorados pelo git
└── README.md                    # Esse arquivo
```


## Tecnologias Utilizadas

- **Python 3.11**: Linguagem principal
- **Flask**: Framework web (usado pelo Functions Framework)
- **Pydantic**: Validação de dados e schemas
- **Requests**: Cliente HTTP com sessões persistentes
- **Google Cloud Functions Gen 2**: Serverless compute
- **Google Cloud API Gateway**: Gestão centralizada de APIs
- **Functions Framework**: Desenvolvimento e testes locais de Cloud Functions
- **Swagger UI**: Documentação interativa da API
- **SWAPI**: Fonte de dados externa (The Star Wars API)

## Deploy

### Pré-requisitos

- Google Cloud SDK instalado e configurado
- Projeto GCP criado com billing habilitado
- APIs necessárias habilitadas (Cloud Functions, Cloud Build, etc.)

### Deploy das Cloud Functions Principais

Execute o script automatizado para deploy dos 4 endpoints principais:

```bash
./deploy.sh
```

Esse script irá:
1. Validar a instalação do Google Cloud SDK
2. Verificar autenticação e configuração do projeto
3. Habilitar APIs necessárias (se ainda não estiverem)
4. Copiar arquivos compartilhados para cada função
5. Fazer deploy das 4 Cloud Functions: films, characters, planets, starships
6. Exibir URLs de acesso

### Deploy da Documentação (Swagger UI)

Executa o script de deploy das cloud functions de documentação:

```bash
./deploy-swagger.sh
```

- `swagger-ui`: Interface interativa Swagger UI (`/docs`)
- `openapi-spec`: Endpoint que serve a especificação OpenAPI (`/openapi.yaml`)

### Deploy do API Gateway

Executa o script de deploy do gateway para unificar todos os endpoints:

```bash
./deploy-gateway.sh
```

Esse script cria e configura o API Gateway que:
- Unifica todos os 6 endpoints em uma única URL
- Adiciona autenticação via API Key obrigatória
- Roteia requisições para as Cloud Functions correspondentes

## Desenvolvimento e Testes Locais

### Configurar Ambiente Virtual

É recomendado usar ambiente virtual Python (venv) para isolar as dependências:

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac/WSL
# ou
venv\Scripts\activate     # Windows
```

### Instalar Dependências

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências do projeto
pip install -r requirements.txt

# Instalar Functions Framework para testes locais
pip install functions-framework
```

### Testar Cloud Functions Localmente

Você pode executar qualquer Cloud Function localmente usando o Functions Framework:

#### Exemplo: Testar endpoint de filmes

```bash
# Navegar até o diretório da função
cd functions/films

# Executar localmente na porta 8080
functions-framework --target=get_films --port=8080
```

Em outro terminal, fazer requisições:

```bash
# Requisição simples
curl "http://localhost:8080?page=1"

# Com busca
curl "http://localhost:8080?page=1&search=Empire"

# Com enriquecimento completo
curl "http://localhost:8080?page=1&include_all=true"
```

#### Testar outros endpoints

```bash
# Characters na porta 8081
cd functions/characters
functions-framework --target=get_characters --port=8081
curl "http://localhost:8081?page=1&search=Luke"

# Planets na porta 8082
cd functions/planets
functions-framework --target=get_planets --port=8082
curl "http://localhost:8082?page=1&search=Tatooine"

# Starships na porta 8083
cd functions/starships
functions-framework --target=get_starships --port=8083
curl "http://localhost:8083?page=1&search=Falcon"
```

### Observações sobre Cache e Performance

As funções utilizam:
- **Cache LRU (@lru_cache)**: Segunda requisição com mesmos parâmetros é mais rápida
- **Retry automático**: Até 3 tentativas em caso de falhas transitórias
- **Paginação obrigatória**: Parâmetro `page` é obrigatório em todos os endpoints

Para verificar o cache funcionando, execute a mesma requisição duas vezes e compare o tempo:

```bash
time curl "http://localhost:8080?page=1"
time curl "http://localhost:8080?page=1"  # Deve ser mais rápido
```

