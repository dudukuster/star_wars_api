"""
Funções utilitárias compartilhadas

Este módulo contém funções auxiliares usadas em múltiplas Cloud Functions,
incluindo formatação de dados, ordenação e enriquecimento de informações.
"""

import concurrent.futures
from typing import Any, Callable, Dict, List, Optional


def fetch_all_and_paginate(
    fetch_func: Callable,
    params: Any,
    filters: Optional[Dict[str, str]] = None,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Busca todos os dados da SWAPI em paralelo, aplica filtros locais,
    e retorna paginação correta do dataset filtrado.

    Esta função resolve o problema de paginação inconsistente quando
    aplicamos filtros que a SWAPI não suporta nativamente (como gender,
    climate, starship_class, etc).

    Args:
        fetch_func: Função para buscar dados (ex: client.get_people)
        params: Objeto QueryParams com parâmetros da requisição
        filters: Dict com filtros locais a aplicar (ex: {'gender': 'male'})
        page_size: Tamanho da página (default: 10)

    Returns:
        Dict com:
            - items: Lista de itens da página atual
            - total: Total de itens após aplicar filtros
            - next: Número da próxima página (None se não houver)
            - previous: Número da página anterior (None se não houver)

    Example:
        result = fetch_all_and_paginate(
            fetch_func=client.get_people,
            params=params,
            filters={'gender': params.gender},
            page_size=10
        )
    """
    # 1. Buscar primeira página para determinar total de páginas
    first_page = fetch_func(search=params.search, page=1)
    all_items = first_page.get('results', [])

    total_swapi = first_page.get('count', 0)
    items_per_page = len(first_page.get('results', [])) or 10
    total_pages = (total_swapi + items_per_page - 1) // items_per_page

    # 2. Buscar demais páginas em paralelo (se houver)
    if total_pages > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Criar futures para todas as páginas restantes
            future_to_page = {
                executor.submit(fetch_func, params.search, page): page
                for page in range(2, total_pages + 1)
            }

            # Coletar resultados conforme completam
            for future in concurrent.futures.as_completed(future_to_page):
                try:
                    data = future.result()
                    all_items.extend(data.get('results', []))
                except Exception:
                    # Em caso de erro em alguma página, continua com as demais
                    continue

    # 3. Aplicar filtros locais (se especificados)
    if filters:
        for field, value in filters.items():
            if value:  # Só aplica filtro se valor foi fornecido
                all_items = filter_by_field(all_items, field, value)

    # 4. Calcular totais do dataset filtrado
    total_filtered = len(all_items)
    total_pages_filtered = (total_filtered + page_size - 1) // page_size if total_filtered > 0 else 1

    # 5. Aplicar paginação no nosso dataset filtrado
    start_idx = (params.page - 1) * page_size
    end_idx = start_idx + page_size
    page_items = all_items[start_idx:end_idx]

    # 6. Calcular next/previous corretos
    next_page = params.page + 1 if params.page < total_pages_filtered else None
    previous_page = params.page - 1 if params.page > 1 else None

    return {
        'items': page_items,
        'total': total_filtered,
        'next': next_page,
        'previous': previous_page
    }


def fetch_films_details(film_urls: List[str], swapi_client) -> List[Dict]:
    """
    Busca detalhes completos dos filmes a partir de uma lista de URLs

    Args:
        film_urls: Lista de URLs de filmes da SWAPI
        swapi_client: Instância do SWAPIClient para fazer requisições

    Returns:
        Lista de dicionários com dados enriquecidos dos filmes
    """
    films = []

    for url in film_urls:
        try:
            # Extrair ID da URL
            film_id = swapi_client.extract_id_from_url(url)
            if film_id:
                # Buscar filme por ID
                film_data = swapi_client.get_film_by_id(film_id)
                # Reaproveitar função de enriquecimento existente
                enriched_film = enrich_film_data(film_data)
                films.append(enriched_film)
        except Exception:
            # Em caso de erro, ignora este filme e continua
            continue

    return films


def fetch_homeworld_details(homeworld_url: str, swapi_client) -> Optional[Dict]:
    """
    Busca detalhes completos do planeta de origem (homeworld)

    Args:
        homeworld_url: URL do planeta de origem
        swapi_client: Instância do SWAPIClient

    Returns:
        Dicionário com dados do planeta ou None se erro
    """
    if not homeworld_url:
        return None

    try:
        planet_id = swapi_client.extract_id_from_url(homeworld_url)
        if planet_id:
            planet_data = swapi_client.get_planet_by_id(planet_id)
            return enrich_planet_data(planet_data)
    except Exception:
        return None

    return None


def fetch_species_details(species_urls: List[str], swapi_client) -> List[Dict]:
    """
    Busca detalhes completos das espécies a partir de uma lista de URLs

    Args:
        species_urls: Lista de URLs de espécies da SWAPI
        swapi_client: Instância do SWAPIClient

    Returns:
        Lista de dicionários com dados das espécies
    """
    species = []

    for url in species_urls:
        try:
            species_id = swapi_client.extract_id_from_url(url)
            if species_id:
                species_data = swapi_client.get_species_by_id(species_id)
                enriched_species = enrich_species_data(species_data)
                species.append(enriched_species)
        except Exception:
            continue

    return species


def fetch_vehicles_details(vehicle_urls: List[str], swapi_client) -> List[Dict]:
    """
    Busca detalhes completos dos veículos a partir de uma lista de URLs

    Args:
        vehicle_urls: Lista de URLs de veículos da SWAPI
        swapi_client: Instância do SWAPIClient

    Returns:
        Lista de dicionários com dados dos veículos
    """
    vehicles = []

    for url in vehicle_urls:
        try:
            vehicle_id = swapi_client.extract_id_from_url(url)
            if vehicle_id:
                vehicle_data = swapi_client.get_vehicle_by_id(vehicle_id)
                enriched_vehicle = enrich_vehicle_data(vehicle_data)
                vehicles.append(enriched_vehicle)
        except Exception:
            continue

    return vehicles


def fetch_starships_details(starship_urls: List[str], swapi_client) -> List[Dict]:
    """
    Busca detalhes completos das naves a partir de uma lista de URLs

    Args:
        starship_urls: Lista de URLs de naves da SWAPI
        swapi_client: Instância do SWAPIClient

    Returns:
        Lista de dicionários com dados das naves
    """
    starships = []

    for url in starship_urls:
        try:
            starship_id = swapi_client.extract_id_from_url(url)
            if starship_id:
                starship_data = swapi_client.get_starship_by_id(starship_id)
                enriched_starship = enrich_starship_data(starship_data)
                starships.append(enriched_starship)
        except Exception:
            continue

    return starships


def fetch_characters_details(character_urls: List[str], swapi_client, enrich_homeworld: bool = False) -> List[Dict]:
    """
    Busca detalhes completos dos personagens a partir de uma lista de URLs

    Args:
        character_urls: Lista de URLs de personagens da SWAPI
        swapi_client: Instância do SWAPIClient
        enrich_homeworld: Se True, enriquece o homeworld de cada personagem (padrão: False)

    Returns:
        Lista de dicionários com dados dos personagens
    """
    characters = []

    for url in character_urls:
        try:
            character_id = swapi_client.extract_id_from_url(url)
            if character_id:
                character_data = swapi_client.get_person_by_id(character_id)
                enriched_character = enrich_character_data(character_data)

                # Enriquecer homeworld se solicitado
                if enrich_homeworld:
                    homeworld_url = character_data.get('homeworld')
                    if homeworld_url:
                        homeworld_details = fetch_homeworld_details(homeworld_url, swapi_client)
                        if homeworld_details:
                            enriched_character['homeworld'] = homeworld_details

                characters.append(enriched_character)
        except Exception:
            continue

    return characters


def fetch_planets_details(planet_urls: List[str], swapi_client) -> List[Dict]:
    """
    Busca detalhes completos dos planetas a partir de uma lista de URLs

    Args:
        planet_urls: Lista de URLs de planetas da SWAPI
        swapi_client: Instância do SWAPIClient

    Returns:
        Lista de dicionários com dados dos planetas
    """
    planets = []

    for url in planet_urls:
        try:
            planet_id = swapi_client.extract_id_from_url(url)
            if planet_id:
                planet_data = swapi_client.get_planet_by_id(planet_id)
                enriched_planet = enrich_planet_data(planet_data)
                planets.append(enriched_planet)
        except Exception:
            continue

    return planets


def fetch_films_details(film_urls: List[str], swapi_client) -> List[Dict]:
    """
    Busca detalhes completos dos filmes a partir de uma lista de URLs

    Args:
        film_urls: Lista de URLs de filmes da SWAPI
        swapi_client: Instância do SWAPIClient

    Returns:
        Lista de dicionários com dados dos filmes
    """
    films = []

    for url in film_urls:
        try:
            film_id = swapi_client.extract_id_from_url(url)
            if film_id:
                film_data = swapi_client.get_film_by_id(film_id)
                enriched_film = enrich_film_data(film_data)
                films.append(enriched_film)
        except Exception:
            continue

    return films


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Trunca texto para um tamanho máximo

    Args:
        text: Texto original
        max_length: Tamanho máximo (default: 100)

    Returns:
        Texto truncado com '...' se necessário
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


def enrich_film_data(film: Dict) -> Dict:
    """
    Enriquece dados de um filme com informações agregadas

    Adiciona contadores de personagens, planetas e naves.
    Trunca opening_crawl para 100 caracteres.

    Args:
        film: Dicionário com dados do filme da SWAPI

    Returns:
        Dicionário enriquecido
    """
    return {
        'episode_id': film.get('episode_id'),
        'title': film.get('title'),
        'release_date': film.get('release_date'),
        'director': film.get('director'),
        'producer': film.get('producer'),
        'opening_crawl': truncate_text(film.get('opening_crawl', '')),
        'characters_count': len(film.get('characters', [])),
        'planets_count': len(film.get('planets', [])),
        'starships_count': len(film.get('starships', [])),
        'vehicles_count': len(film.get('vehicles', [])),
        'species_count': len(film.get('species', [])),
        'url': film.get('url')
    }


def enrich_character_data(character: Dict) -> Dict:
    """
    Enriquece dados de um personagem

    Args:
        character: Dicionário com dados do personagem da SWAPI

    Returns:
        Dicionário enriquecido
    """
    return {
        'name': character.get('name'),
        'height': character.get('height'),
        'mass': character.get('mass'),
        'hair_color': character.get('hair_color'),
        'skin_color': character.get('skin_color'),
        'eye_color': character.get('eye_color'),
        'birth_year': character.get('birth_year'),
        'gender': character.get('gender'),
        'homeworld': character.get('homeworld'),
        'films_count': len(character.get('films', [])),
        'species_count': len(character.get('species', [])),
        'vehicles_count': len(character.get('vehicles', [])),
        'starships_count': len(character.get('starships', [])),
        'url': character.get('url')
    }


def enrich_planet_data(planet: Dict) -> Dict:
    """
    Enriquece dados de um planeta

    Args:
        planet: Dicionário com dados do planeta da SWAPI

    Returns:
        Dicionário enriquecido
    """
    return {
        'name': planet.get('name'),
        'rotation_period': planet.get('rotation_period'),
        'orbital_period': planet.get('orbital_period'),
        'diameter': planet.get('diameter'),
        'climate': planet.get('climate'),
        'gravity': planet.get('gravity'),
        'terrain': planet.get('terrain'),
        'surface_water': planet.get('surface_water'),
        'population': planet.get('population'),
        'residents_count': len(planet.get('residents', [])),
        'films_count': len(planet.get('films', [])),
        'url': planet.get('url')
    }


def enrich_species_data(species: Dict) -> Dict:
    """
    Enriquece dados de uma espécie

    Args:
        species: Dicionário com dados da espécie da SWAPI

    Returns:
        Dicionário enriquecido
    """
    return {
        'name': species.get('name'),
        'classification': species.get('classification'),
        'designation': species.get('designation'),
        'average_height': species.get('average_height'),
        'average_lifespan': species.get('average_lifespan'),
        'eye_colors': species.get('eye_colors'),
        'hair_colors': species.get('hair_colors'),
        'skin_colors': species.get('skin_colors'),
        'language': species.get('language'),
        'homeworld': species.get('homeworld'),
        'people_count': len(species.get('people', [])),
        'films_count': len(species.get('films', [])),
        'url': species.get('url')
    }


def enrich_vehicle_data(vehicle: Dict) -> Dict:
    """
    Enriquece dados de um veículo

    Args:
        vehicle: Dicionário com dados do veículo da SWAPI

    Returns:
        Dicionário enriquecido
    """
    return {
        'name': vehicle.get('name'),
        'model': vehicle.get('model'),
        'manufacturer': vehicle.get('manufacturer'),
        'cost_in_credits': vehicle.get('cost_in_credits'),
        'length': vehicle.get('length'),
        'max_atmosphering_speed': vehicle.get('max_atmosphering_speed'),
        'crew': vehicle.get('crew'),
        'passengers': vehicle.get('passengers'),
        'cargo_capacity': vehicle.get('cargo_capacity'),
        'consumables': vehicle.get('consumables'),
        'vehicle_class': vehicle.get('vehicle_class'),
        'pilots_count': len(vehicle.get('pilots', [])),
        'films_count': len(vehicle.get('films', [])),
        'url': vehicle.get('url')
    }


def enrich_starship_data(starship: Dict) -> Dict:
    """
    Enriquece dados de uma nave espacial

    Args:
        starship: Dicionário com dados da nave da SWAPI

    Returns:
        Dicionário enriquecido
    """
    return {
        'name': starship.get('name'),
        'model': starship.get('model'),
        'manufacturer': starship.get('manufacturer'),
        'cost_in_credits': starship.get('cost_in_credits'),
        'length': starship.get('length'),
        'max_atmosphering_speed': starship.get('max_atmosphering_speed'),
        'crew': starship.get('crew'),
        'passengers': starship.get('passengers'),
        'cargo_capacity': starship.get('cargo_capacity'),
        'consumables': starship.get('consumables'),
        'hyperdrive_rating': starship.get('hyperdrive_rating'),
        'MGLT': starship.get('MGLT'),
        'starship_class': starship.get('starship_class'),
        'pilots_count': len(starship.get('pilots', [])),
        'films_count': len(starship.get('films', [])),
        'url': starship.get('url')
    }


def sort_data(
    data: List[Dict],
    sort_by: str,
    order: str = "asc"
) -> List[Dict]:
    """
    Ordena lista de dicionários por um campo específico

    Args:
        data: Lista de dicionários
        sort_by: Campo para ordenação
        order: Ordem ("asc" ou "desc")

    Returns:
        Lista ordenada
    """
    reverse = (order == "desc")

    def get_sort_key(item: Dict) -> Any:
        """Obtém valor do campo, tratando None e conversão numérica"""
        value = item.get(sort_by)

        # Tratar valores None
        if value is None:
            return float('inf')  # Coloca None no final

        # Tentar converter para número se for string numérica
        if isinstance(value, str):
            try:
                # Tenta converter para int primeiro
                if '.' not in value:
                    return int(value)
                # Senão, tenta float
                return float(value)
            except (ValueError, TypeError):
                # Se não for número, retorna string lowercase para comparação
                return value.lower()

        return value

    return sorted(data, key=get_sort_key, reverse=reverse)


def filter_by_field(
    data: List[Dict],
    field: str,
    value: str
) -> List[Dict]:
    """
    Filtra lista de dicionários por um campo específico

    Faz comparação case-insensitive e busca substring.

    Args:
        data: Lista de dicionários
        field: Campo para filtrar
        value: Valor a buscar

    Returns:
        Lista filtrada
    """
    if not value:
        return data

    value_lower = value.lower()

    return [
        item for item in data
        if item.get(field) and value_lower in str(item.get(field)).lower()
    ]
