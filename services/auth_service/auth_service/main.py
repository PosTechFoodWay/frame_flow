from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI

from .config import config as app_env_config
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carrega variáveis de ambiente
    database_url = app_env_config.database_url
    if not database_url:
        raise RuntimeError("DATABASE_URL not set in environment.")

    # Cria o pool e armazena em app.state
    print(">> Startup: Criando pool de conexões...")
    print(f">> Database URL: {database_url}")
    app.state.db_pool = await asyncpg.create_pool(database_url)
    print(">> Startup: Pool de conexões criado.")

    yield

    # Fecha o pool no shutdown
    await app.state.db_pool.close()
    print(">> Shutdown: Pool fechado.")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, title="Async Auth Service", debug=True)
    app.include_router(router, prefix="/auth", tags=["auth"])
    return app


app = create_app()
