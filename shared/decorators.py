"""
Decoradores para Cloud Functions

Este módulo fornece decoradores reutilizáveis para aplicar em todas as
Cloud Functions, incluindo logging, CORS e tratamento de erros.

"""

import json
import logging
import time
from functools import wraps
from typing import Callable

from flask import Request
from pydantic import ValidationError

from swapi_client import SWAPIException


logger = logging.getLogger(__name__)


def add_cors_headers(func: Callable) -> Callable:
    """
    Adiciona headers CORS às respostas

    Permite que a API seja consumida por aplicações web de qualquer origem.
    Também trata requisições OPTIONS (CORS preflight).

    Args:
        func: Função da Cloud Function

    Returns:
        Função decorada com headers CORS
    """
    @wraps(func)
    def wrapper(request: Request):
        # Tratar requisições OPTIONS (CORS preflight)
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '3600'
            }
            return ('', 204, headers)

        # Executar função e adicionar headers CORS na resposta
        response = func(request)

        # Se resposta já é uma tupla (body, status_code, headers)
        if isinstance(response, tuple):
            if len(response) == 3:
                body, status_code, headers = response
                headers.update({
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                })
                return (body, status_code, headers)
            elif len(response) == 2:
                body, status_code = response
                headers = {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
                return (body, status_code, headers)

        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return (response, 200, headers)

    return wrapper


def log_request(func: Callable) -> Callable:
    """
    Registra detalhes da requisição e resposta

    Loga informações sobre cada requisição recebida, incluindo:
    - Método HTTP
    - Path
    - Query params
    - Duração da requisição
    - Status code da resposta

    Args:
        func: Função da Cloud Function

    Returns:
        Função decorada com logging
    """
    @wraps(func)
    def wrapper(request: Request):
        start_time = time.time()

        # Log início da requisição
        logger.info(json.dumps({
            'event': 'request_start',
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.args),
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }))

        try:
            # Executar função
            response = func(request)

            # Calcular duração
            duration = time.time() - start_time

            # Determinar status code
            status_code = 200
            if isinstance(response, tuple):
                if len(response) >= 2:
                    status_code = response[1]

            # Log sucesso
            logger.info(json.dumps({
                'event': 'request_success',
                'method': request.method,
                'path': request.path,
                'status_code': status_code,
                'duration_seconds': round(duration, 3)
            }))

            return response

        except Exception as e:
            # Calcular duração mesmo em caso de erro
            duration = time.time() - start_time

            # Log erro
            logger.error(json.dumps({
                'event': 'request_error',
                'method': request.method,
                'path': request.path,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'duration_seconds': round(duration, 3)
            }))

            # Re-lançar exceção para ser tratada pelo handle_errors
            raise

    return wrapper


def handle_errors(func: Callable) -> Callable:
    """
    Trata erros e retorna respostas JSON apropriadas

    Captura diferentes tipos de exceção e retorna respostas estruturadas:
    - ValidationError (Pydantic): 400 Bad Request
    - SWAPIException: 503 Service Unavailable
    - Exception genérica: 500 Internal Server Error

    Args:
        func: Função da Cloud Function

    Returns:
        Função decorada com tratamento de erros
    """
    @wraps(func)
    def wrapper(request: Request):
        try:
            return func(request)

        except ValidationError as e:
            # Erro de validação Pydantic - 400 Bad Request
            logger.warning(json.dumps({
                'event': 'validation_error',
                'errors': e.errors()
            }))

            error_response = {
                'success': False,
                'error': 'Parâmetros inválidos',
                'details': e.errors()
            }

            return (
                json.dumps(error_response),
                400,
                {'Content-Type': 'application/json'}
            )

        except SWAPIException as e:
            # Erro ao comunicar com SWAPI - 503 Service Unavailable
            logger.error(json.dumps({
                'event': 'swapi_error',
                'error': str(e)
            }))

            error_response = {
                'success': False,
                'error': 'Erro ao consultar SWAPI',
                'message': str(e)
            }

            return (
                json.dumps(error_response),
                503,
                {'Content-Type': 'application/json'}
            )

        except Exception as e:
            # Erro genérico - 500 Internal Server Error
            logger.exception(json.dumps({
                'event': 'internal_error',
                'error_type': type(e).__name__,
                'error': str(e)
            }))

            error_response = {
                'success': False,
                'error': 'Erro interno do servidor',
                'message': 'Ocorreu um erro ao processar sua requisição'
            }

            return (
                json.dumps(error_response),
                500,
                {'Content-Type': 'application/json'}
            )

    return wrapper
