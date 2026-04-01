from fastapi import FastAPI

from app.config import settings
from app.router import router

app = FastAPI(
    title="quick-sell API",
    description="Marketplace używanej elektroniki z AI Pre-filling",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "provider": settings.model_provider,
        "env": settings.app_env,
    }