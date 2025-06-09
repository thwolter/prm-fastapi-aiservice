from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request, status
from starlette.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.health_checks import router as core_router
from src.utils import logutils
from src.keywords.router import router as keywords_router
from src.middleware.custom_error_format import custom_error_format_middleware
from src.middleware.token_extraction import TokenExtractionMiddleware
from src.router import router as base_router

logger = logutils.get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield


if settings.IS_PRODUCTION:
    logger.info('Setting up Sentry')
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
    origins = [str(origin).strip('/') for origin in settings.BACKEND_CORS_ORIGINS]
    logger.info(f'Allowed origins: {origins}')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@app.middleware('http')
async def custom_middleware(request: Request, call_next):
    return await custom_error_format_middleware(request, call_next)


app.add_middleware(TokenExtractionMiddleware)


app.include_router(base_router)
app.include_router(keywords_router)
app.include_router(core_router)


@app.get('/api/_health', tags=['Health Check'], status_code=status.HTTP_204_NO_CONTENT)
async def root():
    return
