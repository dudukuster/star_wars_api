"""
Cloud Function: Consulta de Filmes

Endpoint GET /get-films que retorna filmes da saga Star Wars
com suporte a busca, ordenação e filtros.

UC relacionado: UC-API-002

Nota: Os imports abaixo assumem que os arquivos do shared/ foram copiados
para este diretório durante o deploy (feito automaticamente pelo script deploy.sh)
"""

import functions_framework
import json
from flask import Request
from pydantic import ValidationError

from swapi_client import get_swapi_client
from validators import FilmQueryParams
from decorators import add_cors_headers, log_request, handle_errors
from utils import (
    enrich_film_data,
    sort_data,
    fetch_characters_details,
    fetch_planets_details,
    fetch_species_details,
    fetch_vehicles_details,
    fetch_starships_details
)


@functions_framework.http
@add_cors_headers
@log_request
@handle_errors
def get_films(request: Request):
    """
    Busca filmes da saga Star Wars

    Query Parameters:
        search (str): Busca por título
        sort_by (str): Campo para ordenação (title, release_date, episode_id)
        order (str): Ordem (asc, desc)
        include_characters (bool): Incluir detalhes completos dos personagens
        include_planets (bool): Incluir detalhes completos dos planetas
        include_species (bool): Incluir detalhes completos das espécies
        include_vehicles (bool): Incluir detalhes completos dos veículos
        include_starships (bool): Incluir detalhes completos das naves
        include_all (bool): Incluir TODOS os detalhes relacionados

    Returns:
        JSON com lista de filmes enriquecidos

    Exemplos:
        GET /get-films
        GET /get-films?search=empire
        GET /get-films?sort_by=title&order=asc
        GET /get-films?search=star&sort_by=episode_id&order=desc
        GET /get-films?search=hope&include_characters=true
        GET /get-films?search=empire&include_all=true  (Recomendado!)
    """
    # Extrair e validar parâmetros
    params = FilmQueryParams(
        search=request.args.get('search'),
        sort_by=request.args.get('sort_by', 'release_date'),
        order=request.args.get('order', 'asc'),
        include_characters=request.args.get('include_characters', 'false').lower() == 'true',
        include_planets=request.args.get('include_planets', 'false').lower() == 'true',
        include_species=request.args.get('include_species', 'false').lower() == 'true',
        include_vehicles=request.args.get('include_vehicles', 'false').lower() == 'true',
        include_starships=request.args.get('include_starships', 'false').lower() == 'true',
        include_all=request.args.get('include_all', 'false').lower() == 'true'
    )

    # Buscar filmes na SWAPI (usando singleton)
    client = get_swapi_client()
    films = client.get_films(search=params.search)

    # Enriquecer dados
    enriched_films = []
    for film in films:
        enriched_film = enrich_film_data(film)

        # Se include_all=true, habilitar todos os includes
        if params.include_all:
            params.include_characters = True
            params.include_planets = True
            params.include_species = True
            params.include_vehicles = True
            params.include_starships = True

        # Incluir detalhes completos dos personagens
        if params.include_characters:
            character_urls = film.get('characters', [])
            enriched_film['characters'] = fetch_characters_details(character_urls, client)

        # Incluir detalhes completos dos planetas
        if params.include_planets:
            planet_urls = film.get('planets', [])
            enriched_film['planets'] = fetch_planets_details(planet_urls, client)

        # Incluir detalhes completos das espécies
        if params.include_species:
            species_urls = film.get('species', [])
            enriched_film['species'] = fetch_species_details(species_urls, client)

        # Incluir detalhes completos dos veículos
        if params.include_vehicles:
            vehicle_urls = film.get('vehicles', [])
            enriched_film['vehicles'] = fetch_vehicles_details(vehicle_urls, client)

        # Incluir detalhes completos das naves
        if params.include_starships:
            starship_urls = film.get('starships', [])
            enriched_film['starships'] = fetch_starships_details(starship_urls, client)

        enriched_films.append(enriched_film)

    # Ordenar resultados
    sorted_films = sort_data(
        enriched_films,
        sort_by=params.sort_by,
        order=params.order
    )

    # Montar resposta
    response = {
        'success': True,
        'count': len(sorted_films),
        'data': sorted_films
    }

    return (
        json.dumps(response),
        200,
        {'Content-Type': 'application/json'}
    )
