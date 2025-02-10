# Dockerfile
FROM python:3.13-slim

# Instala algumas dependências do sistema (opcional)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala Poetry
RUN pip install --no-cache-dir poetry==2.0.1

# Copia config da Poetry
COPY pyproject.toml poetry.lock* /app/

# Instala dependências (sem dev-deps, se quiser)
RUN poetry install --no-interaction --no-ansi --no-root

# Copia o restante do código
COPY . /app

# Exponha a porta (por convenção, não é estritamente obrigatório)
EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "download_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
