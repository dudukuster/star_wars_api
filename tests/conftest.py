"""
Fixtures compartilhadas para os testes

Este arquivo contém fixtures pytest reutilizáveis em todos os testes,
incluindo mocks da SWAPI e dados de exemplo.
"""

import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# Adiciona o diretório shared ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))


@pytest.fixture
def clear_lru_cache():
    """Limpa cache LRU entre testes para evitar interferência nos mocks"""
    yield
    # Após cada teste, limpa o cache dos métodos decorados com lru_cache
    try:
        from swapi_client import SWAPIClient
        # Limpa cache dos métodos que usam @lru_cache
        for attr_name in dir(SWAPIClient):
            attr = getattr(SWAPIClient, attr_name, None)
            if hasattr(attr, 'cache_clear'):
                attr.cache_clear()
    except:
        pass


@pytest.fixture
def mock_swapi_client():
    """Mock do cliente SWAPI com métodos comuns"""
    client = Mock()

    # Mock do método extract_id_from_url
    def extract_id(url):
        if not url:
            return None
        parts = url.rstrip('/').split('/')
        try:
            return int(parts[-1])
        except (ValueError, IndexError):
            return None

    client.extract_id_from_url = Mock(side_effect=extract_id)

    return client


@pytest.fixture
def sample_character():
    """Dados de exemplo de um personagem"""
    return {
        "name": "Luke Skywalker",
        "height": "172",
        "mass": "77",
        "hair_color": "blond",
        "skin_color": "fair",
        "eye_color": "blue",
        "birth_year": "19BBY",
        "gender": "male",
        "homeworld": "https://swapi.dev/api/planets/1/",
        "films": [
            "https://swapi.dev/api/films/1/",
            "https://swapi.dev/api/films/2/",
            "https://swapi.dev/api/films/3/",
            "https://swapi.dev/api/films/6/"
        ],
        "species": [],
        "vehicles": [
            "https://swapi.dev/api/vehicles/14/",
            "https://swapi.dev/api/vehicles/30/"
        ],
        "starships": [
            "https://swapi.dev/api/starships/12/",
            "https://swapi.dev/api/starships/22/"
        ],
        "created": "2014-12-09T13:50:51.644000Z",
        "edited": "2014-12-20T21:17:56.891000Z",
        "url": "https://swapi.dev/api/people/1/"
    }


@pytest.fixture
def sample_film():
    """Dados de exemplo de um filme"""
    return {
        "title": "A New Hope",
        "episode_id": 4,
        "opening_crawl": "It is a period of civil war...",
        "director": "George Lucas",
        "producer": "Gary Kurtz, Rick McCallum",
        "release_date": "1977-05-25",
        "characters": [
            "https://swapi.dev/api/people/1/",
            "https://swapi.dev/api/people/2/"
        ],
        "planets": [
            "https://swapi.dev/api/planets/1/",
            "https://swapi.dev/api/planets/2/"
        ],
        "starships": [
            "https://swapi.dev/api/starships/2/"
        ],
        "vehicles": [
            "https://swapi.dev/api/vehicles/4/"
        ],
        "species": [
            "https://swapi.dev/api/species/1/"
        ],
        "created": "2014-12-10T14:23:31.880000Z",
        "edited": "2014-12-20T19:49:45.256000Z",
        "url": "https://swapi.dev/api/films/1/"
    }


@pytest.fixture
def sample_planet():
    """Dados de exemplo de um planeta"""
    return {
        "name": "Tatooine",
        "rotation_period": "23",
        "orbital_period": "304",
        "diameter": "10465",
        "climate": "arid",
        "gravity": "1 standard",
        "terrain": "desert",
        "surface_water": "1",
        "population": "200000",
        "residents": [
            "https://swapi.dev/api/people/1/",
            "https://swapi.dev/api/people/2/"
        ],
        "films": [
            "https://swapi.dev/api/films/1/",
            "https://swapi.dev/api/films/3/"
        ],
        "created": "2014-12-09T13:50:49.641000Z",
        "edited": "2014-12-20T20:58:18.411000Z",
        "url": "https://swapi.dev/api/planets/1/"
    }


@pytest.fixture
def sample_starship():
    """Dados de exemplo de uma nave"""
    return {
        "name": "Millennium Falcon",
        "model": "YT-1300 light freighter",
        "manufacturer": "Corellian Engineering Corporation",
        "cost_in_credits": "100000",
        "length": "34.37",
        "max_atmosphering_speed": "1050",
        "crew": "4",
        "passengers": "6",
        "cargo_capacity": "100000",
        "consumables": "2 months",
        "hyperdrive_rating": "0.5",
        "MGLT": "75",
        "starship_class": "Light freighter",
        "pilots": [
            "https://swapi.dev/api/people/13/",
            "https://swapi.dev/api/people/14/"
        ],
        "films": [
            "https://swapi.dev/api/films/1/",
            "https://swapi.dev/api/films/2/"
        ],
        "created": "2014-12-10T16:59:45.094000Z",
        "edited": "2014-12-20T21:23:49.880000Z",
        "url": "https://swapi.dev/api/starships/10/"
    }


@pytest.fixture
def sample_species():
    """Dados de exemplo de uma espécie"""
    return {
        "name": "Human",
        "classification": "mammal",
        "designation": "sentient",
        "average_height": "180",
        "average_lifespan": "120",
        "eye_colors": "brown, blue, green, hazel, grey, amber",
        "hair_colors": "blonde, brown, black, red",
        "skin_colors": "caucasian, black, asian, hispanic",
        "language": "Galactic Basic",
        "homeworld": "https://swapi.dev/api/planets/9/",
        "people": [
            "https://swapi.dev/api/people/1/"
        ],
        "films": [
            "https://swapi.dev/api/films/1/"
        ],
        "created": "2014-12-10T13:52:11.567000Z",
        "edited": "2014-12-20T21:36:42.136000Z",
        "url": "https://swapi.dev/api/species/1/"
    }


@pytest.fixture
def sample_vehicle():
    """Dados de exemplo de um veículo"""
    return {
        "name": "Sand Crawler",
        "model": "Digger Crawler",
        "manufacturer": "Corellia Mining Corporation",
        "cost_in_credits": "150000",
        "length": "36.8",
        "max_atmosphering_speed": "30",
        "crew": "46",
        "passengers": "30",
        "cargo_capacity": "50000",
        "consumables": "2 months",
        "vehicle_class": "wheeled",
        "pilots": [],
        "films": [
            "https://swapi.dev/api/films/1/"
        ],
        "created": "2014-12-10T15:36:25.724000Z",
        "edited": "2014-12-20T21:30:21.661000Z",
        "url": "https://swapi.dev/api/vehicles/4/"
    }
