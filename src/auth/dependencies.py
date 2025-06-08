from fastapi import HTTPException, Request


async def get_current_user(request: Request):
    """
    Dependency to enforce token validation and access control.
    """
    token = getattr(request.state, 'token', None)
    user_id = getattr(request.state, 'user_id', None)

    if not token or not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')

    return {'token': token, 'user_id': user_id}
