from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import sentry_sdk
from app.core.logger import logging
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.core.config import settings
from app.core.health_checks import router as core_router
from app.keywords.router import router as keywords_router
from app.middleware.consume_tokens import PersistConsumedTokensMiddleware
from app.middleware.custom_error_format import custom_error_format_middleware
from app.middleware.token_extraction import TokenExtractionMiddleware
from app.router import router as base_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield


if settings.IS_PRODUCTION:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        _experiments={
            # Set continuous_profiling_auto_start to True
            # to automatically start the profiler on when
            # possible.
            'continuous_profiling_auto_start': True,
        },
    )


app = FastAPI(lifespan=lifespan)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip('/') for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@app.middleware('http')
async def custom_middleware(request: Request, call_next):
    return await custom_error_format_middleware(request, call_next)


app.add_middleware(TokenExtractionMiddleware)
app.add_middleware(PersistConsumedTokensMiddleware)


app.include_router(base_router)
app.include_router(keywords_router)
app.include_router(core_router)
app.include_router(auth_router)


@app.get('/health-check', tags=['Health Check'])
async def root():
    return {'status': 'ok'}
