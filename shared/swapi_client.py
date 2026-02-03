"""
Cliente SWAPI com cache e resiliência

Este módulo implementa um cliente robusto para consumir a Star Wars API (SWAPI).
Inclui mecanismos de cache (@lru_cache), retry automático em caso de falhas,
e logging estruturado para facilitar debugging e monitoramento.

"""

import json
import logging
import re
import time
from functools import lru_cache
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests


# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SWAPIException(Exception):
    """Exceção customizada para erros relacionados à SWAPI"""
    pass


# Instância global do cliente (singleton)
_swapi_client_instance = None


def get_swapi_client() -> 'SWAPIClient':
    """
    Retorna instância singleton do SWAPIClient

    Cria a instância na primeira chamada e reutiliza nas seguintes.
    Isso mantém o pool de conexões HTTP ativo e melhora performance.

    Returns:
        Instância única do SWAPIClient

    Example:
        >>> client = get_swapi_client()
        >>> films = client.get_films()
    """
    global _swapi_client_instance
    if _swapi_client_instance is None:
        _swapi_client_instance = SWAPIClient()
    return _swapi_client_instance


class SWAPIClient:
    """
    Cliente para interagir com a Star Wars API

    Implementa:
    - Cache LRU para otimização
    - Retry automático em falhas transitórias
    - Logging estruturado
    - Tratamento de erros robusto
    """

    BASE_URL = "https://swapi.dev/api/"
    TIMEOUT = 10  
    MAX_RETRIES = 3
    RETRY_DELAY = 1  

    def __init__(self):
        """Inicializa sessão HTTP com headers customizados"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PowerOfData-StarWars-API/1.0',
            'Accept': 'application/json'
        })

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Faz requisição HTTP à SWAPI com retry logic

        Args:
            endpoint: Endpoint da API (ex: 'films/', 'people/')
            params: Parâmetros de query string

        Returns:
            Dict com resposta da API

        Raises:
            SWAPIException: Em caso de erro após todas as tentativas
        """
        url = urljoin(self.BASE_URL, endpoint)

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.info(json.dumps({
                    'event': 'swapi_request_start',
                    'url': url,
                    'params': params,
                    'attempt': attempt
                }))

                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.TIMEOUT
                )

                # Verificar status HTTP
                if response.status_code == 404:
                    logger.warning(json.dumps({
                        'event': 'swapi_not_found',
                        'url': url,
                        'status_code': 404
                    }))
                    raise SWAPIException(f"Resource not found: {url}")

                # Verificar se é erro 4xx (erro do cliente - não faz retry)
                if 400 <= response.status_code < 500:
                    logger.error(json.dumps({
                        'event': 'swapi_client_error',
                        'url': url,
                        'status_code': response.status_code
                    }))
                    raise SWAPIException(f"Client error {response.status_code}: {url}")

                # Verificar se é erro 5xx (erro do servidor - faz retry)
                if response.status_code >= 500:
                    logger.warning(json.dumps({
                        'event': 'swapi_server_error',
                        'url': url,
                        'status_code': response.status_code,
                        'attempt': attempt
                    }))

                    if attempt == self.MAX_RETRIES:
                        raise SWAPIException(
                            f"Server error {response.status_code} after {self.MAX_RETRIES} attempts"
                        )

                    time.sleep(self.RETRY_DELAY * attempt)
                    continue  # Tenta novamente

                data = response.json()

                logger.info(json.dumps({
                    'event': 'swapi_request_success',
                    'url': url,
                    'attempt': attempt
                }))

                return data

            except requests.exceptions.Timeout:
                logger.warning(json.dumps({
                    'event': 'swapi_timeout',
                    'url': url,
                    'attempt': attempt,
                    'max_retries': self.MAX_RETRIES
                }))

                if attempt == self.MAX_RETRIES:
                    raise SWAPIException(
                        f"Timeout after {self.MAX_RETRIES} attempts"
                    )

                time.sleep(self.RETRY_DELAY * attempt)

            except requests.exceptions.RequestException as e:
                logger.error(json.dumps({
                    'event': 'swapi_request_error',
                    'url': url,
                    'attempt': attempt,
                    'error': str(e)
                }))

                if attempt == self.MAX_RETRIES:
                    raise SWAPIException(
                        f"Request failed after {self.MAX_RETRIES} attempts: {e}"
                    )

                time.sleep(self.RETRY_DELAY * attempt)

            except ValueError as e:
                logger.error(json.dumps({
                    'event': 'swapi_invalid_json',
                    'url': url,
                    'error': str(e)
                }))
                raise SWAPIException(f"Invalid JSON response: {e}")

        raise SWAPIException("Unexpected error in request loop")

    @lru_cache(maxsize=128)
    def get_films(self, search: Optional[str] = None) -> List[Dict]:
        """
        Busca filmes da saga Star Wars (com cache)

        Args:
            search: Termo de busca opcional (título do filme)

        Returns:
            Lista de filmes
        """
        params = {}
        if search:
            params['search'] = search

        data = self._make_request('films/', params)
        return data.get('results', [])

    @lru_cache(maxsize=128)
    def get_film_by_id(self, film_id: int) -> Dict:
        """
        Busca filme específico por ID (com cache)

        Args:
            film_id: ID do filme (1-6)

        Returns:
            Dados do filme
        """
        return self._make_request(f'films/{film_id}/')

    def get_people(
        self,
        search: Optional[str] = None,
        page: int = 1
    ) -> Dict:
        """
        Busca personagens da saga

        Args:
            search: Termo de busca opcional (nome)
            page: Número da página (paginação)

        Returns:
            Dict com 'count', 'next', 'previous', 'results'
        """
        params = {'page': page}
        if search:
            params['search'] = search

        return self._make_request('people/', params)

    def get_person_by_id(self, person_id: int) -> Dict:
        """
        Busca personagem específico por ID

        Args:
            person_id: ID do personagem

        Returns:
            Dados do personagem
        """
        return self._make_request(f'people/{person_id}/')

    def get_planets(
        self,
        search: Optional[str] = None,
        page: int = 1
    ) -> Dict:
        """
        Busca planetas da saga

        Args:
            search: Termo de busca opcional (nome)
            page: Número da página

        Returns:
            Dict com 'count', 'next', 'previous', 'results'
        """
        params = {'page': page}
        if search:
            params['search'] = search

        return self._make_request('planets/', params)

    def get_planet_by_id(self, planet_id: int) -> Dict:
        """
        Busca planeta específico por ID

        Args:
            planet_id: ID do planeta

        Returns:
            Dados do planeta
        """
        return self._make_request(f'planets/{planet_id}/')

    def get_starships(
        self,
        search: Optional[str] = None,
        page: int = 1
    ) -> Dict:
        """
        Busca naves espaciais da saga

        Args:
            search: Termo de busca opcional (nome)
            page: Número da página

        Returns:
            Dict com 'count', 'next', 'previous', 'results'
        """
        params = {'page': page}
        if search:
            params['search'] = search

        return self._make_request('starships/', params)

    def get_starship_by_id(self, starship_id: int) -> Dict:
        """
        Busca nave específica por ID

        Args:
            starship_id: ID da nave

        Returns:
            Dados da nave
        """
        return self._make_request(f'starships/{starship_id}/')

    def get_species_by_id(self, species_id: int) -> Dict:
        """
        Busca espécie específica por ID

        Args:
            species_id: ID da espécie

        Returns:
            Dados da espécie
        """
        return self._make_request(f'species/{species_id}/')

    def get_vehicle_by_id(self, vehicle_id: int) -> Dict:
        """
        Busca veículo específico por ID

        Args:
            vehicle_id: ID do veículo

        Returns:
            Dados do veículo
        """
        return self._make_request(f'vehicles/{vehicle_id}/')

    @staticmethod
    def extract_id_from_url(url: str) -> Optional[int]:
        """
        Extrai ID numérico de uma URL da SWAPI

        Exemplo:
            'https://swapi.dev/api/films/1/' -> 1
            'https://swapi.dev/api/people/10/' -> 10

        Args:
            url: URL da SWAPI

        Returns:
            ID extraído ou None se não encontrado
        """
        match = re.search(r'/(\d+)/?$', url)
        if match:
            return int(match.group(1))
        return None
