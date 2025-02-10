# Auth Service

## Visão Geral

O Auth Service gerencia o cadastro, login e validação de tokens JWT dos usuários.

### Endpoints
- **POST /auth/register**: Cadastra um novo usuário.
- **POST /auth/login**: Realiza o login e retorna um token JWT.
- **GET /auth/validate-token?token=...**: Valida um token JWT.

## Execução

### Com Docker Compose
Na raiz do projeto, execute:
```bash
docker-compose up --build auth_service
```

Localmente (com Poetry)
1. Navegue até services/auth_service.

Instale as dependências:
```bash
poetry install
```
Execute:
```bash
poetry run uvicorn auth_service.main:app --reload --host 0.0.0.0 --port 8000
```

Testando
Registrar Usuário
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "suaSenha123"}'
```

Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "suaSenha123"}'
```

Validar Token
```bash
curl "http://localhost:8000/auth/validate-token?token=SEU_TOKEN_JWT"
```