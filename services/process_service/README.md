# Process Service

## Visão Geral

O Process Service é responsável por baixar vídeos do S3, processá-los com FFmpeg (extrair frames ou chunks de 10s), comprimir os frames em um arquivo ZIP e enviar esse ZIP de volta para o S3. Em seguida, publica um evento `FILE_PROCESSED` via Redis.

## Execução

### Com Docker Compose
Na raiz do projeto, execute:
```bash
docker-compose up --build process_service