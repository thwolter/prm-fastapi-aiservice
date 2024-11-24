from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.health_checks import router as core_router
from app.keywords.router import router as keywords_router
from app.project.router import router as project_router
from app.category.router import router as category_router
from app.risk.router import router as risk_router

app = FastAPI()


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip('/') for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

app.include_router(keywords_router)
app.include_router(core_router)
app.include_router(project_router)
app.include_router(category_router)
app.include_router(risk_router)


@app.get('/')
async def root():
    return {'message': 'Hello World'}
