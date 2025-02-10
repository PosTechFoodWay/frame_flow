# Upload Service

## Visão Geral

O Upload Service recebe arquivos de vídeo, valida tamanho e extensão, realiza o upload para AWS S3, grava metadados no banco e publica um evento (`FILE_UPLOADED`) no Redis.

### Endpoints
- **POST /files/upload**: Envia um vídeo.
- **GET /files/upload/status/{event_id}**: Consulta o status do upload.