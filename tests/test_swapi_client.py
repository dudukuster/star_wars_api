"""
Testes para o cliente SWAPI

Testa client HTTP, cache LRU, retry automático e métodos do SWAPIClient.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from swapi_client import SWAPIClient, get_swapi_client, SWAPIException


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

        try:
            result = client.extract_id_from_url(None)
            assert result is None
        except (AttributeError, TypeError):

            pass
        assert client.extract_id_from_url("invalid") is None

    def test_make_request_success(self):
        """Testa requisição bem-sucedida"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'name': 'Luke Skywalker'}

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client._make_request('people/1/')

        assert result == {'name': 'Luke Skywalker'}
        client.session.get.assert_called_once()
        assert 'people/1/' in client.session.get.call_args[0][0]

    def test_make_request_with_retry(self):
        """Testa retry automático em caso de falha"""

        mock_response_fail = Mock()
        mock_response_fail.status_code = 500

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {'name': 'Luke'}

        client = SWAPIClient()
        client.session.get = Mock(side_effect=[mock_response_fail, mock_response_success])

        result = client._make_request('people/1/')

        assert result == {'name': 'Luke'}
        assert client.session.get.call_count == 2

    def test_make_request_max_retries_exceeded(self):
        """Testa que após 3 tentativas falha definitivamente"""
        from swapi_client import SWAPIException

        mock_response = Mock()
        mock_response.status_code = 500

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        with pytest.raises(SWAPIException):
            client._make_request('people/1/')

        assert client.session.get.call_count == 3 

    def test_get_films(self):
        """Testa busca de filmes"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'count': 6,
            'results': [{'title': 'A New Hope'}]
        }

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client.get_films()

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['title'] == 'A New Hope'
        assert client.session.get.called

    def test_get_films_with_search(self):
        """Testa busca de filmes com parâmetro search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'count': 1,
            'results': [{'title': 'Empire'}]
        }

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client.get_films(search='empire')

        assert client.session.get.called

        call_kwargs = client.session.get.call_args.kwargs
        assert 'params' in call_kwargs
        assert call_kwargs['params']['search'] == 'empire'

    def test_get_people(self):
        """Testa busca de personagens"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'count': 82,
            'results': [{'name': 'Luke'}]
        }

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client.get_people(page=1)

        assert 'results' in result
        assert client.session.get.called

    def test_get_planets(self):
        """Testa busca de planetas"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'count': 60,
            'results': [{'name': 'Tatooine'}]
        }

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client.get_planets(search='tatooine')

        assert client.session.get.called

    def test_get_starships(self):
        """Testa busca de naves"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'count': 36,
            'results': [{'name': 'Millennium Falcon'}]
        }

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client.get_starships()

        assert client.session.get.called

    def test_get_film_by_id(self):
        """Testa busca de filme por ID"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'title': 'A New Hope'}

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client.get_film_by_id(1)

        assert result['title'] == 'A New Hope'
        assert client.session.get.called

    def test_get_person_by_id(self):
        """Testa busca de personagem por ID"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'name': 'Luke Skywalker'}

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client.get_person_by_id(1)

        assert result['name'] == 'Luke Skywalker'
        assert client.session.get.called

    def test_get_planet_by_id(self):
        """Testa busca de planeta por ID"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'name': 'Tatooine'}

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client.get_planet_by_id(1)

        assert result['name'] == 'Tatooine'
        assert client.session.get.called

    def test_get_starship_by_id(self):
        """Testa busca de nave por ID"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'name': 'X-wing'}

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client.get_starship_by_id(12)

        assert result['name'] == 'X-wing'
        assert client.session.get.called

    def test_get_species_by_id(self):
        """Testa busca de espécie por ID"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'name': 'Human'}

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client.get_species_by_id(1)

        assert result['name'] == 'Human'
        assert client.session.get.called

    def test_get_vehicle_by_id(self):
        """Testa busca de veículo por ID"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'name': 'Sand Crawler'}

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        result = client.get_vehicle_by_id(4)

        assert result['name'] == 'Sand Crawler'
        assert client.session.get.called

    def test_cache_works(self):
        """Testa que o cache LRU funciona em get_film_by_id"""
        from swapi_client import SWAPIClient

        # Limpar cache a nível de classe antes do teste
        SWAPIClient.get_film_by_id.cache_clear()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'title': 'A New Hope'}

        client = SWAPIClient()
        client.session.get = Mock(return_value=mock_response)

        # Verificar cache info inicial
        initial_info = SWAPIClient.get_film_by_id.cache_info()
        initial_misses = initial_info.misses
        initial_hits = initial_info.hits

        # Primeira chamada (cache miss)
        result1 = client.get_film_by_id(1)

        # Segunda chamada com mesmo ID (cache hit)
        result2 = client.get_film_by_id(1)

        # Verificar que resultados são iguais
        assert result1 == result2
        assert result1['title'] == 'A New Hope'

        # Verificar cache_info - deve ter 1 miss e 1 hit
        final_info = SWAPIClient.get_film_by_id.cache_info()
        assert final_info.misses == initial_misses + 1
        assert final_info.hits == initial_hits + 1

        # session.get deve ter sido chamado apenas uma vez (na primeira chamada)
        assert client.session.get.call_count == 1
