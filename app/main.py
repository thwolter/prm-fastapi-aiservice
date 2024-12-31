from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.health_checks import router as core_router
from app.keywords.router import router as keywords_router
from app.middleware.custom_error_format import custom_error_format_middleware
from app.router import router as base_router


from app.auth.router import router as auth_router
from middleware.enforce_quota import enforce_quota


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(lifespan=lifespan)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip('/') for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    return await custom_error_format_middleware(request, call_next)


app.middleware("http")(enforce_quota)



app.include_router(base_router)
app.include_router(keywords_router)
app.include_router(core_router)
app.include_router(auth_router)
@app.get('/', tags=['Health Check'])
async def root():
    return {'message': 'Hello World'}


