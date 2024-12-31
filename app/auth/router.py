import httpx
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import JSONResponse

from app.auth.schemas import LoginRequest
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=['auth'])

@router.post("/login")
async def login(request: LoginRequest, response: Response):
    """
    Login endpoint to authenticate a user and set the JWT cookie.
    """
    form_data = {
        "grant_type": request.grant_type,
        "username": request.username,
        "password": request.password,
    }

    async with httpx.AsyncClient() as client:
        auth_response = await client.post(
            f"{settings.DATASERVICE_URL}/auth/jwt/login",
            data=form_data,
        )

        if auth_response.status_code != 204:
            return JSONResponse(status_code=auth_response.status_code, content={"detail": "Invalid credentials"})

        # Extract token from the response
        token = auth_response.cookies.get("auth")
        if not token:
            raise HTTPException(status_code=500, detail="Authentication failed")

        # Set the JWT token as a secure cookie
        response.set_cookie(key="auth", value=token, httponly=True, secure=True)
        return {"message": "Login successful"}


@router.post("/logout")
async def logout(response: Response):
    """
    Logout endpoint to remove the JWT cookie.
    """
    async with httpx.AsyncClient() as client:
        auth_response = await client.post(f"{settings.DATASERVICE_URL}/auth/jwt/logout")
    response.delete_cookie("auth")
    return {"message": "Logout successful"}