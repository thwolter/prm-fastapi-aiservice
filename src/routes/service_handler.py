"""Service handler for executing service queries."""
import logging
from typing import Callable, Generic, Type, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel

from routes.validation import validate_model

TRequest = TypeVar('TRequest', bound=BaseModel)
TResponse = TypeVar('TResponse', bound=BaseModel)

logger = logging.getLogger(__name__)


class ServiceHandler(Generic[TRequest, TResponse]):
    """
    Handler for executing service queries and processing responses.
    
    This class is responsible for:
    1. Creating a service instance using the provided factory
    2. Executing the service query
    3. Validating the response
    4. Handling errors
    """
    
    def __init__(
        self,
        service_factory: Callable[[], object],
        request_model: Type[TRequest],
        response_model: Type[TResponse],
    ):
        """
        Initialize the service handler.
        
        Args:
            service_factory: A callable that returns a service instance.
            request_model: The Pydantic model for the request.
            response_model: The Pydantic model for the response.
        """
        self.service_factory = service_factory
        self.request_model = request_model
        self.response_model = response_model

    async def handle(self, request: TRequest) -> TResponse:
        """
        Handle a service request.
        
        Args:
            request: The request to handle.
            
        Returns:
            The validated response.
            
        Raises:
            HTTPException: If an error occurs during processing.
        """
        service = self.service_factory()
        try:
            # Validate the request
            query = self.request_model(**request.model_dump())
            
            # Execute the query
            result = await service.execute_query(query)
            
            # Preserve response_info if present
            response_info = getattr(result, 'response_info', None)
            
            # Validate the response
            validated = validate_model(result, self.response_model)
            
            # Restore response_info if it was present
            if response_info is not None:
                setattr(validated, 'response_info', response_info)
                
            return validated

        except AttributeError as ae:
            logger.error(f'Attribute error in {self._get_service_name()}: {ae}')
            raise HTTPException(status_code=400, detail=f'Invalid request structure: {ae}')

        except HTTPException as he:
            logger.warning(f'HTTPException in {self._get_service_name()}: {he.detail}')
            raise HTTPException(status_code=he.status_code, detail=he.detail)

        except TypeError as te:
            logger.error(f'Type error in {self._get_service_name()}: {te}')
            raise HTTPException(status_code=400, detail=f'Invalid request structure: {te}')

        except Exception as e:
            logger.error(f'Unexpected error in {self._get_service_name()}: {e}')
            raise HTTPException(status_code=500, detail='Internal Server Error')
            
    def _get_service_name(self) -> str:
        """Get the name of the service for logging purposes."""
        try:
            return self.service_factory.__name__
        except AttributeError:
            return str(self.service_factory)