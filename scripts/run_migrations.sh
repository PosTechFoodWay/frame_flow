#!/bin/bash

# Opcional: parar script em caso de erro
set -e

echo "Rodando as migrações Alembic no contêiner 'auth_service'..."
docker-compose exec auth_service poetry run alembic upgrade head

echo "Rodando as migrações Alembic no contêiner 'upload_service'..."
docker-compose exec upload_service poetry run alembic upgrade head

echo "Migrações aplicadas com sucesso!"
