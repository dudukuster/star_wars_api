"""
Testes para decoradores

Testa CORS, logging e tratamento de erros.
"""

import pytest
import json
from unittest.mock import Mock, patch
from pydantic import ValidationError
from decorators import add_cors_headers, log_request, handle_errors


class TestAddCorsHeaders:
    """Testes para decorador add_cors_headers"""

    def test_adds_cors_headers_to_response(self):
        """Testa que headers CORS são adicionados"""

        @add_cors_headers
        def mock_function(request):
            return ('{"data": "test"}', 200, {'Content-Type': 'application/json'})

        mock_request = Mock()
        response_data, status, headers = mock_function(mock_request)

        assert 'Access-Control-Allow-Origin' in headers
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert 'Access-Control-Allow-Methods' in headers
        assert 'Access-Control-Allow-Headers' in headers

    def test_preserves_existing_headers(self):
        """Testa que headers existentes são preservados"""

        @add_cors_headers
        def mock_function(request):
            return ('data', 200, {'X-Custom-Header': 'value'})

        mock_request = Mock()
        response_data, status, headers = mock_function(mock_request)

        assert 'X-Custom-Header' in headers
        assert headers['X-Custom-Header'] == 'value'
        assert 'Access-Control-Allow-Origin' in headers

    def test_handles_options_request(self):
        """Testa tratamento de requisição OPTIONS (preflight)"""

        @add_cors_headers
        def mock_function(request):
            return ('data', 200, {})

        mock_request = Mock()
        mock_request.method = 'OPTIONS'

        response_data, status, headers = mock_function(mock_request)

        assert status == 204
        assert 'Access-Control-Allow-Origin' in headers


class TestLogRequest:
    """Testes para decorador log_request"""

    @patch('decorators.logging')
    def test_logs_request_info(self, mock_logging):
        """Testa que informações da requisição são logadas"""

        @log_request
        def mock_function(request):
            return ('data', 200, {})

        mock_request = Mock()
        mock_request.path = '/test'
        mock_request.method = 'GET'
        mock_request.args = {'param': 'value'}

        mock_function(mock_request)

        # Verifica que logging.info foi chamado
        assert mock_logging.info.called

    @patch('decorators.logging')
    def test_logs_even_on_error(self, mock_logging):
        """Testa que log é feito mesmo se função falhar"""

        @log_request
        def mock_function(request):
            raise Exception("Test error")

        mock_request = Mock()
        mock_request.path = '/test'
        mock_request.method = 'GET'
        mock_request.args = {}

        with pytest.raises(Exception):
            mock_function(mock_request)

        # Logging deve ter sido chamado antes do erro
        assert mock_logging.info.called


class TestHandleErrors:
    """Testes para decorador handle_errors"""

    def test_returns_response_on_success(self):
        """Testa que resposta normal é retornada sem erros"""

        @handle_errors
        def mock_function(request):
            return ('{"success": true}', 200, {'Content-Type': 'application/json'})

        mock_request = Mock()
        response = mock_function(mock_request)

        assert response[1] == 200

    def test_handles_validation_error(self):
        """Testa tratamento de erro de validação Pydantic"""

        @handle_errors
        def mock_function(request):
            raise ValidationError.from_exception_data(
                'test',
                [{'type': 'value_error', 'loc': ('field',), 'msg': 'Invalid value'}]
            )

        mock_request = Mock()
        response_data, status, headers = mock_function(mock_request)

        assert status == 400
        response_json = json.loads(response_data)
        assert response_json['success'] is False
        assert 'Parâmetros inválidos' in response_json['error']
        assert 'details' in response_json

    def test_handles_generic_exception(self):
        """Testa tratamento de exceção genérica"""

        @handle_errors
        def mock_function(request):
            raise Exception("Something went wrong")

        mock_request = Mock()
        response_data, status, headers = mock_function(mock_request)

        assert status == 500
        response_json = json.loads(response_data)
        assert response_json['success'] is False
        assert 'error' in response_json

    @patch('decorators.logging')
    def test_logs_errors(self, mock_logging):
        """Testa que erros são logados"""

        @handle_errors
        def mock_function(request):
            raise Exception("Test error")

        mock_request = Mock()
        mock_function(mock_request)

        # Verifica que logging.error foi chamado
        assert mock_logging.error.called

    def test_returns_json_response(self):
        """Testa que resposta de erro é JSON válido"""

        @handle_errors
        def mock_function(request):
            raise ValueError("Test value error")

        mock_request = Mock()
        response_data, status, headers = mock_function(mock_request)

        # Deve ser JSON válido
        response_json = json.loads(response_data)
        assert isinstance(response_json, dict)
        assert 'success' in response_json
        assert 'error' in response_json
        assert headers['Content-Type'] == 'application/json'


class TestDecoratorCombination:
    """Testa uso combinado de decoradores"""

    def test_all_decorators_together(self):
        """Testa que todos os decoradores funcionam juntos"""

        @add_cors_headers
        @log_request
        @handle_errors
        def mock_function(request):
            return ('{"data": "test"}', 200, {'Content-Type': 'application/json'})

        mock_request = Mock()
        mock_request.path = '/test'
        mock_request.method = 'GET'
        mock_request.args = {}

        response_data, status, headers = mock_function(mock_request)

        # Verifica resposta
        assert status == 200
        # Verifica CORS headers
        assert 'Access-Control-Allow-Origin' in headers
        # Verifica que não houve erro
        assert json.loads(response_data)['data'] == 'test'

    @patch('decorators.logging')
    def test_decorators_with_error(self, mock_logging):
        """Testa decoradores com função que gera erro"""

        @add_cors_headers
        @log_request
        @handle_errors
        def mock_function(request):
            raise Exception("Test error")

        mock_request = Mock()
        mock_request.path = '/test'
        mock_request.method = 'GET'
        mock_request.args = {}

        response_data, status, headers = mock_function(mock_request)

        # Erro deve ser tratado
        assert status == 500
        # CORS headers devem estar presentes mesmo com erro
        assert 'Access-Control-Allow-Origin' in headers
        # Log deve ter sido feito
        assert mock_logging.info.called or mock_logging.error.called
