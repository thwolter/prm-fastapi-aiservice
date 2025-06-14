import json
import logging

from fastapi import Request
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.auth.quota_service import consume_tokens

logger = logging.getLogger(__name__)


class PersistConsumedTokensMiddleware(BaseHTTPMiddleware):
    """
    Middleware to process token-related information in the response.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Call the next middleware or endpoint
        response = await call_next(request)

        # Post-process the response to handle token info
        response_body = await self._extract_response_body(response)
        await self._process_token_info(response_body, request)

        return response

    async def _extract_response_body(self, response: Response) -> str:
        """
        Extract the response body from a streaming response and reset it for reuse.
        """
        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))
        body = response_body[0].decode()
        return body

    async def _process_token_info(self, response_body: str, request: Request):
        """
        Process the token-related information from the response body.
        """
        token = request.state.token
        user_id = request.state.user_id
        if not token:
            return

        try:
            response_data = json.loads(response_body)
            tokens_info = response_data.get('tokens', {})
        except Exception:
            return

        if tokens_info != {}:
            await consume_tokens(token=token, user_id=user_id, tokens_info=tokens_info)
