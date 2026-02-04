"""
Swagger UI - Interface gráfica para documentação da API

Esse arquivo é uma Cloud Function serve o Swagger UI, uma interface web interativa
que permite visualizar e testar todos os endpoints da Star Wars API.

Funcionalidades:
- Visualização completa da documentação OpenAPI
- Botão "Try it out" para testar endpoints em tempo real
- Campo de autenticação para API Key
- Respostas em tempo real

"""

import functions_framework
from flask import Response


# URL do openapi.yaml (será servido pelo próprio gateway)
OPENAPI_SPEC_URL = "https://starwars-api-gateway-4evvcnbe.uc.gateway.dev/openapi.yaml"


def get_swagger_ui_html():
    """
    Gera HTML do Swagger UI que carrega a especificação OpenAPI

    Returns:
        str: HTML completo do Swagger UI
    """
    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Star Wars API - Documentação</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
        .swagger-ui .topbar {{
            background-color: #1a1a1a;
        }}
        .swagger-ui .info .title {{
            color: #000000;
        }}
        .topbar-wrapper {{
            display: flex;
            align-items: center;
            padding: 10px 20px;
        }}
        .topbar-wrapper .link {{
            color: #FFE81F;
            font-size: 24px;
            font-weight: bold;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>

    <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: "{OPENAPI_SPEC_URL}",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                persistAuthorization: true,
                displayRequestDuration: true,
                filter: true,
                syntaxHighlight: {{
                    activate: true,
                    theme: "monokai"
                }},
                tryItOutEnabled: true,
                requestSnippetsEnabled: true,
                requestSnippets: {{
                    generators: {{
                        curl_bash: {{
                            title: "cURL (bash)",
                            syntax: "bash"
                        }},
                        curl_powershell: {{
                            title: "cURL (PowerShell)",
                            syntax: "powershell"
                        }},
                        curl_cmd: {{
                            title: "cURL (CMD)",
                            syntax: "bash"
                        }}
                    }},
                    defaultExpanded: true,
                    languages: null
                }}
            }});

            window.ui = ui;
        }};
    </script>
</body>
</html>
    """


@functions_framework.http
def swagger_ui(request):
    """
    Cloud Function HTTP handler para Swagger UI

    Serve a interface do Swagger UI que carrega a especificação OpenAPI
    do API Gateway e permite testar os endpoints interativamente.

    Args:
        request (flask.Request): Objeto da requisição HTTP

    Returns:
        tuple: (HTML content, status_code, headers)
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

    # Servir HTML do Swagger UI
    html = get_swagger_ui_html()

    headers = {
        'Content-Type': 'text/html; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'public, max-age=300' 
    }

    return Response(html, status=200, headers=headers)
