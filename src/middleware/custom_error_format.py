from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def custom_error_format_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except RequestValidationError as exc:
        errors = exc.errors()
        return JSONResponse(
            status_code=422,
            content={'detail': 'Validation failed', 'errors': errors},
        )
