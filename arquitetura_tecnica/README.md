# Diagramas C4

O C4 Model (Context, Containers, Components, Code) é uma abordagem para visualização de arquitetura de software criada por Simon Brown. O modelo utiliza uma hierarquia de diagramas com diferentes níveis de abstração, permitindo que diferentes públicos compreendam o sistema de acordo com suas necessidades, foi utilizado o plantuml para a construção dos diagramas (documentação em referências)

## Os 4 Níveis do C4

### Nível 1: Context (Contexto)
Mostra o sistema como uma caixa preta no centro, cercado pelos usuários e outros sistemas com os quais interage. É o diagrama mais abstrato e voltado para stakeholders não técnicos.

### Nível 2: Container (Containers)
Detalha as aplicações e serviços que compõem o sistema. Um "container" pode ser uma aplicação web, API, banco de dados, sistema de arquivos, etc. Não confundir com Docker containers.

### Nível 3: Component (Componentes)
Detalha os componentes internos de um container específico. Mostra as principais abstrações estruturais e suas relações.

### Nível 4: Code (Código)
Nível mais detalhado, mostra como um componente específico é implementado. Geralmente representado por diagramas de classe UML.

## Diagramas Deste Projeto

### C4_1_CONTEXT.png
Visão geral do sistema Star Wars API, mostrando usuários, o sistema principal e sistemas externos (SWAPI, GCP).

### C4_2_CONTAINER.png
Detalhamento das Cloud Functions (films, characters, planets, starships, swagger-ui, openapi-spec), API Gateway, Cache LRU e Cloud Logging.

### C4_3_COMPONENT.png
Componentes internos da Films Cloud Function, incluindo decorators, validators, SWAPI client, pagination logic, enrichment logic e structured logger.

### C4_4_CODE.png
Estrutura de classes dos validadores Pydantic, mostrando herança, enums e relacionamentos entre FilmQueryParams, CharacterQueryParams, PlanetQueryParams e StarshipQueryParams.

### Diagrama_Deploy.png
Infraestrutura do Google Cloud Platform, incluindo API Gateway, Cloud Functions Gen2, Cloud Run, Cloud Build, Artifact Registry, Cloud Logging e IAM.

## Referências

**C4 Model:** https://c4model.com/
**C4-PlantUML:** https://github.com/plantuml-stdlib/C4-PlantUML