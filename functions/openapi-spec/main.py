"""
OpenAPI Specification Server

Esse arquivo é uma Cloud Function serve o arquivo openapi.yaml da API, permitindo que
o Swagger UI e outras ferramentas carreguem a especificação completa.
    
"""

import functions_framework
from flask import Response
import os


@functions_framework.http
def openapi_spec(request):
    """
    Cloud Function HTTP handler para servir openapi.yaml

    Retorna a especificação OpenAPI completa em formato YAML para
    ser consumida pelo Swagger UI e outras ferramentas.

    Args:
        request (flask.Request): Objeto da requisição HTTP

    Returns:
        tuple: (YAML content, status_code, headers)
    """
    # Tratar requisições OPTIONS (CORS preflight)
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Ler arquivo openapi.yaml
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(current_dir, 'openapi.yaml')

        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()

        headers = {
            'Content-Type': 'application/x-yaml; charset=utf-8',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=300'  
        }

        return Response(yaml_content, status=200, headers=headers)

    except FileNotFoundError:
        error_response = "OpenAPI specification file not found"
        headers = {
            'Content-Type': 'text/plain',
            'Access-Control-Allow-Origin': '*'
        }
        return Response(error_response, status=404, headers=headers)

    except Exception as e:
        error_response = f"Error loading OpenAPI specification: {str(e)}"
        headers = {
            'Content-Type': 'text/plain',
            'Access-Control-Allow-Origin': '*'
        }
        return Response(error_response, status=500, headers=headers)
