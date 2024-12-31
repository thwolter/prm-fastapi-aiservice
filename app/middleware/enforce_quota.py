
import json
from fastapi import Request, HTTPException, BackgroundTasks
from starlette.responses import JSONResponse, StreamingResponse, Response
from starlette.concurrency import iterate_in_threadpool
from app.auth.auth import get_jwt_payload
from app.auth.quota_service import check_token_quota, consume_tokens


async def enforce_quota(request: Request, call_next):
    """
    Middleware to enforce token quotas.
    """
    # Bypass public routes
    if is_public_route(request.url.path):
        return await call_next(request)

    try:
        token, user_id = extract_token_and_user_id(request)
        await validate_token_quota(token)
    except HTTPException as e:
        # Return early with the appropriate error response
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    # Process the request and capture the response
    response = await call_next(request)

    # Post-process the response in the background
    response_body = await regenerate_response_body(response)
    await send_token_info(response_body, token)

    return response


# ---------------- Helper Functions ---------------- #


async def regenerate_response_body(response):
    response_body = [chunk async for chunk in response.body_iterator]
    response.body_iterator = iterate_in_threadpool(iter(response_body))
    body = response_body[0].decode()
    return body


def is_public_route(path: str) -> bool:
    """
    Check if the request path is for a public route that doesn't require quota checks.
    """
    public_routes = ["/docs", "/openapi.json", "/auth/login", "/auth/logout"]
    return path in public_routes


def extract_token_and_user_id(request: Request) -> tuple:
    """
    Extract the token from cookies and user ID from the JWT payload.
    """
    try:
        # Extract JWT payload
        payload = get_jwt_payload(request)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Extract auth cookie
        token = request.cookies.get("auth")
        if not token:
            raise HTTPException(status_code=401, detail="Authentication token is missing")

        return token, user_id

    except HTTPException as e:
        raise e


async def validate_token_quota(token: str):
    """
    Validate the token's quota by communicating with the data service.
    """
    try:
        quota = await check_token_quota(token=token)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to validate token quota")
    if quota >= 1:
        raise HTTPException(status_code=429, detail="Token quota exceeded")



async def send_token_info(response_body, token: str):
    """
    Handle post-processing for JSON-based responses.
    """

    try:
        response_data = json.loads(response_body.encode("utf-8"))
        # Extract the tokens information
        tokens_info = response_data.get("tokens", {})
        total_tokens = tokens_info.get("token", 0)  # Default to 0 if not present

        if total_tokens > 0:
            # Consume the extracted token count
            await consume_tokens(token=token, tokens_info=tokens_info)

    except (json.JSONDecodeError, AttributeError):
        print("Unable to decode JSON response during post-processing.")
