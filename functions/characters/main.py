"""
Cloud Function: Consulta de Personagens

Endpoint GET /get-characters que retorna personagens da saga Star Wars
com suporte a busca, paginação e filtros.

UC relacionado: UC-API-003
"""

import functions_framework
import json
from flask import Request

from swapi_client import get_swapi_client
from validators import CharacterQueryParams
from decorators import add_cors_headers, log_request, handle_errors
from utils import (
    enrich_character_data,
    filter_by_field,
    fetch_films_details,
    fetch_homeworld_details,
    fetch_species_details,
    fetch_vehicles_details,
    fetch_starships_details
)


@functions_framework.http
@add_cors_headers
@log_request
@handle_errors
def get_characters(request: Request):
    """
    Busca personagens da saga Star Wars

    Query Parameters:
        search (str): Busca por nome
        page (int): Número da página (1-100)
        gender (str): Filtro por gênero (male, female, n/a, hermaphrodite)
        include_films (bool): Incluir detalhes completos dos filmes
        include_homeworld (bool): Incluir detalhes do planeta de origem
        include_species (bool): Incluir detalhes das espécies
        include_vehicles (bool): Incluir detalhes dos veículos pilotados
        include_starships (bool): Incluir detalhes das naves pilotadas
        include_all (bool): Incluir TODOS os detalhes relacionados

    Returns:
        JSON com lista de personagens enriquecidos

    Exemplos:
        GET /get-characters
        GET /get-characters?search=luke
        GET /get-characters?page=2
        GET /get-characters?gender=female
        GET /get-characters?search=vader&include_films=true
        GET /get-characters?search=luke&include_homeworld=true&include_starships=true
        GET /get-characters?search=vader&include_all=true  (Recomendado!)
    """
    # Extrair e validar parâmetros com Pydantic
    page_str = request.args.get('page')
    if not page_str:
        return (
            json.dumps({
                'success': False,
                'error': 'Validation Error',
                'message': 'O parâmetro "page" é obrigatório',
                'details': [{'field': 'page', 'message': 'Campo obrigatório'}]
            }),
            400,
            {'Content-Type': 'application/json'}
        )

    params = CharacterQueryParams(
        search=request.args.get('search'),
        page=int(page_str),
        gender=request.args.get('gender'),
        include_films=request.args.get('include_films', 'false').lower() == 'true',
        include_homeworld=request.args.get('include_homeworld', 'false').lower() == 'true',
        include_species=request.args.get('include_species', 'false').lower() == 'true',
        include_vehicles=request.args.get('include_vehicles', 'false').lower() == 'true',
        include_starships=request.args.get('include_starships', 'false').lower() == 'true',
        include_all=request.args.get('include_all', 'false').lower() == 'true'
    )

    # Buscar personagens na SWAPI (usando singleton)
    client = get_swapi_client()
    data = client.get_people(search=params.search, page=params.page)

    characters = data.get('results', [])

    # Aplicar filtro de gênero se especificado
    if params.gender:
        characters = filter_by_field(characters, 'gender', params.gender)

    # Enriquecer dados
    enriched_characters = []
    for char in characters:
        enriched_char = enrich_character_data(char)

        # Se include_all=true, habilitar todos os includes
        if params.include_all:
            params.include_films = True
            params.include_homeworld = True
            params.include_species = True
            params.include_vehicles = True
            params.include_starships = True

        # Incluir detalhes completos dos filmes
        if params.include_films:
            film_urls = char.get('films', [])
            enriched_char['films'] = fetch_films_details(film_urls, client)

        # Incluir detalhes do planeta de origem (homeworld)
        if params.include_homeworld:
            homeworld_url = char.get('homeworld')
            homeworld_details = fetch_homeworld_details(homeworld_url, client)
            if homeworld_details:
                enriched_char['homeworld'] = homeworld_details
            else:
                # Manter URL original se não conseguir buscar
                enriched_char['homeworld'] = homeworld_url

        # Incluir detalhes das espécies
        if params.include_species:
            species_urls = char.get('species', [])
            enriched_char['species'] = fetch_species_details(species_urls, client)

        # Incluir detalhes dos veículos
        if params.include_vehicles:
            vehicle_urls = char.get('vehicles', [])
            enriched_char['vehicles'] = fetch_vehicles_details(vehicle_urls, client)

        # Incluir detalhes das naves
        if params.include_starships:
            starship_urls = char.get('starships', [])
            enriched_char['starships'] = fetch_starships_details(starship_urls, client)

        enriched_characters.append(enriched_char)

    # Calcular próxima e anterior página
    next_page = params.page + 1 if data.get('next') else None
    previous_page = params.page - 1 if params.page > 1 else None

    # Montar resposta padronizada
    response = {
        'success': True,
        'count': len(enriched_characters),
        'total': data.get('count', 0),
        'page': params.page,
        'page_size': len(enriched_characters),
        'next': next_page,
        'previous': previous_page,
        'data': enriched_characters
    }

    return (
        json.dumps(response),
        200,
        {'Content-Type': 'application/json'}
    )
