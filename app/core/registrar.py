import logging
from typing import Callable, Generic, Type, TypeVar

from app.auth.dependencies import get_current_user
from app.auth.service import AuthService
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ValidationError

TRequest = TypeVar('TRequest', bound=BaseModel)
TResponse = TypeVar('TResponse', bound=BaseModel)

logger = logging.getLogger(__name__)


def validate_model(data, model: Type[BaseModel]) -> BaseModel:
    try:
        return model(**data.model_dump())
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f'Validation Error: {ve.errors()}')


class BaseServiceHandler(Generic[TRequest, TResponse]):
    def __init__(
        self,
        service_factory: Callable[[], object],
        request_model: Type[TRequest],
        response_model: Type[TResponse],
    ):
        self.service_factory = service_factory
        self.request_model = request_model
        self.response_model = response_model

    async def handle(self, request: TRequest) -> TResponse:
        service = self.service_factory()
        try:
            query = self.request_model(**request.model_dump())
            result = await service.execute_query(query)
            return validate_model(result, self.response_model)

        except AttributeError as ae:
            logging.error(f'Attribute error in {self.service_factory.__name__}: {ae}')
            raise HTTPException(status_code=400, detail=f'Invalid request structure: {ae}')

        except HTTPException as he:
            logging.warning(f'HTTPException in {self.service_factory.__name__}: {he.detail}')
            raise HTTPException(status_code=he.status_code, detail=he.detail)

        except TypeError as te:
            logging.error(f'Type error in {self.service_factory.__name__}: {te}')
            raise HTTPException(status_code=400, detail=f'Invalid request structure: {te}')

        except Exception as e:
            logging.error(f'Unexpected error in {self.service_factory.__name__}: {e}')
            raise HTTPException(status_code=500, detail='Internal Server Error')


class RouteRegistrar:
    def __init__(self, api_router: APIRouter):
        self.router = api_router

    def register_route(
        self,
        path: str,
        request_model: Type[TRequest],
        response_model: Type[TResponse],
        service_factory: Callable[[], object],
        tags: list[str] = None,
    ):
        handler = BaseServiceHandler(service_factory, request_model, response_model)

        async def route_function(
            request: Request,
            request_model: request_model,
            user_info: get_current_user = Depends(get_current_user),
        ) -> response_model:
            user_id = user_info['user_id']
            service = AuthService(request)
            valid = await service.check_token_quota(user_id)
            if not valid:
                raise HTTPException(status_code=402, detail='Token quota exceeded')

            result = await handler.handle(request_model)
            await service.consume_tokens(result, user_id)
            return result

        self.router.post(path, response_model=response_model, tags=tags)(route_function)


# Create APIRouter instance
router = APIRouter(
    prefix='/api',
    tags=['api'],
    responses={404: {'description': 'Not found'}},
)

# Create route registrar
registrar = RouteRegistrar(router)
