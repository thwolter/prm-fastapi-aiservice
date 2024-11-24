import logging
from typing import Type, TypeVar, Generic
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ValidationError

TRequest = TypeVar('TRequest', bound=BaseModel)
TResponse = TypeVar('TResponse', bound=BaseModel)


class BaseServiceHandler(Generic[TRequest, TResponse]):
    def __init__(self, service_class: Type, request_model: Type[TRequest], response_model: Type[TResponse]):
        self.service_class = service_class
        self.request_model = request_model
        self.response_model = response_model

    def handle(self, request: TRequest) -> TResponse:
        service = self.service_class()
        try:
            # Validate the request data
            query = self.request_model(**request.model_dump())

            # Execute the service logic
            result = service.execute_query(query)

            # Validate and return the response
            return self.response_model(**result.model_dump())

        except ValidationError as ve:
            logging.error(f"Validation error in {self.service_class.__name__}: {ve}")
            raise HTTPException(status_code=422, detail=f"Validation Error: {ve.errors()}")

        except AttributeError as ae:
            logging.error(f"Attribute error in {self.service_class.__name__}: {ae}")
            raise HTTPException(status_code=400, detail="Invalid request structure.")

        except HTTPException as he:
            logging.warning(f"HTTPException in {self.service_class.__name__}: {he.detail}")
            raise

        except Exception as e:
            logging.error(f"Unexpected error in {self.service_class.__name__}: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


class RouteRegistrar:
    def __init__(self, api_router: APIRouter):
        self.router = api_router

    def register_route(
            self,
            path: str,
            request_model: Type[TRequest],
            response_model: Type[TResponse],
            service_class: Type,
    ):
        handler = BaseServiceHandler(service_class, request_model, response_model)

        async def route_function(request: request_model, req: Request) -> response_model:
            logging.info(f"Processing request at {path} with data: {await req.json()}")
            try:
                return handler.handle(request)
            except HTTPException as he:
                logging.warning(f"HTTPException: {he.detail}")
                raise he
            except Exception as e:
                logging.error(f"Unhandled error: {e}")
                raise HTTPException(status_code=500, detail="An unexpected error occurred.")

        self.router.post(path, response_model=response_model)(route_function)


# Create APIRouter instance
router = APIRouter(
    prefix='/api',
    tags=['api'],
    responses={404: {'description': 'Not found'}},
)

# Create route registrar
registrar = RouteRegistrar(router)