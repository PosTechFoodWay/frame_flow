# Download Service

## Visão Geral

O Download Service permite ao usuário baixar (streaming) o arquivo ZIP processado, que contém os frames extraídos do vídeo. Ele valida o token JWT via Auth Service e utiliza AWS S3 para buscar o arquivo.

## Endpoints
- **GET /download/{event_id}**: Realiza o download do arquivo ZIP correspondente ao evento.

## Execução

### Com Docker Compose
Na raiz do projeto, execute:
```bash
docker-compose up --build download_service
```