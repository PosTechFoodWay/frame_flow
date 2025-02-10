# Orchestrator Service

## Visão Geral

O Orchestrator Service implementa o padrão Saga para coordenar fluxos entre os serviços. Ele escuta eventos via Redis Pub/Sub (canal `saga_events`), valida e parseia os eventos usando Pydantic e despacha a ação apropriada com base no tipo do evento (usando Strategy Pattern).

## Execução

### Com Docker Compose
Na raiz do projeto, execute:
```bash
docker-compose up --build orchestrator
```