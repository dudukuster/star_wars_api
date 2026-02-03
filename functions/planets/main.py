"""
Cloud Function: Consulta de Planetas

Endpoint GET /get-planets que retorna planetas da saga Star Wars
com suporte a busca, paginação e filtros.

UC relacionado: UC-API-004
"""

import functions_framework
import json
from flask import Request

from swapi_client import get_swapi_client
from validators import PlanetQueryParams
from decorators import add_cors_headers, log_request, handle_errors
from utils import (
    enrich_planet_data,
    filter_by_field,
    fetch_characters_details,
    fetch_films_details
)


@functions_framework.http
@add_cors_headers
@log_request
@handle_errors
def get_planets(request: Request):
    """
    Busca planetas da saga Star Wars

    Query Parameters:
        search (str): Busca por nome
        page (int): Número da página (1-100)
        climate (str): Filtro por clima
        terrain (str): Filtro por terreno
        include_residents (bool): Incluir detalhes completos dos residentes
        include_films (bool): Incluir detalhes completos dos filmes
        include_all (bool): Incluir TODOS os detalhes relacionados

    Returns:
        JSON com lista de planetas enriquecidos

    Exemplos:
        GET /get-planets
        GET /get-planets?search=tatooine
        GET /get-planets?page=2
        GET /get-planets?climate=arid
        GET /get-planets?terrain=desert
        GET /get-planets?search=tatooine&include_all=true  (Recomendado!)
    """
    # Extrair e validar parâmetros (Pydantic faz conversão e validação automaticamente)
    params = PlanetQueryParams(
        search=request.args.get('search'),
        page=request.args.get('page', '1'),  # String, Pydantic converte para int
        climate=request.args.get('climate'),
        terrain=request.args.get('terrain'),
        include_residents=request.args.get('include_residents', 'false').lower() == 'true',
        include_films=request.args.get('include_films', 'false').lower() == 'true',
        include_all=request.args.get('include_all', 'false').lower() == 'true'
    )

    # Buscar planetas na SWAPI (usando singleton)
    client = get_swapi_client()
    data = client.get_planets(search=params.search, page=params.page)

    planets = data.get('results', [])

    # Aplicar filtros se especificados
    if params.climate:
        planets = filter_by_field(planets, 'climate', params.climate)

    if params.terrain:
        planets = filter_by_field(planets, 'terrain', params.terrain)

    # Enriquecer dados
    enriched_planets = []
    for planet in planets:
        enriched_planet = enrich_planet_data(planet)

        # Se include_all=true, habilitar todos os includes
        if params.include_all:
            params.include_residents = True
            params.include_films = True

        # Incluir detalhes completos dos residentes
        if params.include_residents:
            resident_urls = planet.get('residents', [])
            enriched_planet['residents'] = fetch_characters_details(resident_urls, client)

        # Incluir detalhes completos dos filmes
        if params.include_films:
            film_urls = planet.get('films', [])
            enriched_planet['films'] = fetch_films_details(film_urls, client)

        enriched_planets.append(enriched_planet)

    # Montar resposta
    response = {
        'success': True,
        'count': len(enriched_planets),
        'total': data.get('count', 0),
        'next': data.get('next'),
        'previous': data.get('previous'),
        'data': enriched_planets
    }

    return (
        json.dumps(response),
        200,
        {'Content-Type': 'application/json'}
    )
