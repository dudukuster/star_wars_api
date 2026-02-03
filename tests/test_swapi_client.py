"""
Testes para o cliente SWAPI

Testa client HTTP, cache LRU, retry automático e métodos do SWAPIClient.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from swapi_client import SWAPIClient, get_swapi_client


class TestSWAPIClient:
    """Testes para classe SWAPIClient"""

    def test_singleton_pattern(self):
        """Testa que get_swapi_client retorna sempre a mesma instância"""
        client1 = get_swapi_client()
        client2 = get_swapi_client()
        assert client1 is client2

    def test_extract_id_from_url(self):
        """Testa extração de ID de URL"""
        client = SWAPIClient()

        assert client.extract_id_from_url("https://swapi.dev/api/people/1/") == 1
        assert client.extract_id_from_url("https://swapi.dev/api/films/5/") == 5
        assert client.extract_id_from_url("https://swapi.dev/api/planets/14") == 14

    def test_extract_id_from_invalid_url(self):
        """Testa extração de ID com URL inválida"""
        client = SWAPIClient()

        assert client.extract_id_from_url("") is None
        assert client.extract_id_from_url(None) is None
        assert client.extract_id_from_url("invalid") is None

    @patch('swapi_client.requests.get')
    def test_make_request_success(self, mock_get):
        """Testa requisição bem-sucedida"""
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Luke Skywalker'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client._make_request('people/1/')

        assert result == {'name': 'Luke Skywalker'}
        mock_get.assert_called_once()
        assert 'people/1/' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_make_request_with_retry(self, mock_get):
        """Testa retry automático em caso de falha"""
        # Primeira tentativa falha, segunda sucede
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = requests.exceptions.HTTPError()

        mock_response_success = Mock()
        mock_response_success.json.return_value = {'name': 'Luke'}
        mock_response_success.raise_for_status = Mock()

        mock_get.side_effect = [mock_response_fail, mock_response_success]

        client = SWAPIClient()
        result = client._make_request('people/1/')

        assert result == {'name': 'Luke'}
        assert mock_get.call_count == 2

    @patch('swapi_client.requests.get')
    def test_make_request_max_retries_exceeded(self, mock_get):
        """Testa que após 3 tentativas falha definitivamente"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        client = SWAPIClient()

        with pytest.raises(requests.exceptions.HTTPError):
            client._make_request('people/1/')

        assert mock_get.call_count == 3  # Máximo de tentativas

    @patch('swapi_client.requests.get')
    def test_get_films(self, mock_get):
        """Testa busca de filmes"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'count': 6,
            'results': [{'title': 'A New Hope'}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client.get_films()

        assert 'results' in result
        assert result['count'] == 6
        assert 'films/' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_get_films_with_search(self, mock_get):
        """Testa busca de filmes com parâmetro search"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'count': 1,
            'results': [{'title': 'Empire'}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client.get_films(search='empire')

        assert 'search=empire' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_get_people(self, mock_get):
        """Testa busca de personagens"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'count': 82,
            'results': [{'name': 'Luke'}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client.get_people(page=1)

        assert 'results' in result
        assert 'people/' in mock_get.call_args[0][0]
        assert 'page=1' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_get_planets(self, mock_get):
        """Testa busca de planetas"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'count': 60,
            'results': [{'name': 'Tatooine'}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client.get_planets(search='tatooine')

        assert 'planets/' in mock_get.call_args[0][0]
        assert 'search=tatooine' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_get_starships(self, mock_get):
        """Testa busca de naves"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'count': 36,
            'results': [{'name': 'Millennium Falcon'}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client.get_starships()

        assert 'starships/' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_get_film_by_id(self, mock_get):
        """Testa busca de filme por ID"""
        mock_response = Mock()
        mock_response.json.return_value = {'title': 'A New Hope'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client.get_film_by_id(1)

        assert result['title'] == 'A New Hope'
        assert 'films/1/' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_get_person_by_id(self, mock_get):
        """Testa busca de personagem por ID"""
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Luke Skywalker'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client.get_person_by_id(1)

        assert result['name'] == 'Luke Skywalker'
        assert 'people/1/' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_get_planet_by_id(self, mock_get):
        """Testa busca de planeta por ID"""
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Tatooine'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client.get_planet_by_id(1)

        assert result['name'] == 'Tatooine'
        assert 'planets/1/' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_get_starship_by_id(self, mock_get):
        """Testa busca de nave por ID"""
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'X-wing'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client.get_starship_by_id(12)

        assert result['name'] == 'X-wing'
        assert 'starships/12/' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_get_species_by_id(self, mock_get):
        """Testa busca de espécie por ID"""
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Human'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client.get_species_by_id(1)

        assert result['name'] == 'Human'
        assert 'species/1/' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_get_vehicle_by_id(self, mock_get):
        """Testa busca de veículo por ID"""
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Sand Crawler'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()
        result = client.get_vehicle_by_id(4)

        assert result['name'] == 'Sand Crawler'
        assert 'vehicles/4/' in mock_get.call_args[0][0]

    @patch('swapi_client.requests.get')
    def test_cache_works(self, mock_get):
        """Testa que o cache LRU funciona"""
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Luke'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = SWAPIClient()

        # Primeira chamada
        result1 = client.get_person_by_id(1)
        # Segunda chamada (deve usar cache)
        result2 = client.get_person_by_id(1)

        assert result1 == result2
        # Deve chamar requests.get apenas uma vez por causa do cache
        assert mock_get.call_count == 1
