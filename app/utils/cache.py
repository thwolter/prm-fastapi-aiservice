from typing import Optional, Tuple, Any, Dict, Union, Awaitable

from starlette.requests import Request
from starlette.responses import Response


def request_key_builder(
    __function,
    __namespace: str = "",
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> Union[Awaitable[str], str]:
    """Build a cache key based on the request details."""
    # Safely build the cache key using request attributes
    if request:
        method = request.method.lower()
        path = request.url.path
        query_params = repr(sorted(request.query_params.items()))
    else:
        # Fallback if request is None
        method = "no-method"
        path = "no-path"
        query_params = "no-query-params"

    # Construct the key
    key = ":".join([__namespace, method, path, query_params])
    return key
