from fastapi import HTTPException, Request

from app.auth.quota_service import check_token_quota


async def get_current_user(request: Request):
    """
    Dependency to enforce token validation and access control.
    """
    token = request.state.token
    user_id = request.state.user_id

    if not token or not user_id:
        raise HTTPException(status_code=401, detail='Authentication token is required')

    try:
        quota = await check_token_quota(token)
        if quota >= 1:
            raise HTTPException(status_code=429, detail='Token quota exceeded')
    except Exception:
        raise HTTPException(status_code=502, detail='Failed to validate token quota')

    return {'token': token, 'user_id': user_id}
