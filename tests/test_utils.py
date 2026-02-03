"""
Testes para funções utilitárias

Testa funções de enriquecimento, filtragem, ordenação e transformação de dados.
"""

import pytest
from unittest.mock import Mock, patch
from utils import (
    enrich_character_data,
    enrich_film_data,
    enrich_planet_data,
    enrich_starship_data,
    enrich_species_data,
    enrich_vehicle_data,
    filter_by_field,
    sort_data,
    truncate_text,
    fetch_homeworld_details,
    fetch_films_details,
    fetch_characters_details,
    fetch_planets_details,
    fetch_species_details,
    fetch_vehicles_details,
    fetch_starships_details
)


class TestEnrichFunctions:
    """Testes para funções de enriquecimento"""

    def test_enrich_character_data(self, sample_character):
        """Testa enriquecimento de dados de personagem"""
        result = enrich_character_data(sample_character)

        assert result['name'] == "Luke Skywalker"
        assert result['height'] == "172"
        assert result['gender'] == "male"
        assert result['films_count'] == 4
        assert result['species_count'] == 0
        assert result['vehicles_count'] == 2
        assert result['starships_count'] == 2
        assert 'homeworld' in result
        assert 'url' in result

    def test_enrich_film_data(self, sample_film):
        """Testa enriquecimento de dados de filme"""
        result = enrich_film_data(sample_film)

        assert result['title'] == "A New Hope"
        assert result['episode_id'] == 4
        assert result['director'] == "George Lucas"
        assert result['characters_count'] == 2
        assert result['planets_count'] == 2
        assert result['starships_count'] == 1
        assert result['vehicles_count'] == 1
        assert result['species_count'] == 1
        assert 'opening_crawl' in result
        assert len(result['opening_crawl']) <= 100

    def test_enrich_planet_data(self, sample_planet):
        """Testa enriquecimento de dados de planeta"""
        result = enrich_planet_data(sample_planet)

        assert result['name'] == "Tatooine"
        assert result['climate'] == "arid"
        assert result['terrain'] == "desert"
        assert result['population'] == "200000"
        assert result['residents_count'] == 2
        assert result['films_count'] == 2
        assert 'diameter' in result
        assert 'gravity' in result

    def test_enrich_starship_data(self, sample_starship):
        """Testa enriquecimento de dados de nave"""
        result = enrich_starship_data(sample_starship)

        assert result['name'] == "Millennium Falcon"
        assert result['model'] == "YT-1300 light freighter"
        assert result['starship_class'] == "Light freighter"
        assert result['pilots_count'] == 2
        assert result['films_count'] == 2
        assert 'hyperdrive_rating' in result
        assert 'MGLT' in result

    def test_enrich_species_data(self, sample_species):
        """Testa enriquecimento de dados de espécie"""
        result = enrich_species_data(sample_species)

        assert result['name'] == "Human"
        assert result['classification'] == "mammal"
        assert result['designation'] == "sentient"
        assert result['language'] == "Galactic Basic"
        assert result['people_count'] == 1
        assert result['films_count'] == 1
        assert 'average_height' in result

    def test_enrich_vehicle_data(self, sample_vehicle):
        """Testa enriquecimento de dados de veículo"""
        result = enrich_vehicle_data(sample_vehicle)

        assert result['name'] == "Sand Crawler"
        assert result['model'] == "Digger Crawler"
        assert result['vehicle_class'] == "wheeled"
        assert result['pilots_count'] == 0
        assert result['films_count'] == 1
        assert 'manufacturer' in result
        assert 'crew' in result


class TestFilterByField:
    """Testes para função de filtragem"""

    def test_filter_by_field_exact_match(self):
        """Testa filtragem com match exato"""
        data = [
            {'name': 'Luke', 'gender': 'male'},
            {'name': 'Leia', 'gender': 'female'},
            {'name': 'Han', 'gender': 'male'}
        ]
        result = filter_by_field(data, 'gender', 'male')
        assert len(result) == 2
        assert all(item['gender'] == 'male' for item in result)

    def test_filter_by_field_partial_match(self):
        """Testa filtragem com match parcial"""
        data = [
            {'climate': 'arid, hot'},
            {'climate': 'temperate'},
            {'climate': 'arid, cold'}
        ]
        result = filter_by_field(data, 'climate', 'arid')
        assert len(result) == 2

    def test_filter_by_field_case_insensitive(self):
        """Testa filtragem case-insensitive"""
        data = [
            {'terrain': 'DESERT'},
            {'terrain': 'desert'},
            {'terrain': 'Desert'}
        ]
        result = filter_by_field(data, 'terrain', 'desert')
        assert len(result) == 3

    def test_filter_by_field_no_matches(self):
        """Testa filtragem sem resultados"""
        data = [
            {'name': 'Luke'},
            {'name': 'Leia'}
        ]
        result = filter_by_field(data, 'name', 'Vader')
        assert len(result) == 0

    def test_filter_by_field_missing_field(self):
        """Testa filtragem com campo ausente"""
        data = [
            {'name': 'Luke', 'gender': 'male'},
            {'name': 'R2-D2'}  # sem campo gender
        ]
        result = filter_by_field(data, 'gender', 'male')
        assert len(result) == 1


class TestSortData:
    """Testes para função de ordenação"""

    def test_sort_data_ascending(self):
        """Testa ordenação ascendente"""
        data = [
            {'name': 'Luke', 'height': '172'},
            {'name': 'Vader', 'height': '202'},
            {'name': 'Yoda', 'height': '66'}
        ]
        result = sort_data(data, sort_by='height', order='asc')
        assert result[0]['name'] == 'Yoda'
        assert result[-1]['name'] == 'Vader'

    def test_sort_data_descending(self):
        """Testa ordenação descendente"""
        data = [
            {'title': 'A New Hope', 'episode_id': 4},
            {'title': 'The Empire Strikes Back', 'episode_id': 5},
            {'title': 'Return of the Jedi', 'episode_id': 6}
        ]
        result = sort_data(data, sort_by='episode_id', order='desc')
        assert result[0]['episode_id'] == 6
        assert result[-1]['episode_id'] == 4

    def test_sort_data_string_field(self):
        """Testa ordenação por campo string"""
        data = [
            {'name': 'Vader'},
            {'name': 'Luke'},
            {'name': 'Yoda'}
        ]
        result = sort_data(data, sort_by='name', order='asc')
        assert result[0]['name'] == 'Luke'
        assert result[-1]['name'] == 'Yoda'

    def test_sort_data_missing_field(self):
        """Testa ordenação com campo ausente em alguns itens"""
        data = [
            {'name': 'Luke', 'height': '172'},
            {'name': 'R2-D2'},  # sem height
            {'name': 'Yoda', 'height': '66'}
        ]
        result = sort_data(data, sort_by='height', order='asc')
        assert len(result) == 3  # Não deve crashar


class TestTruncateText:
    """Testes para função de truncamento"""

    def test_truncate_text_shorter_than_max(self):
        """Testa texto menor que o máximo"""
        text = "Short text"
        result = truncate_text(text, max_length=100)
        assert result == "Short text"

    def test_truncate_text_exact_max(self):
        """Testa texto exatamente no máximo"""
        text = "x" * 100
        result = truncate_text(text, max_length=100)
        assert len(result) == 100
        assert result == text

    def test_truncate_text_longer_than_max(self):
        """Testa texto maior que o máximo"""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, max_length=20)
        assert len(result) == 23  # 20 + "..."
        assert result.endswith("...")

    def test_truncate_text_empty(self):
        """Testa texto vazio"""
        result = truncate_text("", max_length=100)
        assert result == ""


class TestFetchFunctions:
    """Testes para funções de fetch de detalhes"""

    def test_fetch_homeworld_details(self, sample_planet, mock_swapi_client):
        """Testa busca de detalhes de homeworld"""
        mock_swapi_client.get_planet_by_id = Mock(return_value=sample_planet)

        url = "https://swapi.dev/api/planets/1/"
        result = fetch_homeworld_details(url, mock_swapi_client)

        assert result is not None
        assert result['name'] == "Tatooine"
        assert 'climate' in result
        mock_swapi_client.get_planet_by_id.assert_called_once_with(1)

    def test_fetch_homeworld_details_invalid_url(self, mock_swapi_client):
        """Testa busca com URL inválida"""
        result = fetch_homeworld_details(None, mock_swapi_client)
        assert result is None

    def test_fetch_films_details(self, sample_film, mock_swapi_client):
        """Testa busca de detalhes de filmes"""
        mock_swapi_client.get_film_by_id = Mock(return_value=sample_film)

        urls = ["https://swapi.dev/api/films/1/"]
        result = fetch_films_details(urls, mock_swapi_client)

        assert len(result) == 1
        assert result[0]['title'] == "A New Hope"
        mock_swapi_client.get_film_by_id.assert_called_once_with(1)

    def test_fetch_characters_details(self, sample_character, mock_swapi_client):
        """Testa busca de detalhes de personagens"""
        mock_swapi_client.get_person_by_id = Mock(return_value=sample_character)

        urls = ["https://swapi.dev/api/people/1/"]
        result = fetch_characters_details(urls, mock_swapi_client)

        assert len(result) == 1
        assert result[0]['name'] == "Luke Skywalker"
        mock_swapi_client.get_person_by_id.assert_called_once_with(1)

    def test_fetch_characters_details_with_homeworld(
        self, sample_character, sample_planet, mock_swapi_client
    ):
        """Testa busca de personagens com homeworld enriquecido"""
        mock_swapi_client.get_person_by_id = Mock(return_value=sample_character)
        mock_swapi_client.get_planet_by_id = Mock(return_value=sample_planet)

        urls = ["https://swapi.dev/api/people/1/"]
        result = fetch_characters_details(urls, mock_swapi_client, enrich_homeworld=True)

        assert len(result) == 1
        assert result[0]['name'] == "Luke Skywalker"
        assert isinstance(result[0]['homeworld'], dict)
        assert result[0]['homeworld']['name'] == "Tatooine"

    def test_fetch_details_handles_exceptions(self, mock_swapi_client):
        """Testa que erros não quebram o fetch"""
        mock_swapi_client.get_film_by_id = Mock(side_effect=Exception("API Error"))

        urls = ["https://swapi.dev/api/films/1/", "https://swapi.dev/api/films/2/"]
        result = fetch_films_details(urls, mock_swapi_client)

        # Deve retornar lista vazia sem crashar
        assert result == []

    def test_fetch_details_empty_list(self, mock_swapi_client):
        """Testa fetch com lista vazia"""
        result = fetch_films_details([], mock_swapi_client)
        assert result == []
