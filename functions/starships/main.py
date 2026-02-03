"""
Cloud Function: Consulta de Naves Espaciais

Endpoint GET /get-starships que retorna naves da saga Star Wars
com suporte a busca, paginação e filtros.

"""

import functions_framework
import json
from flask import Request

from swapi_client import get_swapi_client
from validators import StarshipQueryParams
from decorators import add_cors_headers, log_request, handle_errors
from utils import enrich_starship_data, filter_by_field


@functions_framework.http
@add_cors_headers
@log_request
@handle_errors
def get_starships(request: Request):
    """
    Busca naves espaciais da saga Star Wars

    Query Parameters:
        search (str): Busca por nome
        page (int): Número da página (1-100)
        starship_class (str): Filtro por classe da nave
        manufacturer (str): Filtro por fabricante

    Returns:
        JSON com lista de naves

    Exemplos:
        GET /get-starships
        GET /get-starships?search=falcon
        GET /get-starships?page=2
        GET /get-starships?starship_class=starfighter
        GET /get-starships?manufacturer=kuat
    """
    # Extrair e validar parâmetros (Pydantic faz conversão e validação automaticamente)
    params = StarshipQueryParams(
        search=request.args.get('search'),
        page=request.args.get('page', '1'),  # String, Pydantic converte para int
        starship_class=request.args.get('starship_class'),
        manufacturer=request.args.get('manufacturer')
    )

    # Buscar naves na SWAPI (usando singleton)
    client = get_swapi_client()
    data = client.get_starships(search=params.search, page=params.page)

    starships = data.get('results', [])

    # Aplicar filtros se especificados
    if params.starship_class:
        starships = filter_by_field(starships, 'starship_class', params.starship_class)

    if params.manufacturer:
        starships = filter_by_field(starships, 'manufacturer', params.manufacturer)

    # Enriquecer dados
    enriched_starships = [enrich_starship_data(ship) for ship in starships]

    # Montar resposta
    response = {
        'success': True,
        'count': len(enriched_starships),
        'total': data.get('count', 0),
        'next': data.get('next'),
        'previous': data.get('previous'),
        'data': enriched_starships
    }

    return (
        json.dumps(response),
        200,
        {'Content-Type': 'application/json'}
    )
